from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, and_, or_
from datetime import date

from app.crud.base import CRUDBase
from app.models.sermon_material import SermonMaterial, SermonCategory
from app.schemas.sermon_material import (
    SermonMaterialCreate,
    SermonMaterialUpdate,
    SermonCategoryCreate,
    SermonCategoryUpdate,
    SermonSearchRequest,
)


class CRUDSermonMaterial(
    CRUDBase[SermonMaterial, SermonMaterialCreate, SermonMaterialUpdate]
):

    def create_with_church_and_user(
        self, db: Session, *, obj_in: SermonMaterialCreate, church_id: int, user_id: int
    ) -> SermonMaterial:
        """교회 ID와 사용자 ID를 포함하여 설교 자료 생성"""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, church_id=church_id, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_church(
        self, db: Session, *, church_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[SermonMaterial], int]:
        """교회별 설교 자료 조회 (페이지네이션)"""
        query = db.query(self.model).filter(self.model.church_id == church_id)
        total = query.count()
        items = (
            query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
        )
        return items, total

    def get_public_by_church(
        self, db: Session, *, church_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[SermonMaterial], int]:
        """교회별 공개 설교 자료 조회"""
        query = db.query(self.model).filter(
            and_(self.model.church_id == church_id, self.model.is_public == True)
        )
        total = query.count()
        items = (
            query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
        )
        return items, total

    def search(
        self,
        db: Session,
        *,
        church_id: int,
        search_params: SermonSearchRequest,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[SermonMaterial], int]:
        """설교 자료 검색"""
        query = db.query(self.model).filter(self.model.church_id == church_id)

        # 검색어 필터
        if search_params.q:
            search_term = f"%{search_params.q}%"
            query = query.filter(
                or_(
                    self.model.title.ilike(search_term),
                    self.model.content.ilike(search_term),
                    self.model.author.ilike(search_term),
                    self.model.scripture_reference.ilike(search_term),
                )
            )

        # 카테고리 필터
        if search_params.category:
            query = query.filter(self.model.category == search_params.category)

        # 설교자 필터
        if search_params.author:
            query = query.filter(self.model.author.ilike(f"%{search_params.author}%"))

        # 날짜 필터
        if search_params.date_from:
            query = query.filter(self.model.date_preached >= search_params.date_from)
        if search_params.date_to:
            query = query.filter(self.model.date_preached <= search_params.date_to)

        # 태그 필터 (JSON 배열에서 검색)
        if search_params.tags:
            for tag in search_params.tags:
                query = query.filter(self.model.tags.contains([tag]))

        # 공개/비공개 필터
        if search_params.is_public is not None:
            query = query.filter(self.model.is_public == search_params.is_public)

        # 파일 타입 필터
        if search_params.file_type:
            query = query.filter(self.model.file_type == search_params.file_type)

        total = query.count()
        items = (
            query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
        )
        return items, total

    def increment_view_count(
        self, db: Session, *, db_obj: SermonMaterial
    ) -> SermonMaterial:
        """조회수 증가"""
        db_obj.view_count += 1
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def increment_download_count(
        self, db: Session, *, db_obj: SermonMaterial
    ) -> SermonMaterial:
        """다운로드수 증가"""
        db_obj.download_count += 1
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_stats(self, db: Session, *, church_id: int) -> dict:
        """교회별 설교 자료 통계"""
        total_materials = (
            db.query(self.model).filter(self.model.church_id == church_id).count()
        )
        public_materials = (
            db.query(self.model)
            .filter(
                and_(self.model.church_id == church_id, self.model.is_public == True)
            )
            .count()
        )
        private_materials = total_materials - public_materials

        # 총 다운로드수와 조회수
        totals = (
            db.query(
                func.sum(self.model.download_count).label("total_downloads"),
                func.sum(self.model.view_count).label("total_views"),
            )
            .filter(self.model.church_id == church_id)
            .first()
        )

        # 가장 많이 다운로드된 자료
        most_downloaded = (
            db.query(self.model)
            .filter(self.model.church_id == church_id)
            .order_by(desc(self.model.download_count))
            .first()
        )

        # 가장 많이 조회된 자료
        most_viewed = (
            db.query(self.model)
            .filter(self.model.church_id == church_id)
            .order_by(desc(self.model.view_count))
            .first()
        )

        # 최근 자료 5개
        recent_materials = (
            db.query(self.model)
            .filter(self.model.church_id == church_id)
            .order_by(desc(self.model.created_at))
            .limit(5)
            .all()
        )

        # 카테고리 수
        categories_count = (
            db.query(SermonCategory)
            .filter(SermonCategory.church_id == church_id)
            .count()
        )

        return {
            "total_materials": total_materials,
            "public_materials": public_materials,
            "private_materials": private_materials,
            "total_downloads": totals.total_downloads or 0,
            "total_views": totals.total_views or 0,
            "categories_count": categories_count,
            "most_downloaded": most_downloaded,
            "most_viewed": most_viewed,
            "recent_materials": recent_materials,
        }

    def get_authors(self, db: Session, *, church_id: int) -> List[str]:
        """교회별 설교자 목록 조회"""
        authors = (
            db.query(self.model.author)
            .filter(
                and_(self.model.church_id == church_id, self.model.author.isnot(None))
            )
            .distinct()
            .all()
        )
        return [author[0] for author in authors if author[0]]

    def get_tags(self, db: Session, *, church_id: int) -> List[str]:
        """교회별 태그 목록 조회"""
        # JSON 배열에서 태그 추출 (SQLite 호환)
        materials = (
            db.query(self.model.tags)
            .filter(
                and_(self.model.church_id == church_id, self.model.tags.isnot(None))
            )
            .all()
        )

        all_tags = set()
        for material in materials:
            if material.tags and isinstance(material.tags, list):
                all_tags.update(material.tags)

        return list(all_tags)


class CRUDSermonCategory(
    CRUDBase[SermonCategory, SermonCategoryCreate, SermonCategoryUpdate]
):

    def create_with_church(
        self, db: Session, *, obj_in: SermonCategoryCreate, church_id: int
    ) -> SermonCategory:
        """교회 ID를 포함하여 카테고리 생성"""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data, church_id=church_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_church(
        self, db: Session, *, church_id: int, active_only: bool = True
    ) -> List[SermonCategory]:
        """교회별 카테고리 조회"""
        query = db.query(self.model).filter(self.model.church_id == church_id)
        if active_only:
            query = query.filter(self.model.is_active == True)
        return query.order_by(asc(self.model.order_index), asc(self.model.name)).all()


# 인스턴스 생성
sermon_material = CRUDSermonMaterial(SermonMaterial)
sermon_category = CRUDSermonCategory(SermonCategory)
