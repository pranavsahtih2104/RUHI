import unittest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.database.models import Base
from backend.services.memory.conversation_service import conversation_service
from backend.services.memory.memory_service import memory_service
from backend.core.ruhi_core import ruhi_core
from backend.services.llm.base import BaseLLMProvider
from backend.models.schemas import ChatMessage
from backend.main import app
from typing import List, Optional, Any


class MockLLM(BaseLLMProvider):
    async def generate_response(
        self,
        history: List[ChatMessage],
        new_message: str,
        system_instruction: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        return f"Mock answer for: {new_message}"

    def stream_response(self, history, new_message, system_instruction=None, **kwargs):
        async def _gen():
            yield "Mock answer"
        return _gen()

    def get_provider_name(self):
        return "Mock LLM"

    def is_configured(self):
        return True


class TestAPIEndpoints(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        self.session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        conversation_service.session_maker = self.session_maker
        memory_service.session_maker = self.session_maker
        ruhi_core.conversation_service = conversation_service
        ruhi_core.memory_service = memory_service
        ruhi_core.llm_provider = MockLLM()

        self.client = TestClient(app)

    async def asyncTearDown(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await self.engine.dispose()

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["service"], "RUHI AI Core")
        self.assertIn("status", data)

    def test_conversation_api_lifecycle(self):
        # 1. Create Conversation
        create_res = self.client.post("/api/conversations", json={"title": "Test Chat"})
        self.assertEqual(create_res.status_code, 201)
        conv = create_res.json()
        cid = conv["id"]
        self.assertEqual(conv["title"], "Test Chat")

        # 2. List Conversations
        list_res = self.client.get("/api/conversations")
        self.assertEqual(list_res.status_code, 200)
        convs = list_res.json()
        self.assertGreaterEqual(len(convs), 1)

        # 3. Rename
        rename_res = self.client.patch(f"/api/conversations/{cid}", json={"title": "Updated Chat Title"})
        self.assertEqual(rename_res.status_code, 200)

        # 4. Get Detail
        detail_res = self.client.get(f"/api/conversations/{cid}")
        self.assertEqual(detail_res.status_code, 200)
        self.assertEqual(detail_res.json()["title"], "Updated Chat Title")

        # 5. Delete
        del_res = self.client.delete(f"/api/conversations/{cid}")
        self.assertEqual(del_res.status_code, 200)

    def test_memory_api_lifecycle(self):
        # 1. Create Memory
        create_res = self.client.post(
            "/api/memories",
            json={
                "content": "User prefers concise architectural breakdowns",
                "memory_type": "preference",
                "importance": 8
            }
        )
        self.assertEqual(create_res.status_code, 201)
        mem = create_res.json()
        mid = mem["id"]
        self.assertEqual(mem["content"], "User prefers concise architectural breakdowns")

        # 2. List Memories
        list_res = self.client.get("/api/memories")
        self.assertEqual(list_res.status_code, 200)
        self.assertEqual(list_res.json()["total"], 1)

        # 3. Search Memories
        search_res = self.client.get("/api/memories?search=concise")
        self.assertEqual(search_res.status_code, 200)
        self.assertEqual(search_res.json()["total"], 1)

        # 4. Update Memory
        patch_res = self.client.patch(f"/api/memories/{mid}", json={"importance": 9})
        self.assertEqual(patch_res.status_code, 200)
        self.assertEqual(patch_res.json()["importance"], 9)

        # 5. Delete Memory
        del_res = self.client.delete(f"/api/memories/{mid}")
        self.assertEqual(del_res.status_code, 200)

    def test_chat_endpoint_persistence(self):
        res = self.client.post("/api/chat", json={"message": "Hello RUHI Core", "session_id": "test_conv_api"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["session_id"], "test_conv_api")
        self.assertIn("Mock answer for: Hello RUHI Core", data["message"])


if __name__ == "__main__":
    unittest.main()
