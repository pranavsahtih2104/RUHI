"""Initial persistent memory and conversation schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-09-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users table (prepared for future authentication)
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. Conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.String(length=64), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_created_at', 'conversations', ['created_at'], unique=False)
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'], unique=False)
    op.create_index('idx_conversation_user_created', 'conversations', ['user_id', 'created_at'], unique=False)

    # 3. Messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('conversation_id', sa.String(length=64), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'], unique=False)
    op.create_index('ix_messages_created_at', 'messages', ['created_at'], unique=False)
    op.create_index('idx_message_conv_created', 'messages', ['conversation_id', 'created_at'], unique=False)

    # 4. Memories table (long-term persistent memory)
    op.create_table(
        'memories',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.String(length=64), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('memory_type', sa.String(length=64), nullable=False),
        sa.Column('importance', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=64), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_memories_created_at', 'memories', ['created_at'], unique=False)
    op.create_index('ix_memories_is_active', 'memories', ['is_active'], unique=False)
    op.create_index('ix_memories_memory_type', 'memories', ['memory_type'], unique=False)
    op.create_index('ix_memories_user_id', 'memories', ['user_id'], unique=False)
    op.create_index('idx_memory_user_type_active', 'memories', ['user_id', 'memory_type', 'is_active'], unique=False)
    op.create_index('idx_memory_active_importance', 'memories', ['is_active', 'importance'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_memory_active_importance', table_name='memories')
    op.drop_index('idx_memory_user_type_active', table_name='memories')
    op.drop_index('ix_memories_user_id', table_name='memories')
    op.drop_index('ix_memories_memory_type', table_name='memories')
    op.drop_index('ix_memories_is_active', table_name='memories')
    op.drop_index('ix_memories_created_at', table_name='memories')
    op.drop_table('memories')

    op.drop_index('idx_message_conv_created', table_name='messages')
    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_table('messages')

    op.drop_index('idx_conversation_user_created', table_name='conversations')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_index('ix_conversations_created_at', table_name='conversations')
    op.drop_table('conversations')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
