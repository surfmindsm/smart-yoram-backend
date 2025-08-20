from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path

router = APIRouter()

# Get the templates directory
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin_login.html", {"request": request})


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard page - requires superuser authentication"""
    return templates.TemplateResponse("admin.html", {"request": request})
