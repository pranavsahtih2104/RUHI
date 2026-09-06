from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from backend.models.schemas import ChatMessage


class BaseMemoryStore(ABC):
    """
    Abstract Memory Store interface for RUHI.
    
    Decouples session context management from the underlying storage mechanism:
    - Web v1: In-memory sliding window session store
    - Future v2: PostgreSQL / SQLite session persistence
    - Future v3: pgvector / Chroma semantic long-term memory store
    """

    @abstractmethod
    def get_history(self, session_id: str) -> List[ChatMessage]:
        """Retrieve conversation history for a given session."""
        pass

    @abstractmethod
    def add_turn(
        self,
        session_id: str,
        user_text: str,
        assistant_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a single conversational turn in memory."""
        pass

    @abstractmethod
    def clear_session(self, session_id: str) -> bool:
        """Purge all stored messages for a specific session."""
        pass

    @abstractmethod
    def active_session_count(self) -> int:
        """Return the count of active sessions."""
        pass
