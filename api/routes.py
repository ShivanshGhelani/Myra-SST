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
    # Try direct import since we added ROOT_DIR to sys.path
    import sys
    from routes.speech import router as speech_router
    logger.info("Imported speech_router directly")
    speech = type('obj', (object,), {'router': speech_router})
except Exception as e:
    logger.error(f"Failed to import speech module: {e}")
    logger.error(f"sys.path: {sys.path}")
    # Create a temporary router for speech to avoid breaking the app
    speech = type('obj', (object,), {'router': APIRouter()})
    logger.warning("Using empty speech router as fallback")

router = APIRouter()
# Use absolute path to templates directory
templates = Jinja2Templates(directory=os.path.join(ROOT_DIR, "templates"))

# Add a test endpoint to verify routing works
@router.get("/test")
async def test_endpoint():
    # Get the routes from the speech router
    speech_routes = []
    if hasattr(speech, 'router') and hasattr(speech.router, 'routes'):
        speech_routes = [f"{route.methods} {route.path}" for route in speech.router.routes]
    
    return {
        "message": "Router is working", 
        "speech_router_included": hasattr(speech, 'router'),
        "speech_routes": speech_routes,
        "speech_router_type": str(type(speech.router)) if hasattr(speech, 'router') else "None"
    }

router.include_router(speech.router, tags=["sst"])
