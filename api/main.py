from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routes import router  # Use relative import
import os
import logging
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent

# Configure for Vercel deployment
app = FastAPI(
    title="MyraSTT API",
    description="Speech to Text API",
    version="1.0.0",
    root_path=os.getenv("ROOT_PATH", "")
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

# Mount static directories
static_path = os.path.join(ROOT_DIR, "static")
templates_path = os.path.join(ROOT_DIR, "templates")
app.mount("/static", StaticFiles(directory=static_path), name="static")
app.mount("/templates", StaticFiles(directory=templates_path), name="templates")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(static_path, "SVG", "bot.svg"))

@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = os.path.join(templates_path, "sst_core.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)


def create_app():
    return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:create_app()", host="0.0.0.0", port=8000, reload=True)
