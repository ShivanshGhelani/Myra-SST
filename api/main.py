import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("myra-stt")

# Print debug info
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"ROOT_DIR: {ROOT_DIR}")

# Try to load environment variables only if the package is available
# This avoids import errors in environments where dotenv isn't available
env_vars_loaded = False
try:
    # Only attempt to import dotenv if it's installed
    try:
        from dotenv import load_dotenv
        load_dotenv()
        env_vars_loaded = True
        logger.info("Environment variables loaded from .env")
    except ImportError:
        logger.info("python-dotenv not installed, skipping .env loading")
except Exception as e:
    logger.warning(f"Error loading environment variables: {str(e)}")

# Now import router after setting up paths
try:
    from api.routes import router
except ImportError as e:
    print(f"Failed to import router: {str(e)}")
    # Fallback to direct import
    try:
        import api.routes
        router = api.routes.router
    except Exception as e2:
        print(f"Fallback import also failed: {str(e2)}")
        raise

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("myra-stt")

# Configure for Vercel deployment
app = FastAPI(
    title="MyraSTT API",
    description="Speech to Text API",
    version="1.0.0",
    root_path=os.getenv("ROOT_PATH", ""),
    # Ensure we get proper error reports
    debug=True
)

# Add CORS middlewaresti
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Mount static directories with error handling
try:
    static_path = os.path.join(ROOT_DIR, "static")
    templates_path = os.path.join(ROOT_DIR, "templates")
    
    # Log the paths for debugging
    logger.info(f"Static path: {static_path}")
    logger.info(f"Templates path: {templates_path}")
    
    # Check if directories exist
    if os.path.isdir(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
        logger.info("Static directory mounted successfully")
    else:
        logger.warning(f"Static directory not found at: {static_path}")
    
    if os.path.isdir(templates_path):
        app.mount("/templates", StaticFiles(directory=templates_path), name="templates")
        logger.info("Templates directory mounted successfully")
    else:
        logger.warning(f"Templates directory not found at: {templates_path}")
except Exception as e:
    logger.error(f"Error mounting static directories: {str(e)}")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(static_path, "SVG", "bot.svg"))

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        template_path = os.path.join(templates_path, "sst_core.html")
        logger.info(f"Reading template from: {template_path}")
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except Exception as e:
        error_message = f"Error reading template: {str(e)}"
        logger.error(error_message)
        return HTMLResponse(
            content=f"<html><body><h1>Error</h1><p>{error_message}</p></body></html>",
            status_code=500
        )


@app.get("/debug")
async def debug_info():
    """Endpoint to debug server environment and paths"""
    debug_info = {
        "env": dict(os.environ),
        "cwd": os.getcwd(),
        "root_dir": str(ROOT_DIR),
        "static_path_exists": os.path.isdir(static_path),
        "templates_path_exists": os.path.isdir(templates_path),
        "static_files": os.listdir(static_path) if os.path.isdir(static_path) else [],
        "template_files": os.listdir(templates_path) if os.path.isdir(templates_path) else []
    }
    return debug_info


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return HTMLResponse(
        content=f"<html><body><h1>Server Error</h1><p>An error occurred on the server. Please try again later.</p><p>Error: {str(exc)}</p></body></html>",
        status_code=500
    )


def create_app():
    return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:create_app()", host="0.0.0.0", port=8000, reload=True)
