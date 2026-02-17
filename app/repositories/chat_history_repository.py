from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_history import ChatHistory
from app.schemas.chat_history_schema import ChatHistoryCreate
from app.repositories.base_repository import BaseRepository


class ChatHistoryRepository(BaseRepository[ChatHistory]):
    """
    Chat History-specific repository – inherits common CRUD from BaseRepository
    Provides methods for managing chat conversations and history
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, ChatHistory)

    async def create(self, chat_data: ChatHistoryCreate, user_id: int, response: str, conversation_id: str) -> ChatHistory:
        """
        Create a new chat history record with message and response
        """
        payload = chat_data.model_dump()
        payload.update({
            "user_id": user_id,
            "response": response,
            "conversation_id": conversation_id,
        })
        return await super().create(payload)

    async def get_by_user(self, user_id: int) -> List[ChatHistory]:
        """
        Get all chat histories for a specific user
        """
        stmt = select(ChatHistory).where(ChatHistory.user_id == user_id).order_by(ChatHistory.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_conversation(self, conversation_id: str, user_id: int) -> List[ChatHistory]:
        """
        Get all messages in a specific conversation for a specific user
        """
        stmt = (
            select(ChatHistory)
            .where(
                ChatHistory.conversation_id == conversation_id,
                ChatHistory.user_id == user_id,
            )
            .order_by(ChatHistory.created_at)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_conversation(self, conversation_id: str, user_id: int) -> int:
        """
        Delete all messages in a conversation for a specific user.
        Returns the count of deleted records.
        """
        stmt = select(ChatHistory).where(
            ChatHistory.conversation_id == conversation_id,
            ChatHistory.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        for record in records:
            await self.session.delete(record)

        await self.session.commit()
        return len(records)
