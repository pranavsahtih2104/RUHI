from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from backend.models.schemas import ChatMessage

class BaseLLMService(ABC):
    """
    Abstract AI Interface for RUHI.
    
    RUHI is an AI system built around an LLM, not the LLM itself.
    This abstraction decouples RUHI's reasoning, memory, and orchestration layers
    from specific model providers (Gemini, OpenAI, Anthropic, or local weights).
    """

    @abstractmethod
    async def generate_response(
        self,
        history: List[ChatMessage],
        new_message: str,
        system_instruction: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a conversational response given session history and new message.
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of the LLM provider."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return active model identifier."""
        pass
