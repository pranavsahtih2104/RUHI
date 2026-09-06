import unittest
import asyncio
from typing import List, Optional, AsyncIterator, Any
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.database.models import Base
from backend.models.schemas import ChatMessage
from backend.services.llm.base import BaseLLMProvider
from backend.services.memory.session_memory import SessionMemoryStore
from backend.services.memory.conversation_service import ConversationService
from backend.services.memory.memory_service import MemoryService
from backend.services.tools.calculator import CalculatorTool
from backend.services.tools.datetime_tool import DateTimeTool
from backend.services.tools.web_search import WebRetrievalTool
from backend.services.tools.registry import ToolManager
from backend.core.ruhi_core import RUHICore
from backend.core.context import ContextManager


class MockLLMProvider(BaseLLMProvider):
    def __init__(self, fixed_reply: str = "Mocked RUHI intelligent reply"):
        self.fixed_reply = fixed_reply
        self.calls = []

    async def generate_response(
        self,
        history: List[ChatMessage],
        new_message: str,
        system_instruction: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        self.calls.append({"history": history, "new_message": new_message})
        return f"{self.fixed_reply}: {new_message}"

    def stream_response(
        self,
        history: List[ChatMessage],
        new_message: str,
        system_instruction: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        async def _generator():
            tokens = [f"{self.fixed_reply}: ", new_message]
            for t in tokens:
                yield t
        return _generator()

    def get_provider_name(self) -> str:
        return "Mock Provider"

    def is_configured(self) -> bool:
        return True


class TestRUHICore(unittest.IsolatedAsyncioTestCase):

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

    async def asyncTearDown(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await self.engine.dispose()

    async def test_ruhi_core_process_message(self):
        mock_provider = MockLLMProvider()
        core = RUHICore(
            llm_provider=mock_provider,
            conv_service=self.conv_service,
            mem_service=self.mem_service
        )

        response = await core.process_message("Hello RUHI", session_id="test_sess_1")
        self.assertEqual(response.status, "success")
        self.assertEqual(response.session_id, "test_sess_1")
        self.assertIn("Mocked RUHI intelligent reply: Hello RUHI", response.message)
        self.assertEqual(response.context_turn_count, 2)

        # Verify history is stored in persistent memory
        history = await self.conv_service.get_history("test_sess_1")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].role, "user")
        self.assertEqual(history[0].content, "Hello RUHI")
        self.assertEqual(history[1].role, "assistant")

    async def test_ruhi_core_streaming_and_memory(self):
        mock_provider = MockLLMProvider()
        core = RUHICore(
            llm_provider=mock_provider,
            conv_service=self.conv_service,
            mem_service=self.mem_service
        )

        tokens = []
        async for tok in core.stream_message("Streaming query", session_id="test_sess_stream"):
            tokens.append(tok)

        self.assertGreater(len(tokens), 0)
        full_text = "".join(tokens)
        self.assertIn("Streaming query", full_text)

        # Verify turn committed to persistent database after stream completion
        history = await self.conv_service.get_history("test_sess_stream")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].content, "Streaming query")
        self.assertEqual(history[1].content, full_text)

    def test_session_memory_sliding_window(self):
        memory = SessionMemoryStore()
        session_id = "test_window"

        for i in range(20):
            memory.add_turn(session_id, f"User msg {i}", f"Assistant msg {i}")

        history = memory.get_history(session_id)
        self.assertLessEqual(len(history), 30)

        # Test clear
        self.assertTrue(memory.clear_session(session_id))
        self.assertEqual(len(memory.get_history(session_id)), 0)

    async def test_calculator_tool(self):
        calc = CalculatorTool()
        res = await calc.execute(expression="sqrt(144) + 10 * 5")
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 62.0)

        # Unary operations and floor division
        res_unary = await calc.execute(expression="-5 + 15 // 2")
        self.assertTrue(res_unary["success"])
        self.assertEqual(res_unary["result"], 2.0)

        res_const = await calc.execute(expression="pi * 2")
        self.assertTrue(res_const["success"])
        self.assertAlmostEqual(res_const["result"], 6.2831853, places=5)

        err_res = await calc.execute(expression="invalid_syntax +++")
        self.assertFalse(err_res["success"])
        self.assertIn("error", err_res)

    async def test_datetime_tool(self):
        dt_tool = DateTimeTool()
        res = await dt_tool.execute(timezone_name="UTC")
        self.assertTrue(res["success"])
        self.assertIn("iso", res)
        self.assertIn("date", res)
        self.assertEqual(res["timezone"], "UTC")

    async def test_web_retrieval_tool_validation(self):
        tool = WebRetrievalTool()
        # Empty URL test
        res_empty = await tool.execute()
        self.assertFalse(res_empty["success"])
        self.assertIn("error", res_empty)

        # Invalid protocol test
        res_ftp = await tool.execute(url="ftp://example.com/file")
        self.assertFalse(res_ftp["success"])
        self.assertIn("HTTP and HTTPS", res_ftp["error"])

        # Restricted IP test
        res_local = await tool.execute(url="http://127.0.0.1:8000/secret")
        self.assertFalse(res_local["success"])
        self.assertIn("restricted", res_local["error"])

    async def test_tool_manager(self):
        tm = ToolManager()
        active_tools = tm.list_active_tools()
        tool_names = [t.name for t in active_tools]
        self.assertIn("calculator", tool_names)
        self.assertIn("datetime_tool", tool_names)
        self.assertIn("web_retrieval", tool_names)

        res = await tm.execute_tool("calculator", {"expression": "25 * 4"})
        self.assertTrue(res["success"])
        self.assertEqual(res["result"]["result"], 100.0)

        # Empty args test through ToolManager
        calc_empty = await tm.execute_tool("calculator", {})
        self.assertTrue(calc_empty["success"])  # ToolManager caught call
        self.assertFalse(calc_empty["result"]["success"])  # Tool returned error


if __name__ == "__main__":
    unittest.main()
