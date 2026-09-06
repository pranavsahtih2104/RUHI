import logging
import re
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_async_session_maker
from backend.database.repositories.memory_repo import MemoryRepository
from backend.database.models import MemoryModel
from backend.models.schemas import (
    MemorySchema,
    MemoryCreateRequest,
    MemoryUpdateRequest,
    MemoryOperationEvent,
)

logger = logging.getLogger("ruhi.services.memory")

# Stop words to ignore during keyword extraction for retrieval
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "in", "on", "at", "to", "for",
    "with", "about", "by", "of", "and", "or", "but", "so", "it", "this", "that",
    "what", "how", "why", "who", "where", "when", "can", "could", "would", "should",
    "do", "does", "did", "have", "has", "had", "my", "your", "his", "her", "their",
    "our", "me", "you", "him", "them", "us", "i", "we", "tell", "show", "give",
    "explain", "help", "please", "thanks", "hello", "hi", "hey"
}


class MemoryService:
    """
    Core Persistent Memory Service for RUHI.
    
    Handles:
    - Explicit memory commands ("Remember that...", "Forget that...")
    - Conservative automatic memory extraction (preferences, facts, goals, projects)
    - Structured keyword and relevance retrieval for context injection
    - Full CRUD and lifecycle management in PostgreSQL
    - Vector memory preparation (pgvector schema readiness)
    """

    def __init__(self):
        self.session_maker = get_async_session_maker()

    # -------------------------------------------------------------------------
    # Explicit Memory Intent Detection
    # -------------------------------------------------------------------------

    def detect_explicit_command(self, user_message: str) -> Optional[Tuple[str, str]]:
        """
        Detects if the message is an explicit memory command.
        Returns Tuple[command_type, target_payload] or None.
        
        command_type: 'remember' | 'forget' | 'query'
        """
        clean = user_message.strip()
        lower = clean.lower()

        # 1. "Remember that ..." / "Remember: ..." / "Please remember ..."
        rem_patterns = [
            r"^(?:please\s+)?remember\s+(?:that\s+)?(.+)$",
            r"^(?:please\s+)?remember\s*:\s*(.+)$",
            r"^keep\s+in\s+mind\s+(?:that\s+)?(.+)$",
            r"^note\s+(?:that\s+)?(.+)$",
        ]
        for pat in rem_patterns:
            m = re.match(pat, lower)
            if m:
                # Extract actual substring from original case
                prefix_len = len(clean) - len(clean[m.start(1):])
                payload = clean[prefix_len:].strip()
                if payload:
                    return ("remember", payload)

        # 2. "Forget that ..." / "Forget about ..." / "Remove memory ..." / "Forget my ..."
        forget_patterns = [
            r"^(?:please\s+)?forget\s+(?:that\s+|about\s+)?(.+)$",
            r"^(?:please\s+)?delete\s+(?:the\s+)?memory\s+(?:about\s+|that\s+)?(.+)$",
            r"^(?:please\s+)?remove\s+(?:the\s+)?memory\s+(?:about\s+|that\s+)?(.+)$",
            r"^(?:please\s+)?forget\s+it\.?$",
        ]
        for pat in forget_patterns:
            m = re.match(pat, lower)
            if m:
                if m.groups() and m.group(1):
                    prefix_len = len(clean) - len(clean[m.start(1):])
                    payload = clean[prefix_len:].strip()
                else:
                    payload = "last"
                return ("forget", payload)

        # 3. "What do you remember about ..." / "Show my memories"
        query_patterns = [
            r"^(?:what\s+do\s+you\s+remember\s+(?:about\s+)?)(.+)$",
            r"^(?:what\s+are\s+my\s+saved\s+memories\??)$",
            r"^(?:show\s+(?:all\s+)?(?:my\s+)?memories\??)$",
            r"^(?:list\s+(?:my\s+)?memories\??)$",
        ]
        for pat in query_patterns:
            m = re.match(pat, lower)
            if m:
                payload = m.group(1).strip() if m.groups() and m.group(1) else "all"
                return ("query", payload)

        return None

    # -------------------------------------------------------------------------
    # Conservative Memory Classification & Extraction
    # -------------------------------------------------------------------------

    def classify_memory_type(self, text: str) -> Tuple[str, int]:
        """
        Classifies memory category and baseline importance score (1-10).
        """
        lower = text.lower()

        if any(k in lower for k in ["i prefer", "my preference", "i like", "i dislike", "i hate", "i love", "my favorite"]):
            return ("preference", 7)
        if any(k in lower for k in ["project", "building", "developing", "codebase", "architecture", "ruhi"]):
            return ("project", 8)
        if any(k in lower for k in ["goal", "aim to", "plan to", "want to eventually", "aspire"]):
            return ("goal", 8)
        if any(k in lower for k in ["always", "never", "instruction", "format as", "speak in", "rule"]):
            return ("instruction", 9)
        if any(k in lower for k in ["my name is", "i live in", "i work as", "my role is", "i am a"]):
            return ("fact", 8)
        
        return ("general", 6)

    def extract_conservative_memory(self, user_message: str) -> Optional[Tuple[str, str, int]]:
        """
        Conservative heuristic extractor for normal conversation.
        Only extracts high-confidence enduring information without saving ephemeral talk.
        Returns Optional[Tuple[content, memory_type, importance]].
        """
        clean = user_message.strip()
        lower = clean.lower()

        # Reject trivial messages / greetings / queries
        if len(clean) < 15 or len(clean.split()) < 4:
            return None
        if lower.endswith("?") or lower.startswith(("can you", "what is", "how do", "why is", "tell me", "explain")):
            return None

        # Detect clear enduring statements
        preference_match = re.search(r"\b(i\s+prefer\s+[^.,;]+|i\s+always\s+use\s+[^.,;]+)\b", lower)
        if preference_match:
            return (clean, "preference", 7)

        project_match = re.search(r"\b(i\s+am\s+building\s+[^.,;]+|i'm\s+building\s+[^.,;]+|my\s+project\s+is\s+[^.,;]+)\b", lower)
        if project_match:
            return (clean, "project", 8)

        goal_match = re.search(r"\b(my\s+goal\s+is\s+to\s+[^.,;]+|i\s+want\s+to\s+eventually\s+[^.,;]+)\b", lower)
        if goal_match:
            return (clean, "goal", 8)

        fact_match = re.search(r"\b(my\s+name\s+is\s+[^.,;]+|i\s+work\s+as\s+a\s+[^.,;]+)\b", lower)
        if fact_match:
            return (clean, "fact", 8)

        return None

    # -------------------------------------------------------------------------
    # Core Operations
    # -------------------------------------------------------------------------

    async def save_explicit_memory(
        self,
        content: str,
        user_id: Optional[str] = None
    ) -> MemoryOperationEvent:
        """
        Saves an explicit memory in PostgreSQL with high importance.
        """
        mem_type, base_importance = self.classify_memory_type(content)
        importance = max(8, base_importance)  # Explicit memories receive high importance

        async with self.session_maker() as session:
            # Check for existing duplicate active memory
            existing = await MemoryRepository.find_matching_memories(session, content, user_id=user_id, limit=1)
            if existing and existing[0].content.lower() == content.lower():
                # Update importance/timestamp
                mem = await MemoryRepository.update_memory(
                    session=session,
                    memory_id=existing[0].id,
                    importance=importance,
                    is_active=True
                )
                await session.commit()
                assert mem is not None
                return MemoryOperationEvent(
                    operation="updated",
                    memory_id=mem.id,
                    content=mem.content,
                    memory_type=mem.memory_type,
                    summary=f"Updated existing memory: '{mem.content}'",
                )

            mem = await MemoryRepository.create_memory(
                session=session,
                content=content,
                memory_type=mem_type,
                importance=importance,
                source="explicit",
                user_id=user_id,
            )
            await session.commit()
            logger.info(f"Saved explicit memory: [{mem_type.upper()}] '{content}' (id: {mem.id})")

            return MemoryOperationEvent(
                operation="created",
                memory_id=mem.id,
                content=mem.content,
                memory_type=mem.memory_type,
                summary=f"Remembered: '{mem.content}'",
            )

    async def forget_memory(
        self,
        target_phrase: str,
        user_id: Optional[str] = None
    ) -> MemoryOperationEvent:
        """
        Deactivates active memories matching target phrase.
        """
        async with self.session_maker() as session:
            matches = await MemoryRepository.find_matching_memories(
                session=session,
                search_phrase=target_phrase,
                user_id=user_id,
                limit=3
            )

            if not matches:
                # If no direct match, check all active memories to see if recent
                all_active = await MemoryRepository.list_memories(session, user_id=user_id, is_active=True, limit=1)
                if all_active and target_phrase in ("last", "that", "it"):
                    matches = all_active

            if not matches:
                return MemoryOperationEvent(
                    operation="forgotten",
                    summary="No matching active memory found to forget.",
                )

            forgotten_contents = []
            for m in matches:
                await MemoryRepository.delete_memory(session, m.id, hard_delete=False)
                forgotten_contents.append(m.content)

            await session.commit()
            summary_text = f"Removed {len(matches)} memory: " + "; ".join(f"'{c}'" for c in forgotten_contents)
            logger.info(f"Deactivated memories: {summary_text}")

            return MemoryOperationEvent(
                operation="forgotten",
                memory_id=matches[0].id,
                content=matches[0].content,
                summary=summary_text,
            )

    async def retrieve_relevant_memories(
        self,
        query_text: str,
        user_id: Optional[str] = None,
        max_memories: int = 4
    ) -> List[MemorySchema]:
        """
        Retrieves top relevant active memories for a given query text.
        Filters out stop words, queries keywords and phrases, and ranks by relevance/importance.
        """
        tokens = re.findall(r"\b[a-zA-Z0-9_-]+\b", query_text.lower())
        keywords = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]

        async with self.session_maker() as session:
            candidate_map: Dict[str, MemoryModel] = {}

            # 1. Search by extracted keywords
            if keywords:
                kw_results = await MemoryRepository.search_memories_keyword(
                    session=session,
                    keywords=keywords,
                    user_id=user_id,
                    limit=max_memories * 2
                )
                for m in kw_results:
                    candidate_map[m.id] = m

            # 2. Search by key phrases if specific
            phrase_results = await MemoryRepository.find_matching_memories(
                session=session,
                search_phrase=query_text,
                user_id=user_id,
                limit=max_memories
            )
            for m in phrase_results:
                candidate_map[m.id] = m

            # If no matches, return empty
            if not candidate_map:
                return []

            # Score and rank candidates
            scored = []
            for mem in candidate_map.values():
                score = mem.importance * 2
                content_lower = mem.content.lower()
                # Keyword hits boost score
                match_count = sum(1 for kw in keywords if kw in content_lower)
                score += match_count * 3
                scored.append((score, mem))

            scored.sort(key=lambda x: x[0], reverse=True)
            top_memories = [item[1] for item in scored[:max_memories]]

            return [self._to_schema(m) for m in top_memories]

    # -------------------------------------------------------------------------
    # CRUD API Methods
    # -------------------------------------------------------------------------

    async def list_memories(
        self,
        user_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = True,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[MemorySchema], int]:
        async with self.session_maker() as session:
            db_memories = await MemoryRepository.list_memories(
                session=session,
                user_id=user_id,
                memory_type=memory_type,
                is_active=is_active,
                search_query=search,
                limit=limit,
                offset=offset,
            )
            all_for_count = await MemoryRepository.list_memories(
                session=session,
                user_id=user_id,
                memory_type=memory_type,
                is_active=is_active,
                search_query=search,
                limit=5000,
            )
            return [self._to_schema(m) for m in db_memories], len(all_for_count)

    async def get_memory(self, memory_id: str) -> Optional[MemorySchema]:
        async with self.session_maker() as session:
            mem = await MemoryRepository.get_memory(session, memory_id)
            return self._to_schema(mem) if mem else None

    async def create_memory(self, payload: MemoryCreateRequest) -> MemorySchema:
        async with self.session_maker() as session:
            mem = await MemoryRepository.create_memory(
                session=session,
                content=payload.content,
                memory_type=payload.memory_type,
                importance=payload.importance,
                source=payload.source,
                user_id=payload.user_id,
            )
            await session.commit()
            return self._to_schema(mem)

    async def update_memory(self, memory_id: str, payload: MemoryUpdateRequest) -> Optional[MemorySchema]:
        async with self.session_maker() as session:
            mem = await MemoryRepository.update_memory(
                session=session,
                memory_id=memory_id,
                content=payload.content,
                memory_type=payload.memory_type,
                importance=payload.importance,
                is_active=payload.is_active,
            )
            await session.commit()
            return self._to_schema(mem) if mem else None

    async def delete_memory(self, memory_id: str, hard_delete: bool = False) -> bool:
        async with self.session_maker() as session:
            res = await MemoryRepository.delete_memory(session, memory_id, hard_delete=hard_delete)
            await session.commit()
            return res

    def _to_schema(self, m: MemoryModel) -> MemorySchema:
        return MemorySchema(
            id=m.id,
            user_id=m.user_id,
            content=m.content,
            memory_type=m.memory_type,
            importance=m.importance,
            source=m.source,
            is_active=m.is_active,
            metadata=m.metadata_json,
            created_at=m.created_at.isoformat(),
            updated_at=m.updated_at.isoformat(),
        )


memory_service = MemoryService()
