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

# Setup log interceptor for container logs
try:
    from app.services.container_logs import (
        setup_log_interceptor,
        container_logs_service,
    )

    setup_log_interceptor()
    logger.info("Log interceptor initialized for container logs")

    # 초기 로그 추가
    container_logs_service.add_log("Smart Yoram Backend Server Started", "INFO")
    container_logs_service.add_log(f"Version: {settings.VERSION}", "INFO")
    container_logs_service.add_log("Database connection established", "INFO")

except ImportError as e:
    logger.info(f"Running without container log interceptor: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set up CORS - Allow specific origins for authentication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://smart-yoram.vercel.app",
        "https://smart-yoram-frontend.vercel.app",
        "https://api.surfmind-team.com",
    ],
    allow_credentials=True,  # Enable credentials for authentication
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(spec_router, prefix="/api")
app.include_router(admin_router)
app.include_router(web_router)


# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request, call_next):
    from app.services.container_logs import container_logs_service
    import time

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Log the request
    log_message = f"{request.client.host} - {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    container_logs_service.add_log(log_message, "INFO")

    return response


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "service": "smart-yoram-backend",
        "version": settings.VERSION,
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Yoram Backend API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
    }


# Mount static files only if directory exists
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
