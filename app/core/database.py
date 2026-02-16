# from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine,async_sessionmaker

# from sqlalchemy.orm import DeclarativeBase
# #orm is object-relational mapping, it is a technique that allows you to interact with a database using object-oriented programming concepts. It provides a way to map database tables to Python classes and allows you to perform database operations using Python objects instead of writing raw SQL queries.

# from src.core.config import settings

# #create_async_engine --> async_sessionmaker --> AsyncSession

# # crate_async_engine to connect to the database
# #check_same_thread=False is used to allow multiple threads to access the database at the same time. It is necessary when using SQLite in a multi-threaded environment, as SQLite does not allow multiple threads to access the same database file simultaneously by default.
# engine=create_async_engine(settings.DATABASE_URL,echo=True)

# #async_sessionmaker to create a session for interacting with the database
# #expire_on_commit=False is used to prevent the session from expiring the objects after a commit. This means that the objects will still be available in the session after a commit, and you can continue to work with them without having to refresh them from the database.
# async_session_factory=async_sessionmaker(engine,expire_on_commit=False,class_=AsyncSession)



# class Base(DeclarativeBase):
#     pass

# src/core/database.py
# src/core/database.py
# src/core/database.py

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# Create async engine (Supabase)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,                 # True for debugging SQL
    pool_pre_ping=True,
    pool_recycle=300,
)


# Create async session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


# Base class for models
class Base(DeclarativeBase):
    pass


# FastAPI dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


############
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


# Dependency expected by security.py
async def get_chosen_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
################
class DummyFactory:
    async def get_session(self, db_type: str = "supabase"):
        async with async_session_factory() as session:
            yield session


db_factory = DummyFactory()
