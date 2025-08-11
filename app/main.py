import warnings
warnings.filterwarnings("ignore", message=".*error reading bcrypt version.*")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging

from app.api.api_v1.api import api_router
from app.api.spec.api import spec_router
from app.api.web_routes import router as web_router
from app.api.admin_routes import router as admin_router
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set up CORS
cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:8080",
    "https://smart-yoram-admin.vercel.app",
    "https://smart-yoram.vercel.app",
    "*"  # Allow all origins for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(spec_router, prefix="/api")
app.include_router(admin_router)
app.include_router(web_router)

# Mount static files only if directory exists
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
