import os
import sys
import logging
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Set up logging
logger = logging.getLogger("routes")

# Get the project root directory and add it to the Python path
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Log for debugging
logger.info(f"routes.py - ROOT_DIR: {ROOT_DIR}")
logger.info(f"routes.py - sys.path: {sys.path}")

# Import after adding to path with more resilient error handling
try:
    # Try relative import first (in case we're used as a module)
    try:
        from ..routes import speech
        logger.info("Imported speech using relative import")
    except (ImportError, ValueError):
        # Try absolute import next
        from routes import speech
        logger.info("Imported speech using absolute import")
except Exception as e:
    logger.error(f"Failed to import speech module: {e}")
    # Create a temporary router for speech to avoid breaking the app
    speech = type('obj', (object,), {'router': APIRouter()})
    logger.warning("Using empty speech router as fallback")

router = APIRouter()
# Use absolute path to templates directory
templates = Jinja2Templates(directory=os.path.join(ROOT_DIR, "templates"))

router.include_router(speech.router, tags=["sst"])
