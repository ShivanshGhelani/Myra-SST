import os
import sys
import logging
import traceback

# Configure basic logging first thing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("vercel-entry")

# Try to provide as much diagnostic info as possible
try:
    # Log the environment
    logger.info("Starting application in Vercel environment")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Initial sys.path: {sys.path}")
    
    # Add the current directory to Python path if not already there
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        logger.info(f"Added {current_dir} to sys.path")
    
    # Show directory structure for debugging
    try:
        root_files = os.listdir(current_dir)
        logger.info(f"Files in root directory: {root_files}")
        
        # Check if api directory exists
        api_dir = os.path.join(current_dir, "api")
        if os.path.isdir(api_dir):
            api_files = os.listdir(api_dir)
            logger.info(f"Files in api directory: {api_files}")
    except Exception as dir_err:
        logger.error(f"Error listing directory contents: {dir_err}")
    
    # Now try to import the app
    try:
        # First try direct import
        from api.main import app
        logger.info("Successfully imported app from api.main")
    except ImportError as import_err:
        logger.error(f"Direct import failed: {import_err}")
        
        # Try alternative approaches
        try:
            import api
            logger.info("Imported api module")
            from api.main import app
            logger.info("Successfully imported app from api.main after importing api")
        except Exception as alt_err:
            logger.error(f"Alternative import approach failed: {alt_err}")
            raise  # Re-raise to trigger the fallback
    
except Exception as e:
    logger.error(f"Error in index.py: {str(e)}")
    logger.error(traceback.format_exc())
    
    # Create a simple FastAPI app for debugging
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return {
            "error": f"Failed to import main application: {str(e)}",
            "traceback": traceback.format_exc(),
            "python_path": sys.path,
            "cwd": os.getcwd(),
            "files_in_cwd": os.listdir(os.getcwd()) if os.path.exists(os.getcwd()) else []
        }

# This file serves as the entry point for Vercel
# Export the app variable for Vercel to use