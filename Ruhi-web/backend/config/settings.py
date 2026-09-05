import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Load .env from backend dir, project root, or parent dirs
env_paths = [
    BACKEND_DIR / ".env",
    PROJECT_ROOT / ".env",
    PROJECT_ROOT.parent / "Ruhi-v0.1" / ".env",
    PROJECT_ROOT.parent / ".env",
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        break
else:
    load_dotenv()

class Settings:
    PROJECT_NAME: str = "RUHI AI Backend"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    FALLBACK_MODEL: str = "gemini-2.0-flash"
    
    # Session & Memory
    MAX_SESSION_HISTORY: int = int(os.getenv("MAX_SESSION_HISTORY", "30"))
    SESSION_EXPIRY_MINUTES: int = int(os.getenv("SESSION_EXPIRY_MINUTES", "120"))
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*",
    ]

settings = Settings()
