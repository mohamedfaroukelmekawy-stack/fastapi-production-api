from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate
from app.crud.baserepository import BaseRepository


class ItemRepository(BaseRepository[Item]):
    """
    Item-specific repository – inherits common CRUD from BaseRepository
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Item)

    async def create(self, item_data: ItemCreate) -> Item:
        return await super().create(item_data.model_dump())

    async def get_by_id(self, item_id: int) -> Optional[Item]:
        return await super().get_by_id(item_id)

    async def get_all(self, skip: int = 0, limit: int = 50) -> List[Item]:
        return await super().get_all(skip=skip, limit=limit)

    async def update(
        self, item_id: int, update_data: ItemUpdate
    ) -> Optional[Item]:
        values = update_data.model_dump(exclude_unset=True)
        return await super().update(item_id, values)

    async def delete(self, item_id: int) -> Optional[Item]:
        return await super().delete(item_id)
