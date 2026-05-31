from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated, List, Optional
import uvicorn
from datetime import timedelta
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import json
from zipfile import ZipFile
import shutil
from fastapi_socketio import SocketManager

import crud, models, schemas, database, security
# mock and scaling should be available in the Application folder
try:
    from mock import ScopeManager
    from scaling import scale
except ImportError:
    pass

models.Base.metadata.create_all(bind=database.engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = SocketManager(app=app, mount_location='/socket.io')

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except security.JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Annotated[models.User, Depends(get_current_user)]):
    return current_user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: Annotated[models.User, Depends(get_current_active_user)]):
    return current_user

@app.put("/users/me/")
async def update_user_me(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    picture: Optional[UploadFile] = File(None)
):
    if username:
        current_user.username = username
    if email:
        current_user.email = email
    
    if picture:
        import secrets
        from PIL import Image
        random_hex = secrets.token_hex(8)
        f_ext = Path(picture.filename).suffix
        picture_fn = f"{random_hex}{f_ext}"
        picture_path = Path('static') / 'profile_pics' / picture_fn
        picture_path.parent.mkdir(parents=True, exist_ok=True)
        
        output_size = (125, 125)
        i = Image.open(picture.file)
        i.thumbnail(output_size)
        i.save(picture_path)
        current_user.image_file = picture_fn

    db.commit()
    return {"message": "Account information updated successfully"}

@app.get("/tests/", response_model=List[schemas.Test])
def read_user_tests(current_user: Annotated[models.User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    tests = db.query(models.Test).filter(models.Test.user_id == current_user.id).all()
    for t in tests:
        directory = Path.cwd().parent / 'results' / t.title
        t.items = [f.name for f in directory.iterdir()] if directory.is_dir() else []
    return tests

@app.put("/tests/{test_id}", response_model=schemas.Test)
def update_test(
    test_id: int, 
    test_update: schemas.TestCreate,
    current_user: Annotated[models.User, Depends(get_current_active_user)], 
    db: Session = Depends(get_db)
):
    db_test = db.query(models.Test).filter(models.Test.id == test_id, models.Test.user_id == current_user.id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    try:
        old_title = db_test.title
        new_title = test_update.title
        results_dir = Path.cwd().parent / 'results'
        if (results_dir / old_title).exists():
            (results_dir / old_title).rename(results_dir / new_title)
        if (results_dir / f"computed_{old_title}").exists():
            (results_dir / f"computed_{old_title}").rename(results_dir / f"computed_{new_title}")
    except Exception as e:
        print(e)
    
    for var, value in vars(test_update).items():
        setattr(db_test, var, value) if value is not None else None
    
    db.commit()
    db.refresh(db_test)
    
    directory = Path.cwd().parent / 'results' / db_test.title
    db_test.items = [f.name for f in directory.iterdir()] if directory.is_dir() else []
    return db_test

@app.delete("/tests/{test_id}")
def delete_test(
    test_id: int, 
    current_user: Annotated[models.User, Depends(get_current_active_user)], 
    db: Session = Depends(get_db)
):
    db_test = db.query(models.Test).filter(models.Test.id == test_id, models.Test.user_id == current_user.id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    try:
        directory = Path.cwd().parent / 'results'
        test_dir = directory / f"{db_test.title}"
        comp_dir = directory / f"computed_{db_test.title}"
        if test_dir.exists():
            shutil.rmtree(test_dir)
        if comp_dir.exists():
            shutil.rmtree(comp_dir)
    except Exception as e:
        print(e)

    db.delete(db_test)
    db.commit()
    return {"message": "Test deleted"}

@app.get('/review/{test}/{case}')
def get_plots(test: str, case: str):
    file_path = Path("..") / "results" / f"computed_{test}" / f"{case}.json"
    if file_path.exists():
        with file_path.open() as f:
            data = json.load(f)
        return data
    else:
        raise HTTPException(status_code=404, detail="Plot not found")

@app.get("/get_plot/{item:path}")
def get_plot_zip(item: str):
    directory = Path.cwd().parent / 'results'
    zip_path = directory / f"{item}.zip"
    item_dir = directory / item
    
    if zip_path.is_file():
        return FileResponse(zip_path, media_type='application/zip', filename=f"{item}.zip")
    elif item_dir.is_dir():
        files = [f.name for f in item_dir.iterdir()]
        try:
            with ZipFile(zip_path, 'w') as zipf:
                for file in files:
                    zipf.write(item_dir / file, arcname=file)
            return FileResponse(zip_path, media_type='application/zip', filename=f"{item}.zip")
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Error creating zip")
    else:
         raise HTTPException(status_code=404, detail="Item not found")

device = None
def connect():
    global device
    try:
        device = ScopeManager()
    except:
        device = False

@app.sio.on('connection')
async def handle_connection(sid, environ):
    print(f"Connected {sid}")

@app.sio.on('form')
async def handle_form(sid, data):
    global device
    form = json.loads(data) if isinstance(data, str) else data
    if form.get("start"):
        try:
            device.set_title(form["title"])
            device.set_channel([form["ch1"], form["ch2"], form["ch3"], form["ch4"]])
            device.initialize()
            for i in range(form["iterations"]):
                device.acquire()
                await app.sio.emit('result', i + 1, to=sid)
                device.reinitialize()
            # Decode token from the form to identify the user and save the test results
            user_id = None
            token_str = form.get("token")
            db = database.SessionLocal()
            if token_str:
                try:
                    payload = security.jwt.decode(token_str, security.SECRET_KEY, algorithms=[security.ALGORITHM])
                    username: str = payload.get("sub")
                    if username:
                        user = db.query(models.User).filter(models.User.username == username).first()
                        if user:
                            user_id = user.id
                except Exception as ex:
                    print("Error decoding token in WebSocket handler:", ex)
            
            if user_id:
                db_test = models.Test(
                    title=form["title"],
                    description=form.get("description"),
                    ch1=form["ch1"],
                    ch2=form["ch2"],
                    ch3=form["ch3"],
                    ch4=form["ch4"],
                    iteration=form["iterations"],
                    user_id=user_id
                )
                db.add(db_test)
                db.commit()
            
            db.close()
            device.close()
            scale(form["title"])
            await app.sio.emit('redirect', {'destination': '/review'}, to=sid)
        except Exception as e:
            print(e)
            await app.sio.emit('status', {'status': 'danger'}, to=sid)
    elif form.get("stop"):
        await app.sio.emit('status', {'status': 'warning'}, to=sid)
    elif form.get("connect"):
        connect()
        if device:
             await app.sio.emit('redirect', {'destination': '/start'}, to=sid)
        else:
             await app.sio.emit('status', {'status': 'danger'}, to=sid)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)