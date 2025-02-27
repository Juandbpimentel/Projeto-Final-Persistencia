from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from yaml import load, FullLoader
import os

configurations = load(open("app/configs.yml", "r"), Loader=FullLoader)
DATABASE_HOST = configurations["configs"]["database"]["host"]
DATABASE_PORT = configurations["configs"]["database"]["port"]
DATABASE_NAME = configurations["configs"]["database"]["name"]
DATABASE_USER = configurations["configs"]["database"]["username"]
DATABASE_PASSWORD = configurations["configs"]["database"]["password"]

url_by_env = os.getenv("DATABASE_URL")
DATABASE_URL = url_by_env if url_by_env is not None else f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = session_local()
    try:
        yield db
        db.commit()
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)