"""
커뮤니티 이미지 업로드 API 엔드포인트
"""
import os
import uuid
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User

router = APIRouter()

# 허용 이미지 확장자
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_FILES_COUNT = 10  # 최대 10개 파일


def validate_image_file(filename: str, file_size: int) -> tuple[bool, str]:
    """이미지 파일 유효성 검증"""
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False, f"지원하지 않는 파일 형식입니다. 허용: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
    
    if file_size > MAX_FILE_SIZE:
        return False, f"파일 크기가 너무 큽니다. 최대: {MAX_FILE_SIZE // (1024*1024)}MB"
    
    return True, ""


def generate_unique_filename(original_filename: str, church_id: int) -> str:
    """고유 파일명 생성"""
    file_ext = os.path.splitext(original_filename)[1].lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"community_{church_id}_{timestamp}_{unique_id}{file_ext}"


@router.post("/images/upload", response_model=dict)
async def upload_community_images(
    images: List[UploadFile] = File(..., description="업로드할 이미지 파일들"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """커뮤니티 이미지 업로드 - 여러 이미지 파일 지원"""
    try:
        # 파일 개수 검증
        if len(images) > MAX_FILES_COUNT:
            return {
                "success": False,
                "urls": [],
                "message": f"최대 {MAX_FILES_COUNT}개의 이미지만 업로드할 수 있습니다."
            }
        
        uploaded_urls = []
        
        for i, image in enumerate(images):
            try:
                # 파일 크기 읽기
                content = await image.read()
                file_size = len(content)
                
                # 파일 유효성 검증
                is_valid, error_message = validate_image_file(image.filename or "unknown.jpg", file_size)
                if not is_valid:
                    continue  # 유효하지 않은 파일은 건너뛰기
                
                # 고유 파일명 생성
                unique_filename = generate_unique_filename(
                    image.filename or f"image_{i}.jpg", 
                    current_user.church_id
                )
                
                # 실제 파일 저장
                import os
                os.makedirs("static/community/images", exist_ok=True)
                file_path = f"static/community/images/{unique_filename}"
                
                with open(file_path, "wb") as buffer:
                    buffer.write(content)
                
                # URL 생성
                file_url = f"https://api.surfmind-team.com/static/community/images/{unique_filename}"
                uploaded_urls.append(file_url)
                
            except Exception as file_error:
                continue  # 개별 파일 에러는 무시하고 계속 진행
        
        return {
            "success": True,
            "urls": uploaded_urls,
            "message": f"{len(uploaded_urls)}개의 이미지가 성공적으로 업로드되었습니다."
        }
        
    except Exception as e:
        # 전체 프로세스 실패시 기본 응답
        return {
            "success": False,
            "urls": [],
            "message": f"이미지 업로드 중 오류가 발생했습니다: {str(e)}"
        }


@router.post("/images/upload-single", response_model=dict)
async def upload_single_community_image(
    image: UploadFile = File(..., description="업로드할 이미지 파일"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """커뮤니티 단일 이미지 업로드"""
    try:
        # 파일 크기 읽기
        content = await image.read()
        file_size = len(content)
        
        # 파일 유효성 검증
        is_valid, error_message = validate_image_file(image.filename or "unknown.jpg", file_size)
        if not is_valid:
            return {
                "success": False,
                "url": "",
                "message": error_message
            }
        
        # 고유 파일명 생성
        unique_filename = generate_unique_filename(
            image.filename or "image.jpg", 
            current_user.church_id
        )
        
        # 실제 파일 저장
        import os
        os.makedirs("static/community/images", exist_ok=True)
        file_path = f"static/community/images/{unique_filename}"
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # URL 생성
        file_url = f"https://api.surfmind-team.com/static/community/images/{unique_filename}"
        
        return {
            "success": True,
            "url": file_url,
            "message": "이미지가 성공적으로 업로드되었습니다."
        }
        
    except Exception as e:
        return {
            "success": False,
            "url": "",
            "message": f"이미지 업로드 중 오류가 발생했습니다: {str(e)}"
        }


@router.post("/upload-image", response_model=dict)
async def upload_community_image_alias(
    images: List[UploadFile] = File(..., description="업로드할 이미지 파일들"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """커뮤니티 이미지 업로드 - 프론트엔드 호환성을 위한 별칭 엔드포인트"""
    return await upload_community_images(images, db, current_user)


@router.get("/images/health", response_model=dict)
def check_image_upload_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """이미지 업로드 서비스 상태 확인"""
    return {
        "success": True,
        "message": "이미지 업로드 서비스가 정상 작동 중입니다.",
        "storage_status": "ready",
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "max_files_count": MAX_FILES_COUNT,
        "allowed_extensions": list(ALLOWED_IMAGE_EXTENSIONS)
    }