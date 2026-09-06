import unittest
from typing import List, Optional, AsyncIterator, Any
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.database.models import Base
from backend.models.schemas import ChatMessage
from backend.services.llm.base import BaseLLMProvider
from backend.services.memory.conversation_service import ConversationService
from backend.services.memory.memory_service import MemoryService
from backend.core.ruhi_core import RUHICore


class MockLLMProvider(BaseLLMProvider):
    def __init__(self):
        self.last_system_instruction = ""
        self.last_history = []
        self.last_message = ""

    async def generate_response(
        self,
        history: List[ChatMessage],
        new_message: str,
        system_instruction: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        self.last_system_instruction = system_instruction or ""
        self.last_history = history
        self.last_message = new_message

        # If memory context is present, simulate acknowledging it
        if "Active Persistent Context" in self.last_system_instruction:
            return f"Understood with memory context: Responding to '{new_message}'"
        return f"Standard response to '{new_message}'"

    def stream_response(
        self,
        history: List[ChatMessage],
        new_message: str,
        system_instruction: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        self.last_system_instruction = system_instruction or ""
        async def _generator():
            yield f"Streamed: {new_message}"
        return _generator()

    def get_provider_name(self) -> str:
        return "Mock LLM Provider"

    def is_configured(self) -> bool:
        return True


class TestRUHICorePersistent(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        self.session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        self.conv_service = ConversationService()
        self.conv_service.session_maker = self.session_maker

        self.mem_service = MemoryService()
        self.mem_service.session_maker = self.session_maker

        self.mock_llm = MockLLMProvider()

        self.core = RUHICore(
            llm_provider=self.mock_llm,
            conv_service=self.conv_service,
            mem_service=self.mem_service
        )

    async def asyncTearDown(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await self.engine.dispose()

    async def test_acceptance_flow_1_explicit_memory_and_retrieval(self):
        """
        Acceptance Test 1 & 4:
        1. User: "Remember that RUHI is my personal AI project."
        2. RUHI confirms.
        3. Simulate Restart / Next conversation.
        4. User: "What is RUHI?"
        5. RUHI retrieves the persistent memory and passes it to LLM.
        """
        # Step 1: Explicit Remember
        res1 = await self.core.process_message(
            message="Remember that RUHI is my personal AI project.",
            session_id="session_1"
        )
        self.assertEqual(res1.status, "success")
        self.assertIn("I'll remember that: RUHI is my personal AI project.", res1.message)
        self.assertEqual(len(res1.memory_events), 1)
        self.assertEqual(res1.memory_events[0].operation, "created")

        # Verify memory is in PostgreSQL
        memories, count = await self.mem_service.list_memories(is_active=True)
        self.assertEqual(count, 1)
        self.assertIn("RUHI is my personal AI project", memories[0].content)

        # Step 2: Next Conversation / Next query
        res2 = await self.core.process_message(
            message="Tell me about my RUHI project.",
            session_id="session_2"
        )
        self.assertEqual(res2.status, "success")
        self.assertEqual(res2.retrieved_memories_count, 1)
        # Check system instruction received the persistent memory
        self.assertIn("RUHI is my personal AI project", self.mock_llm.last_system_instruction)

    async def test_acceptance_flow_2_forget_memory(self):
        """
        Acceptance Test 3 & 5:
        1. Remember something.
        2. Forget it.
        3. Future queries no longer retrieve it.
        """
        await self.core.process_message(
            message="Remember that I want desktop control.",
            session_id="sess_forget_test"
        )
        
        # Verify stored
        memories, count = await self.mem_service.list_memories(is_active=True)
        self.assertEqual(count, 1)

        # Forget
        res_forget = await self.core.process_message(
            message="Forget that I want desktop control.",
            session_id="sess_forget_test"
        )
        self.assertEqual(res_forget.status, "success")
        self.assertIn("removed that from my persistent memory", res_forget.message)

        # Verify query no longer retrieves it
        res_after = await self.core.process_message(
            message="What desktop capabilities do I want?",
            session_id="sess_after"
        )
        self.assertEqual(res_after.retrieved_memories_count, 0)
        self.assertNotIn("desktop control", self.mock_llm.last_system_instruction)

    async def test_streaming_with_persistent_storage(self):
        """
        Tests token streaming preserves persistent turn storage.
        """
        tokens = []
        async for tok in self.core.stream_message(
            message="Streaming test message",
            session_id="stream_session_1"
        ):
            tokens.append(tok)

        self.assertGreater(len(tokens), 0)

        # Check turn was recorded in PostgreSQL
        history = await self.conv_service.get_history("stream_session_1")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].content, "Streaming test message")


if __name__ == "__main__":
    unittest.main()
