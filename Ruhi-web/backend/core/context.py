from typing import List, Optional, Dict, Any
from backend.models.schemas import ChatMessage, MemorySchema
from backend.config.settings import settings
from backend.core.prompt import RUHI_SYSTEM_INSTRUCTION


class ContextManager:
    """
    Manages conversational context packaging, sliding window trimming,
    and long-term memory prompt formulation for RUHI Core.
    """

    def __init__(self, max_history_turns: Optional[int] = None):
        self.max_history_turns = max_history_turns or settings.MAX_SESSION_HISTORY

    def prepare_context_window(
        self,
        raw_history: List[ChatMessage],
        extra_context: Optional[Dict[str, Any]] = None
    ) -> List[ChatMessage]:
        """
        Extract sliding window of messages, respecting maximum turns limit.
        """
        if len(raw_history) > self.max_history_turns:
            return raw_history[-self.max_history_turns:]
        return list(raw_history)

    def build_system_instruction(
        self,
        relevant_memories: Optional[List[MemorySchema]] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Builds the unified system instruction, incorporating relevant persistent memories.
        """
        base_instruction = RUHI_SYSTEM_INSTRUCTION

        if not relevant_memories:
            return base_instruction

        memory_bullets = []
        for mem in relevant_memories:
            type_label = mem.memory_type.capitalize()
            memory_bullets.append(f"- [{type_label}]: {mem.content}")

        memory_block = (
            "\n\n[Active Persistent Context & Memories]\n"
            "You have recalled the following persistent facts, goals, or preferences about the user:\n"
            + "\n".join(memory_bullets) + "\n\n"
            "Instruction: Use these recalled memories naturally and coherently to personalize your response. "
            "Do not recite the memory list verbatim unless asked."
        )

        return base_instruction + memory_block


context_manager = ContextManager()
