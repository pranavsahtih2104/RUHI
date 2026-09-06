from fastapi import APIRouter
from backend.models.schemas import HealthResponse
from backend.core.ruhi_core import ruhi_core

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint returning core readiness, PostgreSQL connection status,
    active sessions, and persistent memory counts.
    """
    status_info = await ruhi_core.get_system_status()
    return HealthResponse(
        status=status_info["status"],
        version=status_info["version"],
        service=status_info["service"],
        database_connected=status_info.get("database_connected", False),
        database_name=status_info.get("database_name", "ruhi-web"),
        active_sessions=status_info.get("active_sessions", 0),
        persistent_memories_count=status_info.get("persistent_memories_count", 0),
        configured_api_key=status_info.get("configured_api_key", False),
        streaming_supported=status_info.get("streaming_supported", True),
        available_tools_count=status_info.get("available_tools_count", 0),
    )
