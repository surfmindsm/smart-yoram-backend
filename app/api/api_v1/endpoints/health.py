from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import redis
from celery import current_app
from datetime import datetime
import psutil
import os

from app.api.deps import get_db
from app.core.redis import get_redis_client
from app.core.celery_app import celery_app

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "smart-yoram-backend"
    }


@router.get("/health/database", response_model=Dict[str, Any])
async def database_health(db: Session = Depends(get_db)):
    """Check database connectivity and health"""
    try:
        # Execute a simple query
        result = db.execute("SELECT 1").scalar()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "result": result
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "disconnected",
            "error": str(e)
        }


@router.get("/health/redis", response_model=Dict[str, Any])
async def redis_health():
    """Check Redis connectivity and health"""
    try:
        redis_client = get_redis_client()
        
        # Check if Redis is actually connected (not a dummy client)
        if hasattr(redis_client, 'ping'):
            redis_client.ping()
            info = redis_client.info()
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "redis": "connected",
                "version": info.get("redis_version", "unknown"),
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0)
            }
        else:
            return {
                "status": "warning",
                "timestamp": datetime.utcnow().isoformat(),
                "redis": "dummy_client",
                "message": "Redis not configured, using dummy client"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "redis": "disconnected",
            "error": str(e)
        }


@router.get("/health/celery", response_model=Dict[str, Any])
async def celery_health():
    """Check Celery workers and beat scheduler health"""
    try:
        # Check if Celery is configured
        if not celery_app:
            return {
                "status": "warning",
                "timestamp": datetime.utcnow().isoformat(),
                "celery": "not_configured",
                "message": "Celery not configured"
            }
        
        # Get active workers
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        active_workers = list(stats.keys()) if stats else []
        
        # Get scheduled tasks
        scheduled = inspect.scheduled()
        scheduled_count = sum(len(tasks) for tasks in (scheduled or {}).values())
        
        # Get active tasks
        active = inspect.active()
        active_count = sum(len(tasks) for tasks in (active or {}).values())
        
        return {
            "status": "healthy" if active_workers else "warning",
            "timestamp": datetime.utcnow().isoformat(),
            "celery": "connected",
            "workers": {
                "count": len(active_workers),
                "names": active_workers
            },
            "tasks": {
                "active": active_count,
                "scheduled": scheduled_count
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "celery": "error",
            "error": str(e)
        }


@router.get("/health/system", response_model=Dict[str, Any])
async def system_health():
    """Check system resources and health"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Process info
        process = psutil.Process()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "percent": memory.percent,
                    "total": f"{memory.total / (1024**3):.2f} GB",
                    "available": f"{memory.available / (1024**3):.2f} GB"
                },
                "disk": {
                    "percent": disk.percent,
                    "total": f"{disk.total / (1024**3):.2f} GB",
                    "free": f"{disk.free / (1024**3):.2f} GB"
                },
                "process": {
                    "pid": process.pid,
                    "memory_mb": f"{process.memory_info().rss / (1024**2):.2f}",
                    "threads": process.num_threads()
                }
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/health/all", response_model=Dict[str, Any])
async def all_health_checks(db: Session = Depends(get_db)):
    """Comprehensive health check of all services"""
    results = {}
    
    # Database check
    try:
        db.execute("SELECT 1").scalar()
        results["database"] = {"status": "healthy"}
    except Exception as e:
        results["database"] = {"status": "unhealthy", "error": str(e)}
    
    # Redis check
    try:
        redis_client = get_redis_client()
        if hasattr(redis_client, 'ping'):
            redis_client.ping()
            results["redis"] = {"status": "healthy"}
        else:
            results["redis"] = {"status": "warning", "message": "Using dummy client"}
    except Exception as e:
        results["redis"] = {"status": "unhealthy", "error": str(e)}
    
    # Celery check
    try:
        if celery_app:
            inspect = celery_app.control.inspect()
            stats = inspect.stats()
            if stats:
                results["celery"] = {"status": "healthy", "workers": len(stats)}
            else:
                results["celery"] = {"status": "warning", "message": "No active workers"}
        else:
            results["celery"] = {"status": "warning", "message": "Not configured"}
    except Exception as e:
        results["celery"] = {"status": "unhealthy", "error": str(e)}
    
    # System check
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        results["system"] = {
            "status": "healthy" if cpu < 90 and memory < 90 else "warning",
            "cpu": cpu,
            "memory": memory
        }
    except Exception as e:
        results["system"] = {"status": "error", "error": str(e)}
    
    # Overall status
    statuses = [v.get("status", "unknown") for v in results.values()]
    if all(s == "healthy" for s in statuses):
        overall_status = "healthy"
    elif any(s == "unhealthy" for s in statuses):
        overall_status = "unhealthy"
    elif any(s == "warning" for s in statuses):
        overall_status = "degraded"
    else:
        overall_status = "unknown"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "services": results
    }