import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query

from backend.models.schemas import (
    MemorySchema,
    MemoryCreateRequest,
    MemoryUpdateRequest,
    MemoryListResponse,
)
from backend.services.memory.memory_service import memory_service

logger = logging.getLogger("ruhi.api.memories")
router = APIRouter(prefix="/memories", tags=["Persistent Memories"])


@router.get("", response_model=MemoryListResponse)
async def list_memories_endpoint(
    type: Optional[str] = Query(default=None, description="Filter by type: preference, fact, goal, project, instruction, general"),
    search: Optional[str] = Query(default=None, description="Search term across memory contents"),
    active: bool = Query(default=True, description="Filter active memories"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Retrieves a list of persistent long-term memories with filtering and search.
    """
    try:
        memories, total = await memory_service.list_memories(
            memory_type=type,
            search=search,
            is_active=active,
            limit=limit,
            offset=offset,
        )
        return MemoryListResponse(memories=memories, total=total)
    except Exception as e:
        logger.error(f"Failed to list memories: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not load memories: {str(e)}"
        )


@router.post("", response_model=MemorySchema, status_code=status.HTTP_201_CREATED)
async def create_memory_endpoint(payload: MemoryCreateRequest):
    """
    Manually creates a new persistent memory.
    """
    try:
        return await memory_service.create_memory(payload)
    except Exception as e:
        logger.error(f"Failed to create memory: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create memory: {str(e)}"
        )


@router.get("/{memory_id}", response_model=MemorySchema)
async def get_memory_endpoint(memory_id: str):
    """
    Retrieves a single memory by ID.
    """
    try:
        mem = await memory_service.get_memory(memory_id)
        if not mem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory '{memory_id}' not found."
            )
        return mem
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load memory '{memory_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not load memory: {str(e)}"
        )


@router.patch("/{memory_id}", response_model=MemorySchema)
async def update_memory_endpoint(memory_id: str, payload: MemoryUpdateRequest):
    """
    Updates the content, type, importance, or active state of a memory.
    """
    try:
        mem = await memory_service.update_memory(memory_id, payload)
        if not mem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory '{memory_id}' not found."
            )
        return mem
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update memory '{memory_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not update memory: {str(e)}"
        )


@router.delete("/{memory_id}")
async def delete_memory_endpoint(
    memory_id: str,
    hard: bool = Query(default=False, description="Permanently delete instead of deactivating")
):
    """
    Deactivates (or permanently deletes) a persistent memory.
    """
    try:
        success = await memory_service.delete_memory(memory_id, hard_delete=hard)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory '{memory_id}' not found."
            )
        return {"status": "deleted", "memory_id": memory_id, "hard_delete": hard}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete memory '{memory_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete memory: {str(e)}"
        )
