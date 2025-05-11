from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routes import speech
# from routes import lpr_core, myra_rover, myra_uav, myra_line_following

router = APIRouter()
templates = Jinja2Templates(directory="templates")

router.include_router(speech.router, tags=["sst"])
