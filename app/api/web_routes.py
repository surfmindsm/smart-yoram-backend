from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# Setup templates directory
# In Docker container, the structure is /app/app/templates
templates_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "templates"
)
templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect to login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/system-logs", response_class=HTMLResponse)
async def system_logs_page(request: Request):
    """System logs viewer page (for system admins only)"""
    return templates.TemplateResponse("system_logs.html", {"request": request})
