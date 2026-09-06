import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
WORKSPACE_ROOT = PROJECT_ROOT.parent

# Attempt to load .env from priority order
env_paths = [
    BACKEND_DIR / ".env",
    PROJECT_ROOT / ".env",
    WORKSPACE_ROOT / "Ruhi-v0.1" / ".env",
    WORKSPACE_ROOT / ".env",
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        break
else:
    load_dotenv()


class Settings:
    PROJECT_NAME: str = "RUHI AI Core"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # LLM Provider Configuration
    DEFAULT_PROVIDER: str = os.getenv("RUHI_LLM_PROVIDER", "gemini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    FALLBACK_MODEL: str = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.0-flash")

    # PostgreSQL Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://localhost:5432/ruhi-web"
    )
    DEFAULT_USER_ID: str = os.getenv("DEFAULT_USER_ID", "default_user")

    @property
    def async_database_url(self) -> str:
        """Returns PostgreSQL URL formatted for asyncpg (SQLAlchemy Async)."""
        url = self.DATABASE_URL.strip()
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def sync_database_url(self) -> str:
        """Returns PostgreSQL URL formatted for synchronous drivers (Alembic)."""
        url = self.DATABASE_URL.strip()
        if url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
        return url

    # Session & Context Memory Configuration
    MAX_SESSION_HISTORY: int = int(os.getenv("MAX_SESSION_HISTORY", "30"))
    SESSION_EXPIRY_MINUTES: int = int(os.getenv("SESSION_EXPIRY_MINUTES", "120"))

    # CORS Origins
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*",
    ]


settings = Settings()
