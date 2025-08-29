"""
교회 데이터 캐싱 서비스

성능 최적화를 위한 교회 데이터 캐싱 시스템
- 교인 통계: 1시간 캐시 (자주 변하지 않음)
- 헌금 통계: 30분 캐시 (하루에 몇 번만 변경)  
- 출석 통계: 15분 캐시 (예배 후에만 변경)
- 공지사항: 5분 캐시 (수정 빈도 높음)
- 예배 일정: 6시간 캐시 (거의 변하지 않음)
- 기도요청: 10분 캐시 (비교적 자주 변경)
- 심방요청: 10분 캐시 (비교적 자주 변경)
"""

from typing import Dict, Any, List, Optional, Callable
from sqlalchemy.orm import Session
import hashlib
import logging
from datetime import datetime

from app.core.redis import redis_client
from app.services.church_data_context import (
    get_enhanced_member_statistics,
    get_all_offerings,
    get_attendance_stats,
    get_recent_announcements,
    get_worship_schedule,
    get_recent_prayer_requests,
    get_recent_pastoral_care_requests,
)

logger = logging.getLogger(__name__)


class ChurchDataCache:
    """교회 데이터 캐싱 매니저"""

    def __init__(self):
        self.redis = redis_client
        
        # 데이터 타입별 캐시 TTL 설정 (초 단위)
        self.cache_ttl = {
            "member_stats": 3600,      # 1시간 - 교인 정보는 자주 변하지 않음
            "offering_stats": 1800,    # 30분 - 헌금은 하루에 몇 번만 변경
            "attendance_stats": 900,   # 15분 - 출석은 예배 후에만 변경
            "announcements": 300,      # 5분 - 공지사항은 수정 빈도 높음
            "worship_schedule": 21600, # 6시간 - 예배 일정은 거의 변하지 않음
            "prayer_requests": 600,    # 10분 - 기도요청은 비교적 자주 변경
            "pastoral_care_requests": 600, # 10분 - 심방요청은 비교적 자주 변경
        }
        
        # 데이터 조회 함수 매핑
        self.data_fetchers = {
            "member_stats": get_enhanced_member_statistics,
            "offering_stats": get_all_offerings,
            "attendance_stats": get_attendance_stats,
            "announcements": get_recent_announcements,
            "worship_schedule": get_worship_schedule,
            "prayer_requests": get_recent_prayer_requests,
            "pastoral_care_requests": get_recent_pastoral_care_requests,
        }

    def get_cache_key(self, church_id: int, data_type: str, **params) -> str:
        """캐시 키 생성"""
        # 파라미터가 있으면 포함하여 고유한 키 생성
        param_str = "_".join(f"{k}={v}" for k, v in sorted(params.items())) if params else ""
        key_data = f"church_data:{church_id}:{data_type}"
        if param_str:
            key_data += f":{param_str}"
        
        # 키가 너무 길면 해시 사용
        if len(key_data) > 200:
            return f"church_data:{church_id}:{hashlib.md5(key_data.encode()).hexdigest()}"
        return key_data

    def get_cached_data(self, db: Session, church_id: int, data_type: str, **params) -> Any:
        """캐시된 데이터 조회 (캐시 미스시 DB에서 조회 후 캐시 저장)"""
        
        if not self.redis.connected:
            # Redis가 사용 불가능하면 직접 DB 조회
            logger.warning(f"Redis not available, fetching {data_type} directly from DB")
            return self._fetch_from_db(db, church_id, data_type, **params)
        
        cache_key = self.get_cache_key(church_id, data_type, **params)
        
        try:
            # 캐시에서 조회
            cached_data = self.redis.cache_get(cache_key)
            if cached_data:
                logger.info(f"Cache HIT for {data_type} (church_id: {church_id})")
                return cached_data
            
            # 캐시 미스 - DB에서 조회
            logger.info(f"Cache MISS for {data_type} (church_id: {church_id})")
            data = self._fetch_from_db(db, church_id, data_type, **params)
            
            # 캐시에 저장
            ttl = self.cache_ttl.get(data_type, 300)  # 기본 5분 TTL
            self.redis.cache_set(cache_key, data, ttl=ttl)
            logger.info(f"Cached {data_type} for {ttl}s (church_id: {church_id})")
            
            return data
            
        except Exception as e:
            logger.error(f"Cache error for {data_type}: {e}")
            # 캐시 오류시 직접 DB 조회
            return self._fetch_from_db(db, church_id, data_type, **params)

    def _fetch_from_db(self, db: Session, church_id: int, data_type: str, **params) -> Any:
        """데이터베이스에서 직접 데이터 조회"""
        
        fetcher = self.data_fetchers.get(data_type)
        if not fetcher:
            logger.error(f"No fetcher found for data_type: {data_type}")
            return {}
            
        try:
            # 함수 시그니처에 따라 파라미터 전달
            import inspect
            sig = inspect.signature(fetcher)
            
            # limit 파라미터가 있는 함수들 처리
            if 'limit' in sig.parameters:
                limit = params.get('limit', 100)
                return fetcher(db, church_id, limit)
            else:
                return fetcher(db, church_id)
                
        except Exception as e:
            logger.error(f"Error fetching {data_type} from DB: {e}")
            return {} if data_type.endswith('_stats') else []

    def invalidate_cache(self, church_id: int, data_types: List[str]):
        """캐시 무효화"""
        
        if not self.redis.connected:
            logger.warning("Redis not available, cannot invalidate cache")
            return
            
        try:
            invalidated_count = 0
            for data_type in data_types:
                cache_key = self.get_cache_key(church_id, data_type)
                self.redis.cache_delete(cache_key)
                invalidated_count += 1
                
            logger.info(f"Invalidated {invalidated_count} cache entries for church_id: {church_id}")
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")

    def invalidate_church_cache(self, church_id: int):
        """특정 교회의 모든 캐시 무효화"""
        all_data_types = list(self.cache_ttl.keys())
        self.invalidate_cache(church_id, all_data_types)

    def get_cache_stats(self, church_id: int) -> Dict[str, Any]:
        """캐시 통계 정보 조회"""
        
        if not self.redis.connected:
            return {"status": "Redis not available"}
            
        stats = {
            "church_id": church_id,
            "timestamp": datetime.now().isoformat(),
            "cache_status": {},
        }
        
        for data_type in self.cache_ttl.keys():
            cache_key = self.get_cache_key(church_id, data_type)
            try:
                # 캐시 존재 여부 및 TTL 확인
                exists = self.redis.client.exists(f"cache:{cache_key}")
                ttl = self.redis.client.ttl(f"cache:{cache_key}") if exists else -1
                
                stats["cache_status"][data_type] = {
                    "cached": bool(exists),
                    "ttl_seconds": ttl,
                    "configured_ttl": self.cache_ttl[data_type],
                }
            except Exception as e:
                stats["cache_status"][data_type] = {"error": str(e)}
                
        return stats


# 싱글톤 인스턴스
cache_manager = ChurchDataCache()


# 편의 함수들
def get_member_stats_cached(db: Session, church_id: int) -> Dict:
    """캐시된 교인 통계 조회"""
    return cache_manager.get_cached_data(db, church_id, "member_stats")


def get_offering_stats_cached(db: Session, church_id: int) -> Dict:
    """캐시된 헌금 통계 조회"""
    return cache_manager.get_cached_data(db, church_id, "offering_stats")


def get_attendance_stats_cached(db: Session, church_id: int) -> Dict:
    """캐시된 출석 통계 조회"""
    return cache_manager.get_cached_data(db, church_id, "attendance_stats")


def get_announcements_cached(db: Session, church_id: int, limit: int = 100) -> List[Dict]:
    """캐시된 공지사항 조회"""
    return cache_manager.get_cached_data(db, church_id, "announcements", limit=limit)


def get_worship_schedule_cached(db: Session, church_id: int, limit: int = 100) -> List[Dict]:
    """캐시된 예배 일정 조회"""
    return cache_manager.get_cached_data(db, church_id, "worship_schedule", limit=limit)


def get_prayer_requests_cached(db: Session, church_id: int, limit: int = 100) -> List[Dict]:
    """캐시된 기도요청 조회"""
    return cache_manager.get_cached_data(db, church_id, "prayer_requests", limit=limit)


def get_pastoral_care_requests_cached(db: Session, church_id: int, limit: int = 100) -> List[Dict]:
    """캐시된 심방요청 조회"""
    return cache_manager.get_cached_data(db, church_id, "pastoral_care_requests", limit=limit)


# 캐시 무효화 헬퍼 함수들 - 데이터 생성/수정 시 사용
def invalidate_member_cache(church_id: int):
    """교인 관련 캐시 무효화"""
    cache_manager.invalidate_cache(church_id, ["member_stats"])


def invalidate_offering_cache(church_id: int):
    """헌금 관련 캐시 무효화"""
    cache_manager.invalidate_cache(church_id, ["offering_stats"])


def invalidate_attendance_cache(church_id: int):
    """출석 관련 캐시 무효화"""  
    cache_manager.invalidate_cache(church_id, ["attendance_stats"])


def invalidate_announcement_cache(church_id: int):
    """공지사항 관련 캐시 무효화"""
    cache_manager.invalidate_cache(church_id, ["announcements"])


def invalidate_worship_cache(church_id: int):
    """예배 일정 관련 캐시 무효화"""
    cache_manager.invalidate_cache(church_id, ["worship_schedule"])


def invalidate_prayer_cache(church_id: int):
    """기도요청 관련 캐시 무효화"""
    cache_manager.invalidate_cache(church_id, ["prayer_requests"])


def invalidate_pastoral_care_cache(church_id: int):
    """심방요청 관련 캐시 무효화"""
    cache_manager.invalidate_cache(church_id, ["pastoral_care_requests"])