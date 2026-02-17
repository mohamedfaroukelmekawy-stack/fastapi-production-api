from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ChatHistoryCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="User message to send to LLM")


class ChatHistoryOut(BaseModel):
    id: int
    conversation_id: str
    user_id: int
    message: str
    response: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationOut(BaseModel):
    """Represents a complete conversation with all messages"""
    conversation_id: str
    messages: list[ChatHistoryOut]

    model_config = ConfigDict(from_attributes=True)


class ChatResponseOut(BaseModel):
    """Response from creating a new chat message"""
    conversation_id: str
    message: str
    response: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
