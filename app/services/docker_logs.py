"""
Docker Container Logs Service
EC2 인스턴스의 Docker 컨테이너 로그를 실시간으로 수집하고 스트리밍
"""

import asyncio
import subprocess
import json
from typing import AsyncGenerator, Optional, List, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DockerLogsService:
    """Docker 컨테이너 로그 관리 서비스"""
    
    def __init__(self):
        self.container_prefix = "smart-yoram-backend"
        
    async def get_containers(self) -> List[Dict[str, str]]:
        """
        실행 중인 Docker 컨테이너 목록 조회
        
        Returns:
            컨테이너 정보 리스트
        """
        try:
            # Docker 컨테이너 목록 조회
            cmd = ["docker", "ps", "--format", "json"]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Failed to get containers: {stderr.decode()}")
                return []
            
            containers = []
            for line in stdout.decode().strip().split('\n'):
                if line:
                    container = json.loads(line)
                    # smart-yoram-backend 관련 컨테이너만 필터링
                    if self.container_prefix in container.get("Names", ""):
                        containers.append({
                            "id": container["ID"],
                            "name": container["Names"],
                            "image": container["Image"],
                            "status": container["Status"],
                            "created": container["CreatedAt"]
                        })
            
            return containers
            
        except Exception as e:
            logger.error(f"Error getting containers: {e}")
            return []
    
    async def get_logs(
        self,
        container_name: str = "backend_1",
        lines: int = 100,
        since: Optional[str] = None,
        until: Optional[str] = None,
        follow: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Docker 컨테이너 로그 조회
        
        Args:
            container_name: 컨테이너 이름 (backend_1, celery_worker_1, redis_1 등)
            lines: 조회할 로그 라인 수
            since: 시작 시간 (예: "2024-01-01T00:00:00")
            until: 종료 시간
            follow: 실시간 스트리밍 여부
            
        Yields:
            로그 라인
        """
        full_container_name = f"{self.container_prefix}_{container_name}"
        
        # Docker logs 명령어 구성
        cmd = ["docker", "logs", f"--tail={lines}"]
        
        if since:
            cmd.append(f"--since={since}")
        if until:
            cmd.append(f"--until={until}")
        if follow:
            cmd.append("-f")
            
        cmd.append(full_container_name)
        
        try:
            # 비동기 프로세스 실행
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            # 로그 스트리밍
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                log_line = line.decode('utf-8', errors='ignore').strip()
                if log_line:
                    # 로그 라인에 타임스탬프 추가 (없는 경우)
                    if not log_line.startswith('['):
                        log_line = f"[{datetime.now().isoformat()}] {log_line}"
                    
                    yield log_line
                    
                if not follow:
                    continue
                    
        except Exception as e:
            logger.error(f"Error reading logs from {full_container_name}: {e}")
            yield f"Error: {str(e)}"
        finally:
            if 'process' in locals():
                try:
                    process.terminate()
                    await process.wait()
                except:
                    pass
    
    async def get_logs_json(
        self,
        container_name: str = "backend_1",
        lines: int = 100,
        since_minutes: int = 60
    ) -> List[Dict[str, any]]:
        """
        Docker 컨테이너 로그를 JSON 형태로 조회
        
        Args:
            container_name: 컨테이너 이름
            lines: 조회할 로그 라인 수
            since_minutes: 최근 N분 간의 로그
            
        Returns:
            파싱된 로그 엔트리 리스트
        """
        since_time = (datetime.now() - timedelta(minutes=since_minutes)).isoformat()
        
        logs = []
        async for line in self.get_logs(
            container_name=container_name,
            lines=lines,
            since=since_time,
            follow=False
        ):
            # 로그 라인 파싱
            log_entry = self._parse_log_line(line)
            if log_entry:
                logs.append(log_entry)
        
        return logs
    
    def _parse_log_line(self, line: str) -> Optional[Dict[str, any]]:
        """
        로그 라인을 파싱하여 구조화된 데이터로 변환
        
        Args:
            line: 로그 라인
            
        Returns:
            파싱된 로그 엔트리
        """
        try:
            # 기본 로그 구조
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "message": line,
                "level": "INFO"
            }
            
            # 로그 레벨 감지
            if "ERROR" in line or "Exception" in line:
                log_entry["level"] = "ERROR"
            elif "WARNING" in line or "WARN" in line:
                log_entry["level"] = "WARNING"
            elif "DEBUG" in line:
                log_entry["level"] = "DEBUG"
            elif "CRITICAL" in line or "FATAL" in line:
                log_entry["level"] = "CRITICAL"
            
            # 타임스탬프 추출 시도
            if line.startswith("[") and "]" in line:
                timestamp_end = line.index("]")
                timestamp_str = line[1:timestamp_end]
                try:
                    log_entry["timestamp"] = timestamp_str
                    log_entry["message"] = line[timestamp_end + 1:].strip()
                except:
                    pass
            
            return log_entry
            
        except Exception as e:
            logger.error(f"Error parsing log line: {e}")
            return None
    
    async def search_logs(
        self,
        container_name: str,
        search_term: str,
        lines: int = 1000
    ) -> List[str]:
        """
        로그에서 특정 텍스트 검색
        
        Args:
            container_name: 컨테이너 이름
            search_term: 검색어
            lines: 검색할 로그 라인 수
            
        Returns:
            검색어가 포함된 로그 라인 리스트
        """
        matching_logs = []
        
        async for line in self.get_logs(
            container_name=container_name,
            lines=lines,
            follow=False
        ):
            if search_term.lower() in line.lower():
                matching_logs.append(line)
        
        return matching_logs
    
    async def get_error_logs(
        self,
        container_name: str = "backend_1",
        lines: int = 100
    ) -> List[str]:
        """
        에러 로그만 필터링하여 조회
        
        Args:
            container_name: 컨테이너 이름
            lines: 조회할 로그 라인 수
            
        Returns:
            에러 로그 라인 리스트
        """
        error_keywords = ["ERROR", "Exception", "Traceback", "CRITICAL", "FATAL"]
        error_logs = []
        
        async for line in self.get_logs(
            container_name=container_name,
            lines=lines * 10,  # 에러를 찾기 위해 더 많은 라인 검색
            follow=False
        ):
            if any(keyword in line for keyword in error_keywords):
                error_logs.append(line)
                if len(error_logs) >= lines:
                    break
        
        return error_logs
    
    async def clear_logs(self, container_name: str) -> bool:
        """
        컨테이너 로그 초기화 (컨테이너 재시작)
        
        Args:
            container_name: 컨테이너 이름
            
        Returns:
            성공 여부
        """
        full_container_name = f"{self.container_prefix}_{container_name}"
        
        try:
            # Docker 컨테이너 재시작
            cmd = ["docker", "restart", full_container_name]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Failed to restart container: {stderr.decode()}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error restarting container {full_container_name}: {e}")
            return False


# 싱글톤 인스턴스
docker_logs_service = DockerLogsService()