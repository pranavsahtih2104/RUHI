import unittest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.database.models import Base
from backend.services.memory.memory_service import MemoryService
from backend.models.schemas import MemoryCreateRequest, MemoryUpdateRequest


class TestMemoryService(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        self.session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        self.service = MemoryService()
        self.service.session_maker = self.session_maker

    async def asyncTearDown(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await self.engine.dispose()

    def test_explicit_command_detection(self):
        # 1. Remember
        cmd = self.service.detect_explicit_command("Remember that RUHI is my personal AI project")
        self.assertIsNotNone(cmd)
        assert cmd is not None
        self.assertEqual(cmd[0], "remember")
        self.assertEqual(cmd[1], "RUHI is my personal AI project")

        # 2. Forget
        cmd_forget = self.service.detect_explicit_command("Forget that I want desktop control")
        self.assertIsNotNone(cmd_forget)
        assert cmd_forget is not None
        self.assertEqual(cmd_forget[0], "forget")
        self.assertEqual(cmd_forget[1], "I want desktop control")

        # 3. Query
        cmd_query = self.service.detect_explicit_command("What do you remember about my project?")
        self.assertIsNotNone(cmd_query)
        assert cmd_query is not None
        self.assertEqual(cmd_query[0], "query")

        # 4. Normal message
        cmd_none = self.service.detect_explicit_command("Explain how PostgreSQL indexes work")
        self.assertIsNone(cmd_none)

    def test_conservative_extraction(self):
        # Should extract strong enduring preference
        ext_pref = self.service.extract_conservative_memory("I prefer dark mode in all user interfaces.")
        self.assertIsNotNone(ext_pref)
        assert ext_pref is not None
        self.assertEqual(ext_pref[1], "preference")

        # Should extract project intent
        ext_proj = self.service.extract_conservative_memory("I am building an autonomous personal AI system.")
        self.assertIsNotNone(ext_proj)
        assert ext_proj is not None
        self.assertEqual(ext_proj[1], "project")

        # Should NOT extract ephemeral chatter
        ext_transient = self.service.extract_conservative_memory("I drank a cup of black coffee today.")
        self.assertIsNone(ext_transient)

        ext_short = self.service.extract_conservative_memory("Hello there")
        self.assertIsNone(ext_short)

    async def test_save_and_retrieve_explicit_memory(self):
        # Save memory
        event = await self.service.save_explicit_memory("RUHI is my personal AI project", user_id="test_user")
        self.assertEqual(event.operation, "created")
        self.assertIn("RUHI is my personal AI project", event.summary)

        # Retrieve with relevant query
        retrieved = await self.service.retrieve_relevant_memories("Tell me about my RUHI project", user_id="test_user")
        self.assertGreaterEqual(len(retrieved), 1)
        self.assertIn("RUHI is my personal AI project", retrieved[0].content)

        # Retrieve with unrelated query -> should return empty
        unrelated = await self.service.retrieve_relevant_memories("How is the weather in Tokyo?", user_id="test_user")
        self.assertEqual(len(unrelated), 0)

    async def test_forget_memory(self):
        await self.service.save_explicit_memory("I want RUHI to have desktop automation", user_id="user_1")
        
        # Verify it is retrieved
        res1 = await self.service.retrieve_relevant_memories("desktop automation", user_id="user_1")
        self.assertEqual(len(res1), 1)

        # Forget it
        forget_event = await self.service.forget_memory("desktop automation", user_id="user_1")
        self.assertEqual(forget_event.operation, "forgotten")

        # Verify it is no longer retrieved
        res2 = await self.service.retrieve_relevant_memories("desktop automation", user_id="user_1")
        self.assertEqual(len(res2), 0)

    async def test_crud_endpoints(self):
        created = await self.service.create_memory(
            MemoryCreateRequest(
                content="I prefer concise code examples",
                memory_type="preference",
                importance=8
            )
        )
        self.assertIsNotNone(created.id)

        # Update
        updated = await self.service.update_memory(
            created.id,
            MemoryUpdateRequest(importance=9)
        )
        self.assertIsNotNone(updated)
        assert updated is not None
        self.assertEqual(updated.importance, 9)

        # List
        memories, total = await self.service.list_memories(is_active=True)
        self.assertGreaterEqual(total, 1)

        # Delete
        deleted = await self.service.delete_memory(created.id)
        self.assertTrue(deleted)


if __name__ == "__main__":
    unittest.main()
