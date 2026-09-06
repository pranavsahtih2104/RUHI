from abc import ABC, abstractmethod
from typing import List, Optional, AsyncIterator, Dict, Any
from backend.models.schemas import ChatMessage


class BaseLLMProvider(ABC):
    """
    Abstract LLM Provider interface for RUHI.
    
    RUHI is an autonomous personal AI system, not a wrapper around any single model.
    This abstraction decouples RUHI Core (prompting, context, tool routing, memory)
    from the underlying model provider (Gemini, Claude, GPT-4o, or local weights).
    """

    @abstractmethod
    async def generate_response(
        self,
        history: List[ChatMessage],
        new_message: str,
        system_instruction: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate a complete conversational response string."""
        pass

    @abstractmethod
    def stream_response(
        self,
        history: List[ChatMessage],
        new_message: str,
        system_instruction: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Yield response tokens sequentially as they are generated."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider identifier name."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if provider credentials/client are configured and valid."""
        pass
