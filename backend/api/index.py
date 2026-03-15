# Vercel serverless entry point
# Vercel looks for a handler in api/ directory
import sys
import os

# Add backend root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app  # noqa: F401 — Vercel uses 'app' as the ASGI handler
