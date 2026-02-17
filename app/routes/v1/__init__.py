from .students import router as students_router
from .items import router as items_router
from .users import router as register_router
from .auth import router as auth_router
from .llm import router as llm_router

__all__ = [
    "students_router",
    "items_router",
    "register_router",
    "auth_router",
    "llm_router",
]
