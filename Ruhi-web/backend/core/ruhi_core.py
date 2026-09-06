import logging
import uuid
from typing import Optional, Dict, Any, AsyncIterator, List

from backend.config.settings import settings
from backend.models.schemas import (
    ChatMessage,
    ChatResponse,
    MemoryOperationEvent,
)
from backend.services.llm.base import BaseLLMProvider
from backend.services.llm.gemini_service import GeminiProvider
from backend.services.memory.conversation_service import (
    ConversationService,
    conversation_service as default_conv_service,
)
from backend.services.memory.memory_service import (
    MemoryService,
    memory_service as default_memory_service,
)
from backend.services.tools.registry import tool_manager, ToolManager
from backend.core.prompt import RUHI_SYSTEM_INSTRUCTION
from backend.core.context import context_manager, ContextManager
from backend.database.connection import check_database_connection

logger = logging.getLogger("ruhi.core")


class RUHICore:
    """
    RUHI Central Intelligence Layer (Stage 2: Persistent Memory & PostgreSQL).
    
    Coordinates:
    - Persistent Conversation Management (PostgreSQL)
    - Persistent Long-Term Memory (Explicit commands, conservative extraction & retrieval)
    - Context Window Formulation
    - Safe Tool Registry & Routing
    - Decoupled LLM Provider Execution
    """

    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        conv_service: Optional[ConversationService] = None,
        mem_service: Optional[MemoryService] = None,
        tool_mgr: Optional[ToolManager] = None,
        context_mgr: Optional[ContextManager] = None,
    ):
        self.llm_provider = llm_provider or GeminiProvider()
        self.conversation_service = conv_service or default_conv_service
        self.memory_service = mem_service or default_memory_service
        self.tool_manager = tool_mgr or tool_manager
        self.context_manager = context_mgr or context_manager
        logger.info("RUHI Core (Stage 2: Persistent Memory) initialized.")

    def set_llm_provider(self, provider: BaseLLMProvider):
        """Allows runtime swapping of LLM provider without restarting RUHI Core."""
        self.llm_provider = provider
        logger.info(f"Swapped LLM Provider to: {provider.get_provider_name()}")

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> ChatResponse:
        """
        Processes a single user message through the persistent memory & LLM pipeline.
        """
        clean_text = message.strip()
        if not clean_text:
            raise ValueError("Message content cannot be empty.")

        actual_user_id = user_id or settings.DEFAULT_USER_ID
        actual_session_id = await self.conversation_service.ensure_conversation(
            conversation_id=session_id,
            user_id=actual_user_id,
        )

        memory_events: List[MemoryOperationEvent] = []

        # 1. Check for explicit memory commands
        explicit_cmd = self.memory_service.detect_explicit_command(clean_text)
        if explicit_cmd:
            cmd_type, payload = explicit_cmd
            logger.info(f"Explicit memory command detected: '{cmd_type}' -> '{payload}'")

            if cmd_type == "remember":
                event = await self.memory_service.save_explicit_memory(payload, user_id=actual_user_id)
                memory_events.append(event)
                reply = f"I'll remember that: {payload}."
                await self.conversation_service.add_turn(
                    conversation_id=actual_session_id,
                    user_text=clean_text,
                    assistant_text=reply,
                )
                return ChatResponse(
                    session_id=actual_session_id,
                    conversation_id=actual_session_id,
                    message=reply,
                    status="success",
                    provider="RUHI Core",
                    context_turn_count=1,
                    retrieved_memories_count=0,
                    memory_events=memory_events,
                )

            elif cmd_type == "forget":
                event = await self.memory_service.forget_memory(payload, user_id=actual_user_id)
                memory_events.append(event)
                reply = f"I've removed that from my persistent memory." if event.memory_id else "I couldn't find a matching active memory to forget."
                await self.conversation_service.add_turn(
                    conversation_id=actual_session_id,
                    user_text=clean_text,
                    assistant_text=reply,
                )
                return ChatResponse(
                    session_id=actual_session_id,
                    conversation_id=actual_session_id,
                    message=reply,
                    status="success",
                    provider="RUHI Core",
                    context_turn_count=1,
                    retrieved_memories_count=0,
                    memory_events=memory_events,
                )

            elif cmd_type == "query":
                memories, _ = await self.memory_service.list_memories(user_id=actual_user_id, is_active=True)
                if not memories:
                    reply = "I don't have any persistent memories saved about you yet. You can tell me things to remember anytime by saying 'Remember that...'."
                else:
                    bullets = "\n".join(f"• **[{m.memory_type.capitalize()}]**: {m.content}" for m in memories)
                    reply = f"Here is what I currently remember about you across our conversations:\n\n{bullets}"

                await self.conversation_service.add_turn(
                    conversation_id=actual_session_id,
                    user_text=clean_text,
                    assistant_text=reply,
                )
                return ChatResponse(
                    session_id=actual_session_id,
                    conversation_id=actual_session_id,
                    message=reply,
                    status="success",
                    provider="RUHI Core",
                    context_turn_count=len(memories),
                    retrieved_memories_count=len(memories),
                    memory_events=memory_events,
                )

        # 2. Standard Conversational Flow: Retrieve relevant persistent memories
        relevant_memories = await self.memory_service.retrieve_relevant_memories(
            query_text=clean_text,
            user_id=actual_user_id,
            max_memories=4
        )
        if relevant_memories:
            logger.info(f"Retrieved {len(relevant_memories)} relevant persistent memories for query.")

        # 3. Load conversation history from PostgreSQL
        raw_history = await self.conversation_service.get_history(actual_session_id)
        history_window = self.context_manager.prepare_context_window(raw_history, context)

        # 4. Formulate contextual prompt with active memories
        system_instruction = self.context_manager.build_system_instruction(
            relevant_memories=relevant_memories,
            extra_context=context,
        )

        try:
            # 5. Generate LLM response
            response_text = await self.llm_provider.generate_response(
                history=history_window,
                new_message=clean_text,
                system_instruction=system_instruction,
            )

            # 6. Save turn to PostgreSQL
            await self.conversation_service.add_turn(
                conversation_id=actual_session_id,
                user_text=clean_text,
                assistant_text=response_text,
            )

            # 7. Conservative automatic memory extraction
            auto_mem = self.memory_service.extract_conservative_memory(clean_text)
            if auto_mem:
                content, m_type, importance = auto_mem
                auto_event = await self.memory_service.save_explicit_memory(content, user_id=actual_user_id)
                memory_events.append(auto_event)
                logger.info(f"Conservatively extracted memory: [{m_type}] '{content}'")

            updated_history = await self.conversation_service.get_history(actual_session_id)

            return ChatResponse(
                session_id=actual_session_id,
                conversation_id=actual_session_id,
                message=response_text,
                status="success",
                provider="RUHI Core",
                context_turn_count=len(updated_history),
                retrieved_memories_count=len(relevant_memories),
                memory_events=memory_events,
            )

        except Exception as e:
            logger.error(f"Error in RUHI Core message processing: {e}", exc_info=True)
            raise RuntimeError(f"RUHI Core encountered an issue: {str(e)}")

    async def stream_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Streams response tokens sequentially with persistent memory context.
        Persists completed turn to PostgreSQL upon stream completion.
        """
        clean_text = message.strip()
        if not clean_text:
            raise ValueError("Message content cannot be empty.")

        actual_user_id = user_id or settings.DEFAULT_USER_ID
        actual_session_id = await self.conversation_service.ensure_conversation(
            conversation_id=session_id,
            user_id=actual_user_id,
        )

        # Check explicit commands first
        explicit_cmd = self.memory_service.detect_explicit_command(clean_text)
        if explicit_cmd:
            resp = await self.process_message(
                message=clean_text,
                session_id=actual_session_id,
                context=context,
                user_id=actual_user_id,
            )
            yield resp.message
            return

        # Retrieve relevant persistent memories
        relevant_memories = await self.memory_service.retrieve_relevant_memories(
            query_text=clean_text,
            user_id=actual_user_id,
            max_memories=4
        )

        raw_history = await self.conversation_service.get_history(actual_session_id)
        history_window = self.context_manager.prepare_context_window(raw_history, context)
        system_instruction = self.context_manager.build_system_instruction(
            relevant_memories=relevant_memories,
            extra_context=context,
        )

        accumulated_chunks: list[str] = []

        try:
            async for token in self.llm_provider.stream_response(
                history=history_window,
                new_message=clean_text,
                system_instruction=system_instruction,
            ):
                accumulated_chunks.append(token)
                yield token

            # On stream completion, persist turn to PostgreSQL
            full_response = "".join(accumulated_chunks)
            if full_response.strip():
                await self.conversation_service.add_turn(
                    conversation_id=actual_session_id,
                    user_text=clean_text,
                    assistant_text=full_response,
                )

                # Conservative extraction
                auto_mem = self.memory_service.extract_conservative_memory(clean_text)
                if auto_mem:
                    content, _, _ = auto_mem
                    await self.memory_service.save_explicit_memory(content, user_id=actual_user_id)

        except Exception as e:
            logger.error(f"Error in RUHI Core streaming: {e}", exc_info=True)
            raise RuntimeError(f"RUHI Streaming encountered an issue: {str(e)}")

    async def clear_context(self, session_id: str) -> bool:
        """Purges conversational messages for a given session."""
        return await self.conversation_service.delete_conversation(session_id)

    async def get_system_status(self) -> Dict[str, Any]:
        """Returns comprehensive health, DB, and readiness metadata."""
        db_probe = await check_database_connection()
        total_memories = 0
        convs = []
        if db_probe.get("connected"):
            try:
                _, total_memories = await self.memory_service.list_memories(is_active=True, limit=1)
                convs = await self.conversation_service.list_conversations(limit=100)
            except Exception as e:
                logger.warning(f"Error querying memory/conversation metrics: {e}")

        return {
            "status": "healthy" if db_probe.get("connected") else "degraded",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "database_connected": db_probe.get("connected", False),
            "database_name": "ruhi-web",
            "active_sessions": len(convs),
            "persistent_memories_count": total_memories,
            "configured_api_key": self.llm_provider.is_configured(),
            "streaming_supported": True,
            "available_tools_count": len(self.tool_manager.list_active_tools()),
        }


# Singleton instance of RUHI Core
ruhi_core = RUHICore()
