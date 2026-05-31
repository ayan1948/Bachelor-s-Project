from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    image_file = Column(String(20), nullable=False, default='default.jpg')
    password = Column(String(60), nullable=False)

    tests = relationship("Test", back_populates="author")

class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    ch1 = Column(Boolean, default=False)
    ch2 = Column(Boolean, default=False)
    ch3 = Column(Boolean, default=False)
    ch4 = Column(Boolean, default=False)
    iteration = Column(Integer, nullable=False)
    moment = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    author = relationship("User", back_populates="tests")