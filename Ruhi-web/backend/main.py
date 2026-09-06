import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add project root to sys.path to enable clean imports
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import settings
from backend.api.chat import router as chat_router
from backend.api.health import router as health_router
from backend.api.tools import router as tools_router
from backend.api.conversations import router as conversations_router
from backend.api.memories import router as memories_router
from backend.database.connection import check_database_connection, init_db

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ruhi.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler verifying database connectivity on startup."""
    logger.info("Starting RUHI AI Core backend...")
    db_probe = await check_database_connection()
    if db_probe.get("connected"):
        logger.info(f"Connected to PostgreSQL database '{db_probe.get('database')}' successfully.")
        try:
            await init_db()
        except Exception as e:
            logger.warning(f"Database auto-migration warning: {e}")
    else:
        logger.warning(
            f"PostgreSQL probe status: {db_probe.get('status')} ({db_probe.get('error')}). "
            f"Ensure PostgreSQL is configured correctly in .env."
        )
    yield
    logger.info("Shutting down RUHI AI Core backend.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="RUHI AI Core — Personal AI Engine with Persistent PostgreSQL Memory",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(health_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(memories_router, prefix="/api")
app.include_router(tools_router, prefix="/api")


@app.get("/")
async def root_endpoint():
    """Root endpoint for RUHI Core backend."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "http://127.0.0.1:8000/docs",
        "health_check_url": "http://127.0.0.1:8000/api/health",
        "chat_url": "http://127.0.0.1:8000/api/chat",
        "conversations_url": "http://127.0.0.1:8000/api/conversations",
        "memories_url": "http://127.0.0.1:8000/api/memories",
        "message": "RUHI AI Core is operational with persistent PostgreSQL memory."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
