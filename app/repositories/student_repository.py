# src/crud/student.py
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate
from app.crud.baserepository import BaseRepository


class StudentRepository(BaseRepository[Student]):
    """
    Student-specific repository – inherits common CRUD from BaseRepository
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Student)

    async def create(self, student_data: StudentCreate) -> Student:
        return await super().create(student_data.model_dump())

    async def get_by_id(self, student_id: int) -> Optional[Student]:
        return await super().get_by_id(student_id)

    async def get_all(self, skip: int = 0, limit: int = 50) -> List[Student]:
        return await super().get_all(skip=skip, limit=limit)

    async def update(
        self, student_id: int, update_data: StudentUpdate
    ) -> Optional[Student]:
        values = update_data.model_dump(exclude_unset=True)
        return await super().update(student_id, values)

    async def delete(self, student_id: int) -> Optional[Student]:
        return await super().delete(student_id)