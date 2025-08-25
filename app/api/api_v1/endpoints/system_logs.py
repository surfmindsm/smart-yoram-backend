"""
System Logs API Endpoints
시스템 어드민용 Docker 로그 조회 및 관리 API
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import asyncio
import json

from app import models
from app.api import deps
from app.services.docker_logs import docker_logs_service

router = APIRouter()


def check_system_admin(current_user: models.User = Depends(deps.get_current_active_user)):
    """시스템 어드민 권한 체크"""
    if not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="System admin access required"
        )
    return current_user


@router.get("/containers", response_model=List[Dict[str, str]])
async def get_containers(
    current_user: models.User = Depends(check_system_admin)
):
    """
    실행 중인 Docker 컨테이너 목록 조회
    """
    containers = await docker_logs_service.get_containers()
    return containers


@router.get("/logs/{container_name}")
async def get_logs(
    container_name: str,
    lines: int = Query(100, description="Number of log lines to retrieve"),
    since_minutes: int = Query(60, description="Logs from last N minutes"),
    current_user: models.User = Depends(check_system_admin)
):
    """
    특정 컨테이너의 로그 조회
    
    Args:
        container_name: 컨테이너 이름 (backend_1, celery_worker_1, redis_1 등)
        lines: 조회할 로그 라인 수
        since_minutes: 최근 N분 간의 로그
    """
    logs = await docker_logs_service.get_logs_json(
        container_name=container_name,
        lines=lines,
        since_minutes=since_minutes
    )
    
    return {
        "container": container_name,
        "lines": len(logs),
        "since_minutes": since_minutes,
        "logs": logs
    }


@router.get("/logs/{container_name}/errors")
async def get_error_logs(
    container_name: str,
    lines: int = Query(100, description="Number of error log lines to retrieve"),
    current_user: models.User = Depends(check_system_admin)
):
    """
    특정 컨테이너의 에러 로그만 조회
    """
    error_logs = await docker_logs_service.get_error_logs(
        container_name=container_name,
        lines=lines
    )
    
    return {
        "container": container_name,
        "error_count": len(error_logs),
        "errors": error_logs
    }


@router.get("/logs/{container_name}/search")
async def search_logs(
    container_name: str,
    q: str = Query(..., description="Search term"),
    lines: int = Query(1000, description="Number of log lines to search"),
    current_user: models.User = Depends(check_system_admin)
):
    """
    로그에서 특정 텍스트 검색
    """
    if not q:
        raise HTTPException(status_code=400, detail="Search term is required")
    
    matching_logs = await docker_logs_service.search_logs(
        container_name=container_name,
        search_term=q,
        lines=lines
    )
    
    return {
        "container": container_name,
        "search_term": q,
        "matches": len(matching_logs),
        "logs": matching_logs
    }


@router.get("/logs/{container_name}/stream")
async def stream_logs(
    container_name: str,
    lines: int = Query(50, description="Initial number of log lines"),
    current_user: models.User = Depends(check_system_admin)
):
    """
    로그 실시간 스트리밍 (Server-Sent Events)
    """
    async def generate():
        try:
            async for log_line in docker_logs_service.get_logs(
                container_name=container_name,
                lines=lines,
                follow=True
            ):
                # SSE 형식으로 전송
                yield f"data: {json.dumps({'log': log_line})}\n\n"
                await asyncio.sleep(0.1)  # Rate limiting
        except asyncio.CancelledError:
            pass
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Nginx buffering 비활성화
        }
    )


@router.websocket("/ws/{container_name}")
async def websocket_logs(
    websocket: WebSocket,
    container_name: str,
    token: str = Query(..., description="Access token")
):
    """
    WebSocket을 통한 실시간 로그 스트리밍
    """
    # 토큰 검증
    try:
        from app.core.security import decode_access_token
        from app.db.session import SessionLocal
        
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        db = SessionLocal()
        user = db.query(models.User).filter(models.User.id == user_id).first()
        db.close()
        
        if not user or (not user.is_superuser and user.role != "admin"):
            await websocket.close(code=4003, reason="Unauthorized")
            return
            
    except Exception as e:
        await websocket.close(code=4003, reason="Invalid token")
        return
    
    await websocket.accept()
    
    try:
        # 초기 로그 전송
        await websocket.send_json({
            "type": "init",
            "container": container_name,
            "message": f"Connected to {container_name} logs"
        })
        
        # 실시간 로그 스트리밍
        async for log_line in docker_logs_service.get_logs(
            container_name=container_name,
            lines=50,
            follow=True
        ):
            await websocket.send_json({
                "type": "log",
                "container": container_name,
                "message": log_line
            })
            
            # 클라이언트로부터 메시지 확인 (연결 유지)
            try:
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=0.1
                )
                if message == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message == "stop":
                    break
            except asyncio.TimeoutError:
                continue
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        try:
            await websocket.close()
        except:
            pass


@router.post("/logs/{container_name}/clear")
async def clear_logs(
    container_name: str,
    current_user: models.User = Depends(check_system_admin)
):
    """
    컨테이너 로그 초기화 (컨테이너 재시작)
    
    주의: 컨테이너가 재시작되므로 일시적으로 서비스가 중단될 수 있습니다.
    """
    success = await docker_logs_service.clear_logs(container_name)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restart container {container_name}"
        )
    
    return {
        "status": "success",
        "message": f"Container {container_name} restarted successfully"
    }


@router.get("/logs/summary/all")
async def get_logs_summary(
    since_minutes: int = Query(60, description="Summary for last N minutes"),
    current_user: models.User = Depends(check_system_admin)
):
    """
    모든 컨테이너의 로그 요약 정보
    """
    containers = ["backend_1", "celery_worker_1", "celery_beat_1", "redis_1"]
    summary = {}
    
    for container in containers:
        try:
            logs = await docker_logs_service.get_logs_json(
                container_name=container,
                lines=1000,
                since_minutes=since_minutes
            )
            
            # 로그 레벨별 카운트
            level_counts = {
                "ERROR": 0,
                "WARNING": 0,
                "INFO": 0,
                "DEBUG": 0,
                "CRITICAL": 0
            }
            
            for log in logs:
                level = log.get("level", "INFO")
                if level in level_counts:
                    level_counts[level] += 1
            
            summary[container] = {
                "total_logs": len(logs),
                "levels": level_counts,
                "last_log": logs[-1] if logs else None
            }
            
        except Exception as e:
            summary[container] = {
                "error": str(e)
            }
    
    return {
        "since_minutes": since_minutes,
        "summary": summary
    }