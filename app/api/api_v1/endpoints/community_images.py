"""
커뮤니티 이미지 업로드 API 엔드포인트
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.utils.storage import supabase, validate_image_file, generate_unique_filename, COMMUNITY_IMAGES_BUCKET

router = APIRouter()

# 최대 업로드 파일 수
MAX_FILES_COUNT = 10


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
            raise HTTPException(
                status_code=400,
                detail=f"최대 {MAX_FILES_COUNT}개의 이미지만 업로드할 수 있습니다."
            )
        
        uploaded_urls = []
        
        for image in images:
            # 파일 크기 읽기
            content = await image.read()
            file_size = len(content)
            
            # 파일 유효성 검증
            is_valid, error_message = validate_image_file(image.filename or "unknown.jpg", file_size)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_message)

            # 고유 파일명 생성
            unique_filename = generate_unique_filename(
                image.filename or "image.jpg", 
                prefix=f"community_{current_user.church_id}"
            )
            
            # Supabase Storage에 업로드 (필수)
            result = supabase.storage.from_(COMMUNITY_IMAGES_BUCKET).upload(
                path=f"church_{current_user.church_id}/{unique_filename}",
                file=content,
                file_options={
                    "content-type": image.content_type or "image/jpeg",
                    "cache-control": "3600"
                }
            )
            
            if hasattr(result, 'error') and result.error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Supabase Storage 업로드 실패: {result.error.message}"
                )
            
            # 공개 URL 생성
            public_url = supabase.storage.from_(COMMUNITY_IMAGES_BUCKET).get_public_url(
                f"church_{current_user.church_id}/{unique_filename}"
            )
            
            uploaded_urls.append(public_url)
        
        return {
            "success": True,
            "urls": uploaded_urls,
            "message": f"{len(uploaded_urls)}개의 이미지가 성공적으로 업로드되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # 에러가 발생해도 기본 응답은 제공
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
            raise HTTPException(status_code=400, detail=error_message)
        
        # 고유 파일명 생성
        unique_filename = generate_unique_filename(
            image.filename or "image.jpg", 
            prefix=f"community_{current_user.church_id}"
        )
        
        # Supabase Storage에 업로드 (필수)
        result = supabase.storage.from_(COMMUNITY_IMAGES_BUCKET).upload(
            path=f"church_{current_user.church_id}/{unique_filename}",
            file=content,
            file_options={
                "content-type": image.content_type or "image/jpeg",
                "cache-control": "3600"
            }
        )
        
        if hasattr(result, 'error') and result.error:
            raise HTTPException(
                status_code=500,
                detail=f"Supabase Storage 업로드 실패: {result.error.message}"
            )
        
        # 공개 URL 생성
        public_url = supabase.storage.from_(COMMUNITY_IMAGES_BUCKET).get_public_url(
            f"church_{current_user.church_id}/{unique_filename}"
        )
        
        return {
            "success": True,
            "url": public_url,
            "message": "이미지가 성공적으로 업로드되었습니다."
        }
        
    except HTTPException:
        raise
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
    try:
        # Supabase Storage 연결 테스트
        buckets = supabase.storage.list_buckets()
        
        return {
            "success": True,
            "message": "이미지 업로드 서비스가 정상 작동 중입니다.",
            "storage_status": "connected",
            "max_file_size_mb": 5,
            "max_files_count": MAX_FILES_COUNT,
            "allowed_extensions": [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Supabase Storage 연결 실패: {str(e)}",
            "storage_status": "disconnected",
            "max_file_size_mb": 5,
            "max_files_count": MAX_FILES_COUNT,
            "allowed_extensions": [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        }