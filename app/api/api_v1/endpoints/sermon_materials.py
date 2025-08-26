from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import math
import logging
from pathlib import Path

from app import models, schemas, crud
from app.api import deps
from app.schemas.sermon_material import (
    SermonMaterialCreate,
    SermonMaterialUpdate,
    SermonMaterialResponse,
    SermonMaterialListResponse,
    SermonCategoryCreate,
    SermonCategoryUpdate,
    SermonCategoryResponse,
    SermonSearchRequest,
    SermonStatsResponse,
    FileUploadResponse,
)
from app.utils.file_handler import file_handler

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=SermonMaterialListResponse)
def read_sermon_materials(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    교회별 설교 자료 목록 조회
    """
    items, total = crud.sermon_material.get_by_church(
        db=db, church_id=current_user.church_id, skip=skip, limit=limit
    )

    pages = math.ceil(total / limit) if total > 0 else 1
    page = (skip // limit) + 1

    return SermonMaterialListResponse(
        items=items, total=total, page=page, size=limit, pages=pages
    )


@router.post("/", response_model=SermonMaterialResponse)
def create_sermon_material(
    *,
    db: Session = Depends(deps.get_db),
    material_in: SermonMaterialCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    설교 자료 생성
    """
    # 권한 확인 (관리자, 목사, 리더만 가능)
    if current_user.role not in ["admin", "minister", "leader"]:
        raise HTTPException(
            status_code=403,
            detail="Only admins, ministers, and leaders can create sermon materials",
        )

    material = crud.sermon_material.create_with_church_and_user(
        db=db,
        obj_in=material_in,
        church_id=current_user.church_id,
        user_id=current_user.id,
    )
    return material


@router.get("/{material_id}", response_model=SermonMaterialResponse)
def read_sermon_material(
    *,
    db: Session = Depends(deps.get_db),
    material_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    특정 설교 자료 조회
    """
    material = crud.sermon_material.get(db=db, id=material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Sermon material not found")

    if material.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 비공개 자료의 경우 작성자 또는 관리자만 조회 가능
    if not material.is_public and material.user_id != current_user.id:
        if current_user.role not in ["admin", "minister"]:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    # 조회수 증가
    crud.sermon_material.increment_view_count(db=db, db_obj=material)

    return material


@router.put("/{material_id}", response_model=SermonMaterialResponse)
def update_sermon_material(
    *,
    db: Session = Depends(deps.get_db),
    material_id: int,
    material_in: SermonMaterialUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    설교 자료 수정
    """
    material = crud.sermon_material.get(db=db, id=material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Sermon material not found")

    if material.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 작성자 또는 관리자만 수정 가능
    if material.user_id != current_user.id and current_user.role not in [
        "admin",
        "minister",
    ]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    material = crud.sermon_material.update(db=db, db_obj=material, obj_in=material_in)
    return material


@router.delete("/{material_id}")
def delete_sermon_material(
    *,
    db: Session = Depends(deps.get_db),
    material_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    설교 자료 삭제
    """
    material = crud.sermon_material.get(db=db, id=material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Sermon material not found")

    if material.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 작성자 또는 관리자만 삭제 가능
    if material.user_id != current_user.id and current_user.role not in [
        "admin",
        "minister",
    ]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 파일이 있다면 삭제
    if material.file_url:
        file_handler.delete_file(material.file_url)

    crud.sermon_material.remove(db=db, id=material_id)
    return {"success": True, "message": "Sermon material deleted successfully"}


@router.post("/upload", response_model=FileUploadResponse)
async def upload_sermon_file(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    설교 자료 파일 업로드
    """
    # 권한 확인
    if current_user.role not in ["admin", "minister", "leader"]:
        raise HTTPException(
            status_code=403,
            detail="Only admins, ministers, and leaders can upload files",
        )

    try:
        # 파일 저장
        relative_path, file_type, file_size = await file_handler.save_file(
            file=file, church_id=current_user.church_id
        )

        # 파일 URL 생성
        file_url = file_handler.get_file_url(relative_path)

        return FileUploadResponse(
            success=True,
            file_url=relative_path,
            file_type=file_type,
            file_size=file_size,
            filename=file.filename or "unknown",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")


@router.get("/files/{file_path:path}")
def download_sermon_file(
    *,
    db: Session = Depends(deps.get_db),
    file_path: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    설교 자료 파일 다운로드
    """
    # 파일이 속한 설교 자료 찾기
    material = (
        db.query(models.SermonMaterial)
        .filter(
            models.SermonMaterial.file_url == file_path,
            models.SermonMaterial.church_id == current_user.church_id,
        )
        .first()
    )

    if not material:
        raise HTTPException(status_code=404, detail="File not found")

    # 비공개 자료 권한 확인
    if not material.is_public and material.user_id != current_user.id:
        if current_user.role not in ["admin", "minister"]:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    # 파일 경로 구성
    full_file_path = Path(file_handler.upload_directory) / file_path

    if not full_file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # 다운로드수 증가
    crud.sermon_material.increment_download_count(db=db, db_obj=material)

    # 파일 응답
    return FileResponse(
        path=str(full_file_path),
        filename=Path(file_path).name,
        media_type="application/octet-stream",
    )


@router.get("/search/", response_model=SermonMaterialListResponse)
def search_sermon_materials(
    *,
    db: Session = Depends(deps.get_db),
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    is_public: Optional[bool] = Query(None),
    file_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    설교 자료 검색
    """
    search_params = SermonSearchRequest(
        q=q,
        category=category,
        author=author,
        tags=tags,
        is_public=is_public,
        file_type=file_type,
    )

    items, total = crud.sermon_material.search(
        db=db,
        church_id=current_user.church_id,
        search_params=search_params,
        skip=skip,
        limit=limit,
    )

    pages = math.ceil(total / limit) if total > 0 else 1
    page = (skip // limit) + 1

    return SermonMaterialListResponse(
        items=items, total=total, page=page, size=limit, pages=pages
    )


@router.get("/stats/", response_model=SermonStatsResponse)
def get_sermon_stats(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    설교 자료 통계 조회
    """
    stats = crud.sermon_material.get_stats(db=db, church_id=current_user.church_id)
    return SermonStatsResponse(**stats)


@router.get("/authors/", response_model=List[str])
def get_sermon_authors(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    설교자 목록 조회
    """
    authors = crud.sermon_material.get_authors(db=db, church_id=current_user.church_id)
    return authors


@router.get("/tags/", response_model=List[str])
def get_sermon_tags(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    태그 목록 조회
    """
    tags = crud.sermon_material.get_tags(db=db, church_id=current_user.church_id)
    return tags


# 카테고리 관련 엔드포인트
@router.get("/categories/", response_model=List[SermonCategoryResponse])
def read_sermon_categories(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    설교 카테고리 목록 조회
    """
    categories = crud.sermon_category.get_by_church(
        db=db, church_id=current_user.church_id
    )
    return categories


@router.post("/categories/", response_model=SermonCategoryResponse)
def create_sermon_category(
    *,
    db: Session = Depends(deps.get_db),
    category_in: SermonCategoryCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    설교 카테고리 생성
    """
    # 관리자와 목사만 가능
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(
            status_code=403, detail="Only admins and ministers can create categories"
        )

    category = crud.sermon_category.create_with_church(
        db=db, obj_in=category_in, church_id=current_user.church_id
    )
    return category


@router.put("/categories/{category_id}", response_model=SermonCategoryResponse)
def update_sermon_category(
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    category_in: SermonCategoryUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    설교 카테고리 수정
    """
    category = crud.sermon_category.get(db=db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 관리자와 목사만 가능
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(
            status_code=403, detail="Only admins and ministers can update categories"
        )

    category = crud.sermon_category.update(db=db, db_obj=category, obj_in=category_in)
    return category


@router.delete("/categories/{category_id}")
def delete_sermon_category(
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    설교 카테고리 삭제
    """
    category = crud.sermon_category.get(db=db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 관리자와 목사만 가능
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(
            status_code=403, detail="Only admins and ministers can delete categories"
        )

    crud.sermon_category.remove(db=db, id=category_id)
    return {"success": True, "message": "Category deleted successfully"}


@router.get("/test/database")
def test_database_connection(db: Session = Depends(deps.get_db)) -> Any:
    """
    Test database connection and check if sermon materials tables exist (public endpoint for testing)
    """
    try:
        from sqlalchemy import text

        # Test basic connection
        result = db.execute(text("SELECT 1")).scalar()

        # Check if sermon_materials table exists
        table_check = db.execute(
            text(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'sermon_materials'"
            )
        ).scalar()

        # Check if sermon_categories table exists
        category_check = db.execute(
            text(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'sermon_categories'"
            )
        ).scalar()

        return {
            "status": "success",
            "database_connected": result == 1,
            "sermon_materials_table_exists": table_check > 0,
            "sermon_categories_table_exists": category_check > 0,
            "timestamp": "2025-08-26T12:45:00Z",
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2025-08-26T12:45:00Z",
        }


@router.get("/test/migration")
def test_migration_status(db: Session = Depends(deps.get_db)) -> Any:
    """
    Check alembic migration status (public endpoint for testing)
    """
    try:
        from sqlalchemy import text

        # Check alembic version table
        version_check = db.execute(
            text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'alembic_version'")
        ).scalar()

        current_version = None
        if version_check > 0:
            current_version = db.execute(text("SELECT version_num FROM alembic_version")).scalar()

        return {
            "status": "success",
            "alembic_version_table_exists": version_check > 0,
            "current_migration_version": current_version,
            "sermon_materials_migration_id": "de7501bc3e2f",
            "timestamp": "2025-08-26T12:50:00Z",
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2025-08-26T12:50:00Z",
        }


@router.post("/test/run-migration")
def run_sermon_materials_migration(db: Session = Depends(deps.get_db)) -> Any:
    """
    Manually run sermon materials migration (public endpoint for testing)
    """
    try:
        from sqlalchemy import text

        # Create sermon_materials table manually
        create_materials_table = text("""
        CREATE TABLE IF NOT EXISTS sermon_materials (
            id SERIAL PRIMARY KEY,
            church_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255),
            content TEXT,
            file_url VARCHAR(500),
            file_type VARCHAR(50),
            file_size INTEGER,
            category VARCHAR(100),
            scripture_reference VARCHAR(200),
            date_preached DATE,
            tags JSON,
            is_public BOOLEAN DEFAULT FALSE,
            view_count INTEGER DEFAULT 0,
            download_count INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (church_id) REFERENCES churches(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        # Create sermon_categories table manually
        create_categories_table = text("""
        CREATE TABLE IF NOT EXISTS sermon_categories (
            id SERIAL PRIMARY KEY,
            church_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            description VARCHAR(500),
            color VARCHAR(7) DEFAULT '#3B82F6',
            order_index INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (church_id) REFERENCES churches(id)
        )
        """)

        # Execute table creation
        db.execute(create_materials_table)
        db.execute(create_categories_table)
        db.commit()

        return {
            "status": "success",
            "message": "Sermon materials tables created successfully",
            "timestamp": "2025-08-26T12:52:00Z",
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2025-08-26T12:52:00Z",
        }
