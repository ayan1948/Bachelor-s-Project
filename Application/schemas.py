from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TestBase(BaseModel):
    title: str
    description: Optional[str] = None
    ch1: bool = False
    ch2: bool = False
    ch3: bool = False
    ch4: bool = False
    iteration: int

class TestCreate(TestBase):
    pass

class Test(TestBase):
    id: int
    moment: datetime
    user_id: int
    items: List[str] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    image_file: str
    tests: List[Test] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None