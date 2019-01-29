# Database configuration settings the core of this project

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql:///catalogdb')
DBSession = sessionmaker(bind=engine)
Base = declarative_base()
session = DBSession()
