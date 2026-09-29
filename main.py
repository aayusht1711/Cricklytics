import sys
import os

# Add backend directory to sys.path so 'app' and 'ai_engine' resolve correctly from any cwd
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app

__all__ = ["app"]
