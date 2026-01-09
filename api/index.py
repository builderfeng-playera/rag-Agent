"""
Vercel serverless function wrapper for FastAPI app
"""
import sys
import os
from pathlib import Path

# Add parent directory to path so we can import app
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Change to parent directory so file paths work correctly
os.chdir(parent_dir)

# Import app - this will trigger startup events
from app import app

# Vercel's @vercel/python runtime automatically handles ASGI apps
# Just expose the app instance
handler = app
