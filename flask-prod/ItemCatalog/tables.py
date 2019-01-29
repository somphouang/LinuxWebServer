# Relational DB Tables and it's mapping

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from core import Base

# create table and the relationship id reference


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    picture = Column(String)
    email = Column(String, nullable=False)


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    owner = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))

    def __init__(self, name, description, owner='Root'):
        self.name = name
        self.description = description
        self.owner = owner

    @property
    def serialize(self):
        # Return object data in easy to read serializeable format
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'owner': self.owner
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner = Column(String)
    items = relationship('Item', cascade="all, delete")

    def __init__(self, name, owner='Root'):
        self.name = name
        self.owner = owner

    @property
    def serialize(self):
        # Return object data in easy to read serializeable format
        return {
            'id': self.id,
            'name': self.name
        }
