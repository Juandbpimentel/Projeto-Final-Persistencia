from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from yaml import load, FullLoader
import os

configurations = load(open("app/configs.yml", "r"), Loader=FullLoader)
DATABASE_HOST = configurations["configs"]["database"]["host"]
DATABASE_PORT = configurations["configs"]["database"]["port"]
DATABASE_NAME = configurations["configs"]["database"]["name"]
DATABASE_USER = configurations["configs"]["database"]["username"]
DATABASE_PASSWORD = configurations["configs"]["database"]["password"]

url_by_env = os.getenv("DATABASE_URL")
DATABASE_URL = url_by_env if url_by_env is not None else f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

async def get_db():
    async with async_session_local() as session:
        try:
            yield session
            await session.commit()
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)