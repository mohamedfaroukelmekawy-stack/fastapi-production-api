from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.register import User


class ChatHistory(Base):
    __tablename__ = "chat_histories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    conversation_id: Mapped[str] = mapped_column(
        String(36),  # UUID string length
        nullable=False,
        index=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    response: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # Relationship to User
    user: Mapped["User"] = relationship(back_populates="chat_histories")

    def __repr__(self) -> str:
        return (
            f"<ChatHistory(id={self.id}, conversation_id={self.conversation_id!r}, "
            f"user_id={self.user_id}, created_at={self.created_at})>"
        )
