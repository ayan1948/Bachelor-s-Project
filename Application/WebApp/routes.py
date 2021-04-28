import os
import secrets
import json
from zipfile import ZipFile
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, send_from_directory, abort
from flask_socketio import emit
from WebApp import app, db, bcrypt, socketio  # , mail
from WebApp.models import User, Test
from WebApp.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm, \
     ReviewTestForm
from flask_login import login_user, current_user, logout_user, login_required
from mock import ScopeManager
from scaling import scale


# from flask_mail import Message

@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        test = Test.query.filter_by(user_id=current_user.id).all()
        return render_template('home.html', title=home, test=test)
    return render_template('home.html', title='home')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # Redirecting to the home page when logged in, preventing the revisit.
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():  # Form Validation on submit
        user = User.query.filter_by(email=form.email.data).first()  # Verification of the existing user
        if user and bcrypt.check_password_hash(user.password, form.password.data):  # Verification of Password check
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Incorrect password or email!', 'danger')
    return render_template('login.html', title=login, form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # Password Hashing
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)  # User Creation
        db.session.add(user)  # Adding the user
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='register', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)  # Creating Hash
    _, f_ext = os.path.splitext(form_picture.filename)  # Retrieving the file and extension
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)  # Adding to the directory

    output_size = (125, 125)
    i = Image.open(form_picture)  # Opening the form_picture data into Pillow
    i.thumbnail(output_size)
    i.save(picture_path)  # Using Pillow to save the newly created Path
    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:  # Checking if picture is uploaded
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data  # Adding the form data to the current user
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account information has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username  # Printing the Current user's information on the form
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='account', image_file=image_file, form=form)


# def send_reset_email(user):
#     token = user.get_reset_token()
#     msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
#     {url_for('reset_token', token=token, _external=True)}
#
#     If you did not make this request then simply ignore this email
#     '''
#     mail.send(msg)


# @app.route("/reset_password", methods=['GET', 'POST'])
# def reset_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     form = RequestResetForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         send_reset_email(user)
#         flash('An email has been sent with instructions to rest your password', 'info')
#         return redirect(url_for('login'))
#     return render_template('rest_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user in None:
        flash('that is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # Password Hashing
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


def connect():
    global device
    try:
        device = ScopeManager()
    except:
        device = False


@socketio.on('connection')
def response(initial):
    print(initial['data'])


@socketio.on('form')
def capture(form):
    form = json.loads(form)
    # print(form)
    if form["start"]:
        try:
            device.set_title(form["title"])
            device.set_channel([form["ch1"], form["ch2"], form["ch3"], form["ch4"]])
            device.initialize()
            for i in range(form["iterations"]):
                device.acquire()
                emit('result', i + 1)
                device.reinitialize()
            data = Test(title=form["title"], description=form["description"], iteration=form["iterations"],
                        ch1=form["ch1"], ch2=form["ch2"], ch3=form["ch3"], ch4=form["ch4"],
                        author=current_user)
            db.session.add(data)
            db.session.commit()
            device.close()
            scale(form["title"])
            emit('redirect', {'destination': '/review'})
        except:
            emit('status', {'status': 'danger'})
    elif form["stop"]:
        emit('status', {'status': 'warning'})
    elif form["connect"]:
        connect()
        if device:
            emit('redirect', {'destination': '/start'})
        else:
            emit('status', {'status': 'danger'})


@app.route("/start", methods=['GET', 'POST'])
@login_required
def start():
    connect()
    return render_template('start.html', title='start', device=device)


@app.route('/review/<test>/<case>', methods=['GET', 'POST'])
def plots(test, case):
    try:
        file = f"../results/computed_{test}/{case}.json"
        if os.path.exists(file):
            with open(file) as f:
                data = json.load(f)
        return data
    except:
        return None


@app.route("/get_plot/<path:item>", methods=['GET', 'POST'])
def get_plot(item):
    directory = os.getcwd().replace("Application", "results")
    files = os.listdir(f"../results/{item}")

    if os.path.isfile(f"../results/{item}.zip"):
        return send_from_directory(directory, f"{item}.zip", mimetype='application/zip')
    else:
        try:
            with ZipFile(f"../results/{item}.zip", 'w') as Gzip:
                for file in files:
                    Gzip.write(f"../results/{item}/{file}", arcname=f"{file}")
            return send_from_directory(directory, f"{item}.zip", mimetype='application/zip')
        except:
            return abort(404)


@app.route("/review", methods=['GET', 'POST'])
@login_required
def review_test():
    form = ReviewTestForm()
    user_tests = Test.query.filter_by(user_id=current_user.id).all()
    form.tests.choices = [(t.id, t.title) for t in user_tests]
    form.tests.choices.insert(0, (0, "Select a test"))
    dic = {0: {
        "title": None,
        "description": None,
        "iteration": None,
        "time": None,
        "items": None,
        "channels": None
    }}
    for test in user_tests:
        dic[test.id] = {
            "title": test.title,
            "description": test.description,
            "iteration": test.iteration,
            "time": test.moment,
            "items": os.listdir(f"../results/{test.title}") if os.path.isdir(f"../results/{test.title}") else [],
            "channels": [test.ch1, test.ch2, test.ch3, test.ch4]
        }
    if form.submit.data and form.validate():
        selectValue = Test.query.get_or_404(int(form.tests.data))
        os.rename(f"../results/{selectValue.title}", f"../results/{form.title.data}")
        selectValue.title = form.title.data
        selectValue.description = form.description.data
        db.session.commit()
        flash('Your Test description has been updated!', 'success')
        return redirect(url_for('review_test'))
    elif form.delete.data:
        test = Test.query.get_or_404(int(form.tests.data))
        try:
            directory = os.getcwd().replace("Application", "results")
            os.rmdir(os.path.join(directory, f"{form.title.data}"))
            os.rmdir(os.path.join(directory, f"/computer_{form.title.data}"))
        finally:
            db.session.delete(test)
            db.session.commit()
            flash('Your Test has successfully been deleted!', 'warning')
            return redirect(url_for('review_test'))
    return render_template('review_test.html', title='review_test', form=form, test=dic)


@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500
