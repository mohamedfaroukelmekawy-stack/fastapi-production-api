# src/crud/__init__.py
from .basestudent import StudentRepository
from .baseitem import ItemRepository
from .baseregister import UserRepository

__all__ = ["StudentRepository", "ItemRepository", "UserRepository"]
