import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query

from backend.models.schemas import (
    ConversationSummary,
    ConversationDetail,
    ConversationCreateRequest,
    ConversationUpdateRequest,
)
from backend.services.memory.conversation_service import conversation_service

logger = logging.getLogger("ruhi.api.conversations")
router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("", response_model=List[ConversationSummary])
async def list_conversations_endpoint(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Lists all persistent conversation sessions ordered by most recent activity.
    """
    try:
        return await conversation_service.list_conversations(limit=limit, offset=offset)
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not load conversations: {str(e)}"
        )


@router.post("", response_model=ConversationSummary, status_code=status.HTTP_201_CREATED)
async def create_conversation_endpoint(payload: Optional[ConversationCreateRequest] = None):
    """
    Creates a new persistent conversation session.
    """
    try:
        title = payload.title if payload and payload.title else "New Conversation"
        user_id = payload.user_id if payload else None
        cid = await conversation_service.ensure_conversation(title=title, user_id=user_id)
        detail = await conversation_service.get_conversation_detail(cid)
        if not detail:
            raise RuntimeError("Conversation creation succeeded but record not found.")
        return ConversationSummary(
            id=detail.id,
            title=detail.title,
            user_id=detail.user_id,
            created_at=detail.created_at,
            updated_at=detail.updated_at,
            message_count=0,
            last_message_preview=None,
        )
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create conversation: {str(e)}"
        )


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation_endpoint(conversation_id: str):
    """
    Retrieves a single conversation along with all its persisted message turns.
    """
    try:
        conv = await conversation_service.get_conversation_detail(conversation_id)
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found."
            )
        return conv
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load conversation '{conversation_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not load conversation: {str(e)}"
        )


@router.patch("/{conversation_id}")
async def rename_conversation_endpoint(
    conversation_id: str,
    payload: ConversationUpdateRequest
):
    """
    Renames the title of an existing conversation.
    """
    try:
        success = await conversation_service.update_title(conversation_id, payload.title.strip())
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found."
            )
        return {"status": "success", "conversation_id": conversation_id, "title": payload.title}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to rename conversation '{conversation_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not rename conversation: {str(e)}"
        )


@router.delete("/{conversation_id}")
async def delete_conversation_endpoint(conversation_id: str):
    """
    Deletes a conversation and its message history from PostgreSQL.
    """
    try:
        success = await conversation_service.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found."
            )
        return {"status": "deleted", "conversation_id": conversation_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation '{conversation_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete conversation: {str(e)}"
        )
