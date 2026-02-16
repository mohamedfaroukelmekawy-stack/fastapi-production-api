# from fastapi import APIRouter, HTTPException, status, Depends

# from src.core.database import async_session_factory
# from src.schemas.student import StudentCreate, StudentUpdate, StudentOut
# from src.crud import StudentRepository   # ← we use this now
# from src.core.security import get_current_user

# router = APIRouter(prefix="/students", tags=["students"])


# # 1. CREATE (POST)
# @router.post("/", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
# async def create_student(student: StudentCreate, current_user = Depends(get_current_user)):
#     """
#     Create a new student
#     """
#     async with async_session_factory() as session:
#         repo = StudentRepository(session)
#         created = await repo.create(student)
#         return created


# # 2. READ ONE (GET by id)
# @router.get("/{student_id}", response_model=StudentOut)
# async def get_student(student_id: int, current_user = Depends(get_current_user)):
#     """
#     Get one student by ID
#     """
#     async with async_session_factory() as session:
#         repo = StudentRepository(session)
#         student = await repo.get_by_id(student_id)
#         if student is None:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
#         return student


# # 3. READ ALL (GET list)
# @router.get("/", response_model=list[StudentOut])
# async def get_all_students(skip: int = 0, limit: int = 50, current_user = Depends(get_current_user)):
#     """
#     Get list of students with pagination
#     """
#     async with async_session_factory() as session:
#         repo = StudentRepository(session)
#         students = await repo.get_all(skip=skip, limit=limit)
#         return students


# # 4. UPDATE (PUT - partial update)
# @router.put("/{student_id}", response_model=StudentOut)
# async def update_student(student_id: int, student_data: StudentUpdate, current_user = Depends(get_current_user)):
#     """
#     Update existing student (partial update - only sent fields are updated)
#     """
#     async with async_session_factory() as session:
#         repo = StudentRepository(session)

#         # Optional: check if at least one field is provided
#         if not student_data.model_dump(exclude_unset=True):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="At least one field must be provided for update"
#             )

#         updated = await repo.update(student_id, student_data)
#         if updated is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Student not found"
#             )
#         return updated


# # 5. DELETE
# @router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_student(student_id: int, current_user = Depends(get_current_user)):
#     """
#     Delete a student by ID
#     """
#     async with async_session_factory() as session:
#         repo = StudentRepository(session)
#         deleted = await repo.delete(student_id)
#         if deleted is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Student not found"
#             )
#     # No need to return anything → FastAPI will send 204 No Content

# --------------------------------------------------------------------------
# src/api/students.py   (or src/routers/students.py)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession   # ← ADD THIS LINE
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.student import StudentCreate, StudentUpdate, StudentOut
from app.crud import StudentRepository
from app.core.security import get_current_user
from app.core.database import db_factory
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context
from app.core.database import get_chosen_db
from app.crud.baseregister import UserRepository
from app.schemas.token import TokenData
from sqlalchemy.ext.asyncio import AsyncSession   # ← ADD THIS LINE

router = APIRouter(prefix="/students", tags=["students"])


# ────────────────────────────────────────────────
# Reusable dependency - choose database via ?db=
# ────────────────────────────────────────────────
async def get_chosen_db(
    db: str = Query(
        default="local",
        description="Target database: 'local' (PostgreSQL) or 'supabase'"
    )
) -> AsyncSession:
    """
    Dependency that returns AsyncSession for the chosen database.
    """
    choice = db.lower().strip()
    if choice not in ("local", "supabase"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid database choice. Allowed values: 'local' or 'supabase'"
        )

    async for session in db_factory.get_session(choice):
        yield session


# ────────────────────────────────────────────────
# Endpoints - now support ?db=supabase
# ────────────────────────────────────────────────

@router.post(
    "/",
    response_model=StudentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Creates a new student in the selected database. Use ?db=supabase to store in Supabase."
)
async def create_student(
    student: StudentCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db)
):
    repo = StudentRepository(db)

    try:
        created = await repo.create(student)
        await db.commit()
        await db.refresh(created)
        return created
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create student: {str(exc)}"
        ) from exc


@router.get(
    "/{student_id}",
    response_model=StudentOut,
    summary="Get one student by ID"
)
async def get_student(
    student_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db)
):
    repo = StudentRepository(db)
    student = await repo.get_by_id(student_id)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return student


@router.get(
    "/",
    response_model=List[StudentOut],
    summary="Get list of students with pagination"
)
async def get_all_students(
    skip: int = 0,
    limit: int = 50,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db)
):
    repo = StudentRepository(db)
    students = await repo.get_all(skip=skip, limit=limit)
    return students


@router.put(
    "/{student_id}",
    response_model=StudentOut,
    summary="Update existing student (partial update)"
)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db)
):
    if not student_data.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided for update"
        )

    repo = StudentRepository(db)
    updated = await repo.update(student_id, student_data)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    await db.commit()
    await db.refresh(updated)
    return updated


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student by ID"
)
async def delete_student(
    student_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db)
):
    repo = StudentRepository(db)
    deleted = await repo.delete(student_id)

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    await db.commit()
    # 204 No Content - no body returned