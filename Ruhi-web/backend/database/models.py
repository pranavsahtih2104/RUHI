import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
# pyrefly: ignore [missing-import]
from sqlalchemy import (
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def current_utc_time() -> datetime:
    return datetime.now(timezone.utc)


class UserModel(Base):
    """
    User entity representing an authenticated or local identity.
    """
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_utc_time, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_utc_time,
        onupdate=current_utc_time,
        nullable=False
    )

    conversations: Mapped[List["ConversationModel"]] = relationship("ConversationModel", back_populates="user", cascade="all, delete-orphan")
    memories: Mapped[List["MemoryModel"]] = relationship("MemoryModel", back_populates="user", cascade="all, delete-orphan")


class ConversationModel(Base):
    """
    Persistent conversational session.
    """
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="New Conversation")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_utc_time, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_utc_time,
        onupdate=current_utc_time,
        nullable=False
    )

    user: Mapped[Optional["UserModel"]] = relationship("UserModel", back_populates="conversations")
    messages: Mapped[List["MessageModel"]] = relationship(
        "MessageModel",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="MessageModel.created_at"
    )

    __table_args__ = (
        Index("idx_conversation_user_created", "user_id", "created_at"),
    )


class MessageModel(Base):
    """
    Individual message turn within a conversation.
    """
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)  # 'user' | 'assistant' | 'system'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_utc_time, nullable=False, index=True)

    conversation: Mapped[Optional["ConversationModel"]] = relationship("ConversationModel", back_populates="messages")

    __table_args__ = (
        Index("idx_message_conv_created", "conversation_id", "created_at"),
    )


class MemoryModel(Base):
    """
    Persistent long-term memory entity for RUHI.
    
    Stores user preferences, facts, goals, project context, and instructions
    that remain active and searchable across multiple conversation sessions.
    """
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    memory_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="general",
        index=True
    )  # 'preference' | 'fact' | 'goal' | 'project' | 'instruction' | 'relationship' | 'event' | 'general'
    importance: Mapped[int] = mapped_column(Integer, nullable=False, default=5)  # 1 to 10 scale
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="explicit")  # 'explicit' | 'extracted' | 'system'
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Prepared for future vector embeddings & tags
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_utc_time, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_utc_time,
        onupdate=current_utc_time,
        nullable=False
    )

    user: Mapped[Optional["UserModel"]] = relationship("UserModel", back_populates="memories")

    __table_args__ = (
        Index("idx_memory_user_type_active", "user_id", "memory_type", "is_active"),
        Index("idx_memory_active_importance", "is_active", "importance"),
    )
