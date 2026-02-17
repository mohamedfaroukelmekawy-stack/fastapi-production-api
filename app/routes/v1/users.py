# from fastapi import APIRouter, HTTPException, status, Depends
# from src.core.database import async_session_factory
# from src.schemas.register import UserCreate, UserOut
# from src.crud.baseregister import UserRepository   


# router = APIRouter(prefix="/register", tags=["register"])

# @router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
# async def register_user(user: UserCreate):
#     """
#     Register a new user
#     """
#     async with async_session_factory() as session:
#         repo = UserRepository(session)
#         created = await repo.create(user)
#         return created
# ------------------------------------------------------------------
# 

# src/routers/register.py  (or wherever your router is)
# src/routers/register.py# src/api/register.py
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_factory
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserOut

router = APIRouter(prefix="/register", tags=["register"])


async def get_chosen_db(
    db: str = Query(
        default="local",
        description="Target database: 'local' (PostgreSQL) or 'supabase'"
    )
) -> AsyncSession:
    choice = db.lower().strip()
    if choice not in ("local", "supabase"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid database choice. Allowed values: 'local' or 'supabase'"
        )
    
    async for session in db_factory.get_session(choice):
        yield session


@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user in the selected database. Use ?db=supabase to store in Supabase."
)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_chosen_db)
):
    """
    Register a new user

    Query parameter:
    - db: "local" (default) or "supabase"
    """
    repo = UserRepository(db)

    try:
        created = await repo.create(user)
        await db.commit()
        await db.refresh(created)
        return created

    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(exc)}"
        ) from exc