from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_factory
from app.core.security import get_current_user
from app.models.register import User
from app.repositories.chat_history_repository import ChatHistoryRepository
from app.schemas.chat_history_schema import ChatHistoryCreate, ChatResponseOut, ChatHistoryOut, ConversationOut
from app.services.llm_service import generate_response

router = APIRouter(prefix="/llm", tags=["llm"])


# ────────────────────────────────────────────────
# Dependency – choose database via query parameter
# ────────────────────────────────────────────────
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
            detail="Invalid database choice. Allowed: 'local' or 'supabase'"
        )
    
    async for session in db_factory.get_session(choice):
        yield session


# ────────────────────────────────────────────────
# POST /llm/chat - Send message and get response
# ────────────────────────────────────────────────
@router.post(
    "/chat",
    response_model=ChatResponseOut,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message to LLM and save to history",
    description="Send a user message to the LLM, get a response, and save both to chat history."
)
async def chat(
    request: ChatHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db)
):
    """
    Chat endpoint with history persistence.
    
    - Requires authentication (JWT token)
    - Query parameter: db (local or supabase)
    - Saves both user message and LLM response to database
    - Returns conversation_id, message, response, and creation timestamp
    """
    try:
        # Generate LLM response
        llm_response = await generate_response(request.message)
        
        # Save to chat history
        repo = ChatHistoryRepository(db)
        chat_record = await repo.create(
            chat_data=request,
            user_id=current_user.id,
            response=llm_response,
            conversation_id=None  # Will be auto-generated in model
        )
        
        await db.commit()
        await db.refresh(chat_record)
        
        return ChatResponseOut(
            conversation_id=chat_record.conversation_id,
            message=chat_record.message,
            response=chat_record.response,
            created_at=chat_record.created_at,
        )
    
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat: {str(exc)}"
        ) from exc


# ────────────────────────────────────────────────
# GET /llm/history - Get all conversations for user
# ────────────────────────────────────────────────
@router.get(
    "/history",
    response_model=List[ChatHistoryOut],
    summary="Get all chat messages for current user",
    description="Retrieve all chat messages and responses for the authenticated user, ordered by creation time (newest first)."
)
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db)
):
    """
    Get all chat history for the current user.
    
    - Requires authentication (JWT token)
    - Returns all messages and responses sorted by newest first
    - Query parameter: db (local or supabase)
    """
    repo = ChatHistoryRepository(db)
    
    try:
        history = await repo.get_by_user(current_user.id)
        return history
    
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chat history: {str(exc)}"
        ) from exc


# ────────────────────────────────────────────────
# GET /llm/history/{conversation_id} - Get one conversation
# ────────────────────────────────────────────────
@router.get(
    "/history/{conversation_id}",
    response_model=ConversationOut,
    summary="Get all messages in a specific conversation",
    description="Retrieve all messages and responses for a specific conversation ID belonging to the current user."
)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db)
):
    """
    Get all messages in a specific conversation.
    
    - Requires authentication (JWT token)
    - Only returns conversations belonging to the current user
    - Query parameter: db (local or supabase)
    - Raises 404 if conversation not found or doesn't belong to user
    """
    repo = ChatHistoryRepository(db)
    
    try:
        messages = await repo.get_by_conversation(conversation_id, current_user.id)
        
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found or does not belong to you"
            )
        
        return ConversationOut(
            conversation_id=conversation_id,
            messages=messages
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation: {str(exc)}"
        ) from exc


# ────────────────────────────────────────────────
# DELETE /llm/history/{conversation_id} - Delete conversation
# ────────────────────────────────────────────────
@router.delete(
    "/history/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete all messages in a conversation",
    description="Delete all messages and responses in a specific conversation belonging to the current user."
)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db)
):
    """
    Delete a complete conversation.
    
    - Requires authentication (JWT token)
    - Only allows deletion of conversations belonging to the current user
    - Query parameter: db (local or supabase)
    - Returns 404 if conversation not found or doesn't belong to user
    """
    repo = ChatHistoryRepository(db)
    
    try:
        deleted_count = await repo.delete_conversation(conversation_id, current_user.id)
        
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found or does not belong to you"
            )
        
        await db.commit()
        return None
    
    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(exc)}"
        ) from exc
