import json
import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse

from backend.models.schemas import (
    ChatRequest,
    ChatResponse,
    ClearSessionRequest,
    ClearSessionResponse,
)
from backend.core.ruhi_core import ruhi_core

logger = logging.getLogger("ruhi.api.chat")
router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """
    Standard synchronous chat endpoint for RUHI Web with persistent memory.
    """
    if not payload.message or not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty."
        )

    target_session_id = payload.conversation_id or payload.session_id

    try:
        response = await ruhi_core.process_message(
            message=payload.message,
            session_id=target_session_id,
            context=payload.context
        )
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "session_id": target_session_id or "unknown",
                "conversation_id": target_session_id or "unknown",
                "message": f"RUHI encountered an issue: {str(e)}",
                "status": "error",
                "provider": "RUHI Core",
                "context_turn_count": 0,
                "retrieved_memories_count": 0,
                "memory_events": [],
                "error": str(e)
            }
        )


@router.post("/chat/stream")
async def chat_stream_endpoint(payload: ChatRequest):
    """
    Server-Sent Events (SSE) streaming endpoint with persistent PostgreSQL storage.
    """
    if not payload.message or not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty."
        )

    target_session_id = payload.conversation_id or payload.session_id or "default_session"

    async def event_generator():
        try:
            # First event: start acknowledgment
            yield f"data: {json.dumps({'type': 'start', 'session_id': target_session_id, 'conversation_id': target_session_id})}\n\n"

            async for token in ruhi_core.stream_message(
                message=payload.message,
                session_id=target_session_id,
                context=payload.context
            ):
                yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"

            # Completion event
            yield f"data: {json.dumps({'type': 'done', 'session_id': target_session_id, 'conversation_id': target_session_id})}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/chat/clear", response_model=ClearSessionResponse)
async def clear_session_endpoint(payload: ClearSessionRequest):
    """
    Purges conversation messages for the specified session in PostgreSQL.
    """
    success = await ruhi_core.clear_context(payload.session_id)
    return ClearSessionResponse(
        session_id=payload.session_id,
        status="cleared" if success else "not_found",
        message="Conversation context reset successfully."
    )
