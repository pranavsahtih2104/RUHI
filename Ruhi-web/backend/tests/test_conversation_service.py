import unittest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.database.models import Base
from backend.database.repositories.conversation_repo import ConversationRepository
from backend.services.memory.conversation_service import ConversationService


class TestConversationService(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Create an isolated in-memory test database
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        self.session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        self.service = ConversationService()
        self.service.session_maker = self.session_maker

    async def asyncTearDown(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await self.engine.dispose()

    async def test_ensure_conversation(self):
        cid = await self.service.ensure_conversation(title="Test Project Discussion")
        self.assertIsNotNone(cid)

        # Retrieve and verify
        detail = await self.service.get_conversation_detail(cid)
        self.assertIsNotNone(detail)
        assert detail is not None
        self.assertEqual(detail.title, "Test Project Discussion")
        self.assertEqual(len(detail.messages), 0)

    async def test_add_turn_and_history(self):
        cid = await self.service.ensure_conversation(title="Turn Test")
        await self.service.add_turn(
            conversation_id=cid,
            user_text="What is RUHI?",
            assistant_text="RUHI is your personal AI system."
        )

        history = await self.service.get_history(cid)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].role, "user")
        self.assertEqual(history[0].content, "What is RUHI?")
        self.assertEqual(history[1].role, "assistant")
        self.assertEqual(history[1].content, "RUHI is your personal AI system.")

    async def test_list_and_rename_and_delete(self):
        cid = await self.service.ensure_conversation(title="Old Title")
        await self.service.add_turn(cid, "Hello", "Hi there")

        # List
        summaries = await self.service.list_conversations()
        self.assertGreaterEqual(len(summaries), 1)
        self.assertEqual(summaries[0].id, cid)
        self.assertEqual(summaries[0].message_count, 2)

        # Rename
        updated = await self.service.update_title(cid, "New Architectural Title")
        self.assertTrue(updated)
        detail = await self.service.get_conversation_detail(cid)
        self.assertIsNotNone(detail)
        assert detail is not None
        self.assertEqual(detail.title, "New Architectural Title")

        # Delete
        deleted = await self.service.delete_conversation(cid)
        self.assertTrue(deleted)
        self.assertIsNone(await self.service.get_conversation_detail(cid))


if __name__ == "__main__":
    unittest.main()
