# from fastapi import APIRouter, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession

# from src.database import async_session_factory
# from src.schemas.student import StudentCreate, StudentUpdate, StudentOut
# from src.crud.student import (
#     create_student,
#     get_student,
#     get_all_students,
#     update_student,
#     delete_student,
# )

# router = APIRouter(prefix="/students", tags=["students"])


# # 1. CREATE (POST / insert)
# @router.post("/", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
# async def create_student_endpoint(student: StudentCreate):
#     """
#     Create a new student (INSERT)
#     """
#     async with async_session_factory() as session:
#         created = await create_student(session, student)
#         return created


# # 2. SELECT ONE (GET by id)
# @router.get("/{student_id}", response_model=StudentOut)
# async def get_student_by_id(student_id: int):
#     """
#     Get one student by ID (SELECT WHERE id = ?)
#     """
#     async with async_session_factory() as session:
#         student = await get_student(session, student_id)
#         if student is None:
#             raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
#         return student


# # 3. SELECT ALL (GET list)
# @router.get("/", response_model=list[StudentOut])
# async def get_all_students_endpoint(skip: int = 0, limit: int = 50):
#     """
#     Get list of all students (SELECT with LIMIT and OFFSET)
#     """
#     async with async_session_factory() as session:
#         students = await get_all_students(session, skip=skip, limit=limit)
#         return students


# # 4. UPDATE (PUT – full replace)
# @router.put("/{student_id}", response_model=StudentOut)
# async def update_student_endpoint(student_id: int, student_data: StudentUpdate):
#     """
#     Update existing student (full replace – PUT)
#     """
#     if not student_data.model_dump(exclude_unset=True):
#         raise HTTPException(
#             status.HTTP_400_BAD_REQUEST,
#             "At least one field must be provided for update"
#         )

#     async with async_session_factory() as session:
#         updated = await update_student(session, student_id, student_data)
#         if updated is None:
#             raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
#         return updated


# # 5. DELETE
# @router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_student_endpoint(student_id: int):
#     """
#     Delete a student by ID
#     """
#     async with async_session_factory() as session:
#         deleted = await delete_student(session, student_id)
#         if deleted is None:
#             raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
#         # 204 = no content → return nothing