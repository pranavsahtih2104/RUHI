import logging
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_async_session_maker
from backend.database.repositories.conversation_repo import ConversationRepository
from backend.models.schemas import (
    ChatMessage,
    ConversationSummary,
    ConversationDetail,
)

logger = logging.getLogger("ruhi.services.conversation")


class ConversationService:
    """
    Service managing persistent conversations and message history in PostgreSQL.
    """

    def __init__(self):
        self.session_maker = get_async_session_maker()

    async def ensure_conversation(
        self,
        conversation_id: Optional[str] = None,
        title: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Ensures a conversation exists in PostgreSQL. Creates one if not found.
        Returns the conversation ID.
        """
        cid = conversation_id or f"conv_{uuid.uuid4().hex[:12]}"
        async with self.session_maker() as session:
            existing = await ConversationRepository.get_conversation(session, cid)
            if not existing:
                default_title = title or "New Conversation"
                await ConversationRepository.create_conversation(
                    session=session,
                    conversation_id=cid,
                    title=default_title,
                    user_id=user_id,
                )
                await session.commit()
                logger.info(f"Created new persistent conversation: '{cid}' ('{default_title}')")
            return cid

    async def get_history(
        self,
        conversation_id: str,
        limit: int = 30
    ) -> List[ChatMessage]:
        """
        Loads recent conversation history from PostgreSQL.
        """
        async with self.session_maker() as session:
            db_messages = await ConversationRepository.get_recent_messages(
                session=session,
                conversation_id=conversation_id,
                limit=limit
            )
            return [
                ChatMessage(
                    id=m.id,
                    role=m.role,
                    content=m.content,
                    timestamp=m.created_at.isoformat(),
                    metadata=m.metadata_json,
                )
                for m in db_messages
            ]

    async def add_turn(
        self,
        conversation_id: str,
        user_text: str,
        assistant_text: str,
        user_metadata: Optional[dict] = None,
        assistant_metadata: Optional[dict] = None,
    ) -> None:
        """
        Persists a complete conversational turn (User message + Assistant response) to PostgreSQL.
        """
        async with self.session_maker() as session:
            await self.ensure_conversation(conversation_id)
            # Save User message
            await ConversationRepository.add_message(
                session=session,
                conversation_id=conversation_id,
                role="user",
                content=user_text,
                metadata_json=user_metadata,
            )
            # Save Assistant message
            await ConversationRepository.add_message(
                session=session,
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_text,
                metadata_json=assistant_metadata,
            )
            await session.commit()

    async def list_conversations(
        self,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ConversationSummary]:
        """
        Lists all persistent conversations with last message preview and message count.
        """
        async with self.session_maker() as session:
            convs = await ConversationRepository.list_conversations(
                session=session,
                user_id=user_id,
                limit=limit,
                offset=offset,
            )
            summaries = []
            for c in convs:
                recent = await ConversationRepository.get_recent_messages(session, c.id, limit=1)
                last_preview = recent[-1].content[:80] + "..." if recent else None
                all_msgs = await ConversationRepository.get_recent_messages(session, c.id, limit=500)
                summaries.append(
                    ConversationSummary(
                        id=c.id,
                        title=c.title,
                        user_id=c.user_id,
                        created_at=c.created_at.isoformat(),
                        updated_at=c.updated_at.isoformat(),
                        message_count=len(all_msgs),
                        last_message_preview=last_preview,
                    )
                )
            return summaries

    async def get_conversation_detail(
        self,
        conversation_id: str
    ) -> Optional[ConversationDetail]:
        """
        Loads a single conversation along with all its messages.
        """
        async with self.session_maker() as session:
            conv = await ConversationRepository.get_conversation_with_messages(
                session=session,
                conversation_id=conversation_id
            )
            if not conv:
                return None
            return ConversationDetail(
                id=conv.id,
                title=conv.title,
                user_id=conv.user_id,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                messages=[
                    ChatMessage(
                        id=m.id,
                        role=m.role,
                        content=m.content,
                        timestamp=m.created_at.isoformat(),
                        metadata=m.metadata_json,
                    )
                    for m in conv.messages
                ],
            )

    async def update_title(
        self,
        conversation_id: str,
        title: str
    ) -> bool:
        """
        Renames a conversation title in PostgreSQL.
        """
        async with self.session_maker() as session:
            res = await ConversationRepository.update_title(session, conversation_id, title)
            await session.commit()
            return res is not None

    async def delete_conversation(
        self,
        conversation_id: str
    ) -> bool:
        """
        Deletes a conversation and its messages from PostgreSQL.
        """
        async with self.session_maker() as session:
            res = await ConversationRepository.delete_conversation(session, conversation_id)
            await session.commit()
            return res


conversation_service = ConversationService()
