"""
파일 업로드 유틸리티
커뮤니티 신청서 첨부파일 처리
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException
import mimetypes


class FileUploadConfig:
    """파일 업로드 설정"""
    
    # 허용되는 파일 확장자
    ALLOWED_EXTENSIONS = {
        'pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
        'doc', 'docx', 'txt', 'rtf', 
        'xls', 'xlsx', 'csv',
        'ppt', 'pptx',
        'zip', 'rar', '7z'
    }
    
    # MIME 타입 매핑
    ALLOWED_MIMETYPES = {
        'application/pdf',
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain', 'application/rtf',
        'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv',
        'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed'
    }
    
    # 파일 크기 제한 (bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_FILES_COUNT = 5  # 최대 파일 개수
    
    # 업로드 디렉토리
    UPLOAD_DIR = Path("uploads/community_applications")


class CommunityFileUploader:
    """커뮤니티 신청서 파일 업로더"""
    
    def __init__(self):
        self.config = FileUploadConfig()
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """업로드 디렉토리 생성"""
        try:
            self.config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"⚠️ 업로드 디렉토리 생성 실패: {e}")
    
    def _get_file_extension(self, filename: str) -> str:
        """파일 확장자 추출"""
        return filename.lower().split('.')[-1] if '.' in filename else ''
    
    def _detect_mimetype(self, file_path: str) -> str:
        """파일의 MIME 타입 감지"""
        try:
            # mimetypes 사용
            mime_type, _ = mimetypes.guess_type(file_path)
            return mime_type or 'application/octet-stream'
        except:
            return 'application/octet-stream'
    
    def _validate_file(self, file: UploadFile) -> Dict[str, Any]:
        """파일 유효성 검증"""
        errors = []
        
        # 파일명 체크
        if not file.filename:
            errors.append("파일명이 없습니다")
            return {"valid": False, "errors": errors}
        
        # 확장자 체크
        extension = self._get_file_extension(file.filename)
        if extension not in self.config.ALLOWED_EXTENSIONS:
            errors.append(f"허용되지 않는 파일 형식입니다. (허용: {', '.join(self.config.ALLOWED_EXTENSIONS)})")
        
        # 파일 크기 체크
        try:
            # 실제 파일 크기를 읽어서 확인
            file.file.seek(0, 2)  # 파일 끝으로 이동
            file_size = file.file.tell()
            file.file.seek(0)  # 다시 처음으로 이동
            
            if file_size > self.config.MAX_FILE_SIZE:
                errors.append(f"파일 크기가 너무 큽니다. (최대: {self.config.MAX_FILE_SIZE // (1024*1024)}MB)")
                
            if file_size == 0:
                errors.append("빈 파일입니다")
        except Exception as e:
            errors.append(f"파일 크기 확인 실패: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "size": file_size if 'file_size' in locals() else 0
        }
    
    def _generate_safe_filename(self, original_filename: str) -> str:
        """안전한 파일명 생성"""
        extension = self._get_file_extension(original_filename)
        unique_id = str(uuid.uuid4())[:8]
        safe_name = "".join(c for c in original_filename if c.isalnum() or c in "._-")
        return f"{unique_id}_{safe_name}"
    
    def upload_files(self, files: List[UploadFile], application_id: int) -> Dict[str, Any]:
        """
        파일 업로드 처리
        
        Args:
            files: 업로드할 파일 리스트
            application_id: 신청서 ID
            
        Returns:
            업로드 결과 딕셔너리
        """
        if not files:
            return {"success": True, "files": [], "message": "업로드할 파일이 없습니다"}
        
        # 파일 개수 체크
        if len(files) > self.config.MAX_FILES_COUNT:
            return {
                "success": False, 
                "message": f"파일은 최대 {self.config.MAX_FILES_COUNT}개까지 업로드할 수 있습니다"
            }
        
        # 신청서별 디렉토리 생성
        app_dir = self.config.UPLOAD_DIR / str(application_id)
        app_dir.mkdir(exist_ok=True)
        
        uploaded_files = []
        errors = []
        
        for file in files:
            try:
                # 파일 유효성 검증
                validation_result = self._validate_file(file)
                if not validation_result["valid"]:
                    errors.extend(validation_result["errors"])
                    continue
                
                # 안전한 파일명 생성
                safe_filename = self._generate_safe_filename(file.filename)
                file_path = app_dir / safe_filename
                
                # 파일 저장
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # MIME 타입 실제 검증
                detected_mimetype = self._detect_mimetype(str(file_path))
                if detected_mimetype not in self.config.ALLOWED_MIMETYPES:
                    # 허용되지 않은 파일 타입이면 삭제
                    os.remove(file_path)
                    errors.append(f"{file.filename}: 허용되지 않는 파일 형식입니다")
                    continue
                
                # 파일 정보 저장
                file_info = {
                    "filename": file.filename,
                    "safe_filename": safe_filename,
                    "path": str(file_path.relative_to(Path.cwd())),
                    "size": validation_result["size"],
                    "mimetype": detected_mimetype
                }
                
                uploaded_files.append(file_info)
                print(f"✅ 파일 업로드 성공: {file.filename} → {safe_filename}")
                
            except Exception as e:
                error_msg = f"{file.filename}: 업로드 실패 ({str(e)})"
                errors.append(error_msg)
                print(f"❌ 파일 업로드 실패: {error_msg}")
        
        # 결과 반환
        success = len(uploaded_files) > 0
        message = f"{len(uploaded_files)}개 파일 업로드 완료"
        
        if errors:
            message += f", {len(errors)}개 파일 실패"
        
        return {
            "success": success,
            "files": uploaded_files,
            "errors": errors,
            "message": message
        }
    
    def delete_files(self, application_id: int) -> bool:
        """신청서 관련 파일들 삭제"""
        try:
            app_dir = self.config.UPLOAD_DIR / str(application_id)
            if app_dir.exists():
                shutil.rmtree(app_dir)
            return True
        except Exception as e:
            print(f"⚠️ 파일 삭제 실패: {e}")
            return False
    
    def get_file_path(self, application_id: int, filename: str) -> Optional[Path]:
        """파일 경로 반환"""
        file_path = self.config.UPLOAD_DIR / str(application_id) / filename
        return file_path if file_path.exists() else None
    
    def get_file_info(self, application_id: int) -> List[Dict[str, Any]]:
        """신청서의 모든 파일 정보 조회"""
        app_dir = self.config.UPLOAD_DIR / str(application_id)
        files = []
        
        if app_dir.exists():
            for file_path in app_dir.iterdir():
                if file_path.is_file():
                    try:
                        files.append({
                            "filename": file_path.name,
                            "path": str(file_path.relative_to(Path.cwd())),
                            "size": file_path.stat().st_size,
                            "mimetype": self._detect_mimetype(str(file_path))
                        })
                    except Exception as e:
                        print(f"⚠️ 파일 정보 조회 실패: {file_path.name} - {e}")
        
        return files


# 전역 인스턴스
community_uploader = CommunityFileUploader()


def get_uploader() -> CommunityFileUploader:
    """업로더 인스턴스 반환"""
    return community_uploader