import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, desc, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import MemoryModel


class MemoryRepository:
    """
    Data access repository for Persistent Long-Term Memories in PostgreSQL.
    """

    @staticmethod
    async def create_memory(
        session: AsyncSession,
        content: str,
        memory_type: str = "general",
        importance: int = 5,
        source: str = "explicit",
        user_id: Optional[str] = None,
        metadata_json: Optional[dict] = None,
    ) -> MemoryModel:
        mem = MemoryModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            content=content.strip(),
            memory_type=memory_type.lower().strip(),
            importance=max(1, min(10, importance)),
            source=source.lower().strip(),
            is_active=True,
            metadata_json=metadata_json,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(mem)
        await session.flush()
        return mem

    @staticmethod
    async def get_memory(
        session: AsyncSession,
        memory_id: str
    ) -> Optional[MemoryModel]:
        stmt = select(MemoryModel).where(MemoryModel.id == memory_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_memories(
        session: AsyncSession,
        user_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        is_active: Optional[bool] = True,
        search_query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[MemoryModel]:
        stmt = select(MemoryModel)
        conditions = []

        if user_id:
            conditions.append(MemoryModel.user_id == user_id)
        if is_active is not None:
            conditions.append(MemoryModel.is_active == is_active)
        if memory_type and memory_type.lower() != "all":
            conditions.append(MemoryModel.memory_type == memory_type.lower().strip())
        if search_query and search_query.strip():
            term = f"%{search_query.strip().lower()}%"
            conditions.append(func.lower(MemoryModel.content).like(term))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(
            desc(MemoryModel.importance),
            desc(MemoryModel.created_at)
        ).limit(limit).offset(offset)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def search_memories_keyword(
        session: AsyncSession,
        keywords: List[str],
        user_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[MemoryModel]:
        """
        Retrieves active memories that match any of the given keywords, ranked by importance.
        """
        if not keywords:
            return []

        stmt = select(MemoryModel).where(MemoryModel.is_active == True)
        if user_id:
            stmt = stmt.where(MemoryModel.user_id == user_id)

        keyword_clauses = [
            func.lower(MemoryModel.content).like(f"%{kw.lower().strip()}%")
            for kw in keywords if len(kw.strip()) > 2
        ]

        if not keyword_clauses:
            return []

        stmt = stmt.where(or_(*keyword_clauses))
        stmt = stmt.order_by(
            desc(MemoryModel.importance),
            desc(MemoryModel.updated_at)
        ).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def find_matching_memories(
        session: AsyncSession,
        search_phrase: str,
        user_id: Optional[str] = None,
        limit: int = 5,
    ) -> List[MemoryModel]:
        """
        Finds active memories matching a phrase or its significant terms.
        """
        clean_phrase = search_phrase.strip().lower()
        if not clean_phrase:
            return []

        stmt = select(MemoryModel).where(MemoryModel.is_active == True)
        if user_id:
            stmt = stmt.where(MemoryModel.user_id == user_id)

        # Match exact phrase or individual significant tokens
        terms = [t for t in clean_phrase.split() if len(t) > 2]
        clauses = [func.lower(MemoryModel.content).like(f"%{clean_phrase}%")]
        for t in terms:
            clauses.append(func.lower(MemoryModel.content).like(f"%{t}%"))

        stmt = stmt.where(or_(*clauses))
        stmt = stmt.order_by(desc(MemoryModel.importance), desc(MemoryModel.created_at)).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_memory(
        session: AsyncSession,
        memory_id: str,
        content: Optional[str] = None,
        memory_type: Optional[str] = None,
        importance: Optional[int] = None,
        is_active: Optional[bool] = None,
        metadata_json: Optional[dict] = None,
    ) -> Optional[MemoryModel]:
        updates: Dict[str, Any] = {"updated_at": datetime.now(timezone.utc)}
        if content is not None:
            updates["content"] = content.strip()
        if memory_type is not None:
            updates["memory_type"] = memory_type.lower().strip()
        if importance is not None:
            updates["importance"] = max(1, min(10, importance))
        if is_active is not None:
            updates["is_active"] = is_active
        if metadata_json is not None:
            updates["metadata_json"] = metadata_json

        stmt = (
            update(MemoryModel)
            .where(MemoryModel.id == memory_id)
            .values(**updates)
            .returning(MemoryModel)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_memory(
        session: AsyncSession,
        memory_id: str,
        hard_delete: bool = False
    ) -> bool:
        if hard_delete:
            stmt = delete(MemoryModel).where(MemoryModel.id == memory_id)
            result = await session.execute(stmt)
            rowcount = getattr(result, "rowcount", 0) or 0
            return rowcount > 0
        else:
            # Soft delete / deactivate
            stmt = (
                update(MemoryModel)
                .where(MemoryModel.id == memory_id)
                .values(is_active=False, updated_at=datetime.now(timezone.utc))
            )
            result = await session.execute(stmt)
            rowcount = getattr(result, "rowcount", 0) or 0
            return rowcount > 0
