# src/crud/repository.py
from typing import Generic, TypeVar, Optional, List, Any

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)


class BaseRepository(Generic[T]):
    """
    Generic base repository with common CRUD operations.
    You can inherit from this for each model.
    """

    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def create(self, data: dict) -> T:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id_value: Any) -> Optional[T]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id_value)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        order_by_column="id",
    ) -> List[T]:
        result = await self.session.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
            .order_by(getattr(self.model, order_by_column))
        )
        return result.scalars().all()

    async def update(
        self,
        id_value: Any,
        update_data: dict,
    ) -> Optional[T]:
        if not update_data:
            return None

        stmt = (
            update(self.model)
            .where(self.model.id == id_value)
            .values(**update_data)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, id_value: Any) -> Optional[T]:
        stmt = (
            delete(self.model)
            .where(self.model.id == id_value)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()