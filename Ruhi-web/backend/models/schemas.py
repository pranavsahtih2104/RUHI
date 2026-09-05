from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' | 'assistant' | 'system'")
    content: str = Field(..., description="Text content of the message")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User input message")
    session_id: Optional[str] = Field(None, description="Unique session identifier")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional personal context or parameters")

class ChatResponse(BaseModel):
    session_id: str
    message: str
    status: str = "success"
    model: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    context_turn_count: int = 0

class ClearSessionRequest(BaseModel):
    session_id: str

class ClearSessionResponse(BaseModel):
    session_id: str
    status: str = "cleared"
    message: str = "Conversation context reset successfully."

class HealthResponse(BaseModel):
    status: str
    version: str
    llm_provider: str
    model: str
    active_sessions: int
    configured_api_key: bool
