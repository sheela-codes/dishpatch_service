import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase


#replace DATABASE_URL - postgresql://  with postgresql+psycopg:// 
URL = os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://", 1) # 1 means only first occurence

engine = create_engine(URL, pool_pre_ping=True)

#SessionLocal- this creates a factory that creates session, creates brand new session for a new request, like 2 customers have their own session
SessionLocal = sessionmaker(bind=engine) # engine points to the database we configured above for URL 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    

# Base parent class for all models 
class Base(DeclarativeBase):
    pass