import os
import uuid
import hashlib
from typing import Optional, Tuple
from pathlib import Path
from fastapi import UploadFile, HTTPException
import aiofiles
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
import PyPDF2
import docx
import logging

logger = logging.getLogger(__name__)

# 지원되는 파일 타입과 확장자
ALLOWED_EXTENSIONS = {
    "pdf": ["application/pdf"],
    "docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
    "doc": ["application/msword"],
    "txt": ["text/plain"],
    "mp3": ["audio/mpeg", "audio/mp3"],
    "mp4": ["video/mp4"],
    "wav": ["audio/wav"],
    "m4a": ["audio/m4a"],
}

# 최대 파일 크기 (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024


class FileHandler:
    """파일 업로드 및 처리 클래스"""

    def __init__(self, upload_directory: str = "uploads/sermons"):
        self.upload_directory = Path(upload_directory)
        self.upload_directory.mkdir(parents=True, exist_ok=True)

    def validate_file(self, file: UploadFile) -> Tuple[str, str]:
        """파일 유효성 검증"""
        # 파일 크기 검증
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB",
            )

        # 파일 확장자 추출
        filename = file.filename or ""
        file_extension = Path(filename).suffix.lower().lstrip(".")

        # 지원되는 확장자인지 확인
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS.keys())}",
            )

        return file_extension, filename

    def generate_unique_filename(
        self, original_filename: str, file_extension: str
    ) -> str:
        """고유한 파일명 생성"""
        # 파일명에서 확장자를 제거하고 UUID 추가
        name_without_ext = Path(original_filename).stem
        unique_id = str(uuid.uuid4())[:8]
        return f"{name_without_ext}_{unique_id}.{file_extension}"

    async def save_file(self, file: UploadFile, church_id: int) -> Tuple[str, str, int]:
        """파일 저장"""
        file_extension, original_filename = self.validate_file(file)
        unique_filename = self.generate_unique_filename(
            original_filename, file_extension
        )

        # 교회별 디렉토리 생성
        church_directory = self.upload_directory / f"church_{church_id}"
        church_directory.mkdir(parents=True, exist_ok=True)

        file_path = church_directory / unique_filename

        # 파일 저장
        file_size = 0
        try:
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                file_size = len(content)
                await f.write(content)
        except Exception as e:
            logger.error(f"Failed to save file {unique_filename}: {e}")
            raise HTTPException(status_code=500, detail="Failed to save file")

        # 상대 경로 반환
        relative_path = str(file_path.relative_to(self.upload_directory))

        return relative_path, file_extension, file_size

    def extract_text_content(self, file_path: Path, file_type: str) -> Optional[str]:
        """파일에서 텍스트 내용 추출"""
        try:
            if file_type == "pdf":
                return self._extract_pdf_text(file_path)
            elif file_type in ["docx", "doc"]:
                return self._extract_docx_text(file_path)
            elif file_type == "txt":
                return self._extract_txt_text(file_path)
            else:
                return None
        except Exception as e:
            logger.warning(f"Failed to extract text from {file_path}: {e}")
            return None

    def _extract_pdf_text(self, file_path: Path) -> str:
        """PDF에서 텍스트 추출"""
        text = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()

    def _extract_docx_text(self, file_path: Path) -> str:
        """DOCX에서 텍스트 추출"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()

    def _extract_txt_text(self, file_path: Path) -> str:
        """TXT 파일 읽기"""
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()

    def delete_file(self, relative_path: str) -> bool:
        """파일 삭제"""
        try:
            file_path = self.upload_directory / relative_path
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {relative_path}: {e}")
            return False

    def get_file_url(self, relative_path: str, base_url: str = "") -> str:
        """파일 URL 생성"""
        return f"{base_url}/api/v1/sermon-materials/files/{relative_path}"


# 전역 파일 핸들러 인스턴스
file_handler = FileHandler()
