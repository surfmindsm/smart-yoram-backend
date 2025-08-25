"""
Container Logs Service - Alternative approach using log files
컨테이너 내부에서 로그 파일을 직접 읽는 방식
"""

import asyncio
from typing import AsyncGenerator, Optional, List, Dict
from datetime import datetime, timedelta
import logging
import os
import aiofiles
from collections import deque

logger = logging.getLogger(__name__)


class ContainerLogsService:
    """컨테이너 내부 로그 관리 서비스"""

    def __init__(self):
        # 로그 파일 경로들
        self.log_paths = {
            "backend": "/var/log/uvicorn.log",  # 또는 stdout
            "application": "/app/app.log",
            "error": "/app/error.log",
        }

        # 메모리에 로그 버퍼 유지 (최근 10000줄)
        self.log_buffer = deque(maxlen=10000)

    async def get_containers(self) -> List[Dict[str, str]]:
        """
        사용 가능한 로그 소스 목록
        """
        return [
            {
                "id": "application",
                "name": "Application Logs",
                "status": "active",
                "description": "Application stdout/stderr logs",
            },
            {
                "id": "error",
                "name": "Error Logs",
                "status": "active",
                "description": "Application error logs",
            },
            {
                "id": "access",
                "name": "Access Logs",
                "status": "active",
                "description": "HTTP access logs",
            },
        ]

    async def get_logs(
        self,
        container_name: str = "application",
        lines: int = 100,
        since: Optional[str] = None,
        until: Optional[str] = None,
        follow: bool = False,
    ) -> AsyncGenerator[str, None]:
        """
        로그 조회 - stdout/stderr 캡처 또는 파일 읽기
        """
        try:
            # 실시간 stdout/stderr 캡처
            if container_name == "application":
                # 현재 프로세스의 로그를 캡처
                import sys
                import io

                # 최근 로그 버퍼에서 읽기
                recent_logs = list(self.log_buffer)
                if lines > 0:
                    recent_logs = recent_logs[-lines:]

                for log_line in recent_logs:
                    yield log_line

                if follow:
                    # 실시간 로그 스트리밍 시뮬레이션
                    while True:
                        await asyncio.sleep(1)
                        # 새로운 로그가 있으면 전송
                        if len(self.log_buffer) > len(recent_logs):
                            new_logs = list(self.log_buffer)[len(recent_logs) :]
                            for log_line in new_logs:
                                yield log_line
                            recent_logs = list(self.log_buffer)

            # 파일에서 로그 읽기
            elif container_name in self.log_paths:
                log_path = self.log_paths[container_name]
                if os.path.exists(log_path):
                    async with aiofiles.open(log_path, "r") as f:
                        # tail 구현
                        all_lines = await f.readlines()
                        if lines > 0:
                            all_lines = all_lines[-lines:]

                        for line in all_lines:
                            yield line.strip()

                        if follow:
                            # 파일 follow 모드
                            await f.seek(0, 2)  # 파일 끝으로 이동
                            while True:
                                line = await f.readline()
                                if line:
                                    yield line.strip()
                                else:
                                    await asyncio.sleep(0.5)
                else:
                    yield f"Log file not found: {log_path}"

        except Exception as e:
            logger.error(f"Error reading logs: {e}")
            yield f"Error: {str(e)}"

    def add_log(self, message: str, level: str = "INFO"):
        """
        로그 버퍼에 메시지 추가 (애플리케이션에서 호출)
        """
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] [{level}] {message}"
        self.log_buffer.append(log_line)

    async def get_logs_json(
        self,
        container_name: str = "application",
        lines: int = 100,
        since_minutes: int = 60,
    ) -> List[Dict[str, any]]:
        """
        로그를 JSON 형태로 조회
        """
        logs = []

        async for line in self.get_logs(
            container_name=container_name, lines=lines, follow=False
        ):
            log_entry = self._parse_log_line(line)
            if log_entry:
                logs.append(log_entry)

        return logs

    def _parse_log_line(self, line: str) -> Optional[Dict[str, any]]:
        """
        로그 라인 파싱
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "message": line,
                "level": "INFO",
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

            return log_entry

        except Exception as e:
            logger.error(f"Error parsing log line: {e}")
            return None

    async def search_logs(
        self, container_name: str, search_term: str, lines: int = 1000
    ) -> List[str]:
        """
        로그 검색
        """
        matching_logs = []

        async for line in self.get_logs(
            container_name=container_name, lines=lines, follow=False
        ):
            if search_term.lower() in line.lower():
                matching_logs.append(line)

        return matching_logs

    async def get_error_logs(
        self, container_name: str = "application", lines: int = 100
    ) -> List[str]:
        """
        에러 로그만 필터링
        """
        error_keywords = ["ERROR", "Exception", "Traceback", "CRITICAL", "FATAL"]
        error_logs = []

        async for line in self.get_logs(
            container_name=container_name, lines=lines * 10, follow=False
        ):
            if any(keyword in line for keyword in error_keywords):
                error_logs.append(line)
                if len(error_logs) >= lines:
                    break

        return error_logs


# 싱글톤 인스턴스
container_logs_service = ContainerLogsService()


# 로깅 인터셉터 - 애플리케이션 로그를 버퍼에 추가
class LogInterceptor(logging.Handler):
    """Python 로깅을 인터셉트하여 버퍼에 저장"""

    def emit(self, record):
        try:
            msg = self.format(record)
            container_logs_service.add_log(msg, record.levelname)
        except Exception:
            self.handleError(record)


# 로깅 설정
def setup_log_interceptor():
    """로그 인터셉터 설정"""
    interceptor = LogInterceptor()
    interceptor.setLevel(logging.DEBUG)

    # 포맷터 설정
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    interceptor.setFormatter(formatter)

    # 루트 로거에 추가
    logging.getLogger().addHandler(interceptor)

    # FastAPI/Uvicorn 로거에도 추가
    logging.getLogger("uvicorn").addHandler(interceptor)
    logging.getLogger("uvicorn.access").addHandler(interceptor)
    logging.getLogger("uvicorn.error").addHandler(interceptor)
    logging.getLogger("fastapi").addHandler(interceptor)
