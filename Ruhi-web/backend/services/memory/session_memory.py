import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.models.schemas import ChatMessage
from backend.config.settings import settings

class SessionContext:
    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.messages: List[ChatMessage] = []
        self.created_at: float = time.time()
        self.last_accessed: float = time.time()
        self.metadata: Dict[str, Any] = {}

    def add_message(self, role: str, content: str):
        self.messages.append(ChatMessage(role=role, content=content))
        self.last_accessed = time.time()
        # Keep within max sliding window history
        if len(self.messages) > settings.MAX_SESSION_HISTORY:
            self.messages = self.messages[-settings.MAX_SESSION_HISTORY:]

    def clear(self):
        self.messages.clear()
        self.last_accessed = time.time()


class SessionMemoryManager:
    """
    Manages active session context for RUHI web conversations.
    
    Future Extension Point:
    - Long-term memory extraction (e.g. user facts, preferences, project states)
    - Persistent database storage (SQLite / Postgres)
    - Semantic vector retrieval (Embeddings + Vector DB)
    """

    def __init__(self):
        self._sessions: Dict[str, SessionContext] = {}

    def get_or_create_session(self, session_id: Optional[str] = None) -> SessionContext:
        self._cleanup_expired_sessions()
        
        if not session_id or session_id not in self._sessions:
            new_id = session_id or str(uuid.uuid4())
            self._sessions[new_id] = SessionContext(session_id=new_id)
            return self._sessions[new_id]
        
        session = self._sessions[session_id]
        session.last_accessed = time.time()
        return session

    def get_history(self, session_id: str) -> List[ChatMessage]:
        if session_id in self._sessions:
            return self._sessions[session_id].messages
        return []

    def add_turn(self, session_id: str, user_text: str, assistant_text: str):
        session = self.get_or_create_session(session_id)
        session.add_message("user", user_text)
        session.add_message("assistant", assistant_text)

    def clear_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            self._sessions[session_id].clear()
            return True
        return False

    def active_session_count(self) -> int:
        return len(self._sessions)

    def _cleanup_expired_sessions(self):
        expiry_seconds = settings.SESSION_EXPIRY_MINUTES * 60
        now = time.time()
        expired_keys = [
            sid for sid, sess in self._sessions.items()
            if now - sess.last_accessed > expiry_seconds
        ]
        for sid in expired_keys:
            del self._sessions[sid]


# Global memory singleton
memory_manager = SessionMemoryManager()
