import uuid

from dataclasses import dataclass
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import UserDefinedType
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Double, func
from app.database import Base


def create_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, default=create_uuid)
    email = Column(String, unique=True)
    hashed_password = Column(String)


class Token(Base):
    __tablename__ = 'tokens'
    id = Column(String, nullable=False, primary_key=True)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', uselist=False)


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String, nullable=False, unique=True)


class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String, nullable=False)
    filename = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=True)
    description = Column(String, nullable=True)
    rating = Column(Integer, nullable=False)
    category = relationship(Category, uselist=False)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)


