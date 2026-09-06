import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select, update, delete, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import ConversationModel, MessageModel, UserModel


class ConversationRepository:
    """
    Data access repository for Persistent Conversations and Messages in PostgreSQL.
    """

    @staticmethod
    async def create_conversation(
        session: AsyncSession,
        conversation_id: Optional[str] = None,
        title: str = "New Conversation",
        user_id: Optional[str] = None,
    ) -> ConversationModel:
        cid = conversation_id or str(uuid.uuid4())
        conv = ConversationModel(
            id=cid,
            title=title,
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(conv)
        await session.flush()
        return conv

    @staticmethod
    async def get_conversation(
        session: AsyncSession,
        conversation_id: str
    ) -> Optional[ConversationModel]:
        stmt = select(ConversationModel).where(ConversationModel.id == conversation_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_conversation_with_messages(
        session: AsyncSession,
        conversation_id: str
    ) -> Optional[ConversationModel]:
        stmt = (
            select(ConversationModel)
            .where(ConversationModel.id == conversation_id)
            .options(selectinload(ConversationModel.messages))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_conversations(
        session: AsyncSession,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ConversationModel]:
        stmt = select(ConversationModel)
        if user_id:
            stmt = stmt.where(ConversationModel.user_id == user_id)
        stmt = stmt.order_by(desc(ConversationModel.updated_at)).limit(limit).offset(offset)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_title(
        session: AsyncSession,
        conversation_id: str,
        title: str
    ) -> Optional[ConversationModel]:
        stmt = (
            update(ConversationModel)
            .where(ConversationModel.id == conversation_id)
            .values(title=title, updated_at=datetime.now(timezone.utc))
            .returning(ConversationModel)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def touch_conversation(
        session: AsyncSession,
        conversation_id: str
    ) -> None:
        stmt = (
            update(ConversationModel)
            .where(ConversationModel.id == conversation_id)
            .values(updated_at=datetime.now(timezone.utc))
        )
        await session.execute(stmt)

    @staticmethod
    async def delete_conversation(
        session: AsyncSession,
        conversation_id: str
    ) -> bool:
        stmt = delete(ConversationModel).where(ConversationModel.id == conversation_id)
        result = await session.execute(stmt)
        rowcount = getattr(result, "rowcount", 0) or 0
        return rowcount > 0

    @staticmethod
    async def add_message(
        session: AsyncSession,
        conversation_id: str,
        role: str,
        content: str,
        metadata_json: Optional[dict] = None,
    ) -> MessageModel:
        msg = MessageModel(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata_json=metadata_json,
            created_at=datetime.now(timezone.utc),
        )
        session.add(msg)
        await session.flush()
        await ConversationRepository.touch_conversation(session, conversation_id)
        return msg

    @staticmethod
    async def get_recent_messages(
        session: AsyncSession,
        conversation_id: str,
        limit: int = 30
    ) -> List[MessageModel]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at.asc())
        )
        result = await session.execute(stmt)
        messages = list(result.scalars().all())
        if len(messages) > limit:
            return messages[-limit:]
        return messages
