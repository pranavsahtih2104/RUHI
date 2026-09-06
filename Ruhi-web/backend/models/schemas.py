from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone


def current_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# -----------------------------------------------------------------------------
# Chat & Turn Schemas
# -----------------------------------------------------------------------------

class ChatMessage(BaseModel):
    id: Optional[str] = None
    role: str = Field(..., description="Role: 'user' | 'assistant' | 'system'")
    content: str = Field(..., description="Text content of the message")
    timestamp: str = Field(default_factory=current_utc_iso)
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional message-level metadata")


class MemoryOperationEvent(BaseModel):
    operation: str = Field(..., description="'created' | 'forgotten' | 'retrieved' | 'updated'")
    memory_id: Optional[str] = None
    content: Optional[str] = None
    memory_type: Optional[str] = None
    summary: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User input message")
    session_id: Optional[str] = Field(None, description="Session / Conversation ID")
    conversation_id: Optional[str] = Field(None, description="Alias for session_id")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional extra runtime context")
    stream: bool = Field(default=False, description="Whether to request token streaming")


class ChatResponse(BaseModel):
    session_id: str
    conversation_id: Optional[str] = None
    message: str
    status: str = "success"
    provider: str = "RUHI Core"
    timestamp: str = Field(default_factory=current_utc_iso)
    context_turn_count: int = 0
    retrieved_memories_count: int = 0
    memory_events: List[MemoryOperationEvent] = Field(default_factory=list)
    error: Optional[str] = None


class ClearSessionRequest(BaseModel):
    session_id: str


class ClearSessionResponse(BaseModel):
    session_id: str
    status: str = "cleared"
    message: str = "Conversation context reset successfully."


# -----------------------------------------------------------------------------
# Conversation Management Schemas (Persistent Stage 2)
# -----------------------------------------------------------------------------

class ConversationSummary(BaseModel):
    id: str
    title: str
    user_id: Optional[str] = None
    created_at: str
    updated_at: str
    message_count: int = 0
    last_message_preview: Optional[str] = None


class ConversationDetail(BaseModel):
    id: str
    title: str
    user_id: Optional[str] = None
    created_at: str
    updated_at: str
    messages: List[ChatMessage] = Field(default_factory=list)


class ConversationCreateRequest(BaseModel):
    title: Optional[str] = Field(default="New Conversation")
    user_id: Optional[str] = None


class ConversationUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


# -----------------------------------------------------------------------------
# Long-Term Persistent Memory Schemas (Persistent Stage 2)
# -----------------------------------------------------------------------------

class MemorySchema(BaseModel):
    id: str
    user_id: Optional[str] = None
    content: str
    memory_type: str = "general"
    importance: int = 5
    source: str = "explicit"
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str


class MemoryCreateRequest(BaseModel):
    content: str = Field(..., min_length=2, description="Fact, preference, goal, or instruction")
    memory_type: str = Field(default="general", description="preference | fact | goal | project | instruction | relationship | event | general")
    importance: int = Field(default=5, ge=1, le=10, description="Importance score 1-10")
    source: str = Field(default="explicit", description="explicit | extracted | system")
    user_id: Optional[str] = None


class MemoryUpdateRequest(BaseModel):
    content: Optional[str] = None
    memory_type: Optional[str] = None
    importance: Optional[int] = Field(None, ge=1, le=10)
    is_active: Optional[bool] = None


class MemoryListResponse(BaseModel):
    memories: List[MemorySchema]
    total: int


# -----------------------------------------------------------------------------
# Health & Tool Schemas
# -----------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    service: str = "RUHI AI Core"
    database_connected: bool = True
    database_name: str = "ruhi-web"
    active_sessions: int = 0
    persistent_memories_count: int = 0
    configured_api_key: bool = True
    streaming_supported: bool = True
    available_tools_count: int = 3


class ToolDefinitionSchema(BaseModel):
    name: str
    description: str
    category: str
    requires_desktop: bool = False
    parameters: Dict[str, Any] = {}


class ToolExecutionRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}


class ToolExecutionResponse(BaseModel):
    tool_name: str
    success: bool
    result: Any = None
    error: Optional[str] = None
