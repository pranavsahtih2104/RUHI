import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "Ruhi-web"))
sys.path.insert(0, str(ROOT_DIR / "Ruhi-web" / "backend"))

from backend.main import app
