import logging
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text
from backend.config.settings import settings

logger = logging.getLogger("ruhi.database")

_async_engine: Optional[AsyncEngine] = None
_async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def get_async_engine() -> AsyncEngine:
    """Returns singleton AsyncEngine configured with PostgreSQL asyncpg driver."""
    global _async_engine
    if _async_engine is None:
        db_url = settings.async_database_url
        logger.info(f"Initializing PostgreSQL Async Engine (database: ruhi-web)")
        _async_engine = create_async_engine(
            db_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
    return _async_engine


def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    """Returns singleton async sessionmaker."""
    global _async_session_maker
    if _async_session_maker is None:
        engine = get_async_engine()
        _async_session_maker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _async_session_maker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding transactional async DB sessions."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_database_connection() -> dict:
    """
    Non-blocking health probe for PostgreSQL connectivity.
    Returns status dictionary with connection status and metadata.
    """
    try:
        engine = get_async_engine()
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            val = result.scalar()
            if val == 1:
                return {
                    "connected": True,
                    "database": "ruhi-web",
                    "status": "online",
                    "driver": "asyncpg",
                }
            return {
                "connected": False,
                "database": "ruhi-web",
                "status": "unexpected_result",
                "error": "Query returned unexpected scalar value.",
            }
    except Exception as e:
        logger.warning(f"PostgreSQL connection probe failed: {e}")
        return {
            "connected": False,
            "database": "ruhi-web",
            "status": "disconnected",
            "error": str(e),
        }


async def init_db() -> None:
    """Creates all database tables if they do not exist."""
    from backend.database.models import Base
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("PostgreSQL database tables initialized/verified.")

