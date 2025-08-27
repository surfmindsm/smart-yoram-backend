"""
교회 데이터 기반 스마트 AI 어시스턴트 서비스

사용자의 질문을 분석하여 적절한 데이터를 조회하고 
맥락에 맞는 AI 응답을 생성합니다.
"""

import logging
import re
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session

# Models
from app.models.pastoral_care import PastoralCareRequest, PrayerRequest
from app.models.announcement import Announcement
from app.models.visit import Visit, VisitPeople
from app.models.user import User
from app.models.member import Member

# Services
from app.services.openai_service import OpenAIService
from app.services.church_data_service import ChurchDataService

logger = logging.getLogger(__name__)


class SmartAssistantService:
    """교회 데이터 기반 스마트 AI 어시스턴트"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.church_data_service = ChurchDataService()
    
    async def process_query(
        self,
        user_message: str,
        church_id: int,
        user_id: int,
        db: Session,
        gpt_config: Dict = None
    ) -> Dict:
        """
        사용자 질문을 처리하여 데이터 기반 AI 응답 생성
        
        Args:
            user_message: 사용자 질문
            church_id: 교회 ID
            user_id: 사용자 ID
            db: 데이터베이스 세션
            gpt_config: GPT 모델 설정
            
        Returns:
            AI 응답과 메타데이터
        """
        try:
            logger.info(f"Processing query for church {church_id}: {user_message}")
            
            # 1. 질문 의도 분석
            query_analysis = self._analyze_query_intent(user_message)
            logger.info(f"Query analysis: {query_analysis}")
            
            # 2. 필요한 데이터 조회
            context_data = await self._gather_context_data(
                query_analysis, church_id, user_id, db
            )
            
            # 3. GPT 프롬프트 구성
            system_prompt = self._build_system_prompt(query_analysis, context_data)
            
            # 4. AI 응답 생성
            gpt_config = gpt_config or {
                "model": "gpt-4o-mini",
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            ai_response = await self.openai_service.generate_response(
                messages=[{"role": "user", "content": user_message}],
                system_prompt=system_prompt,
                **gpt_config
            )
            
            return {
                "response": ai_response["content"],
                "query_type": query_analysis["primary_intent"],
                "data_sources": list(context_data.keys()),
                "tokens_used": ai_response["tokens_used"],
                "model": ai_response["model"]
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": "죄송합니다. 질문을 처리하는 중 오류가 발생했습니다.",
                "error": str(e),
                "query_type": "error",
                "data_sources": [],
                "tokens_used": 0
            }
    
    def _analyze_query_intent(self, message: str) -> Dict:
        """사용자 질문의 의도를 분석하여 필요한 데이터 타입 결정"""
        
        message_lower = message.lower()
        
        # 의도별 키워드 매핑
        intent_patterns = {
            "pastoral_visit_schedule": [
                "심방", "방문", "오늘 일정", "내일 일정", "이번주 일정", "심방 계획",
                "방문 예정", "심방 스케줄", "심방자", "심방 시간"
            ],
            "prayer_requests": [
                "기도", "중보기도", "기도제목", "기도 요청", "기도해주세요", 
                "간구", "기도 부탁", "중보 요청"
            ],
            "member_info": [
                "성도", "교인", "회원", "연락처", "전화번호", "주소", "생일",
                "가족", "성도 정보", "멤버"
            ],
            "announcements": [
                "공지", "알림", "소식", "공지사항", "안내", "알려주세요",
                "새로운 소식", "교회 소식"
            ],
            "visit_reports": [
                "심방 보고", "심방 기록", "방문 기록", "심방 결과", "보고서",
                "심방했던", "방문했던"
            ],
            "donation_info": [
                "헌금", "십일조", "감사헌금", "건축헌금", "재정", "후원",
                "헌금 현황", "재정 상황"
            ],
            "attendance_info": [
                "출석", "참석", "결석", "예배 참여", "출석률", "출석 현황"
            ],
            "schedule_general": [
                "일정", "스케줄", "예정", "계획", "언제", "시간", "날짜"
            ]
        }
        
        # 시간 관련 키워드 분석
        time_indicators = {
            "today": ["오늘", "금일", "today"],
            "tomorrow": ["내일", "명일", "tomorrow"],
            "this_week": ["이번주", "금주", "this week"],
            "this_month": ["이번달", "금월", "this month"],
            "upcoming": ["예정", "앞으로", "다가오는", "upcoming"]
        }
        
        # 우선순위별 의도 검출
        detected_intents = []
        for intent, keywords in intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                detected_intents.append((intent, score))
        
        # 시간 범위 검출
        time_context = "general"
        for time_key, time_words in time_indicators.items():
            if any(word in message_lower for word in time_words):
                time_context = time_key
                break
        
        # 가장 높은 점수의 의도를 주 의도로 설정
        detected_intents.sort(key=lambda x: x[1], reverse=True)
        primary_intent = detected_intents[0][0] if detected_intents else "general_inquiry"
        
        return {
            "primary_intent": primary_intent,
            "secondary_intents": [intent for intent, _ in detected_intents[1:3]],
            "time_context": time_context,
            "confidence": detected_intents[0][1] if detected_intents else 0,
            "original_message": message
        }
    
    async def _gather_context_data(
        self, 
        query_analysis: Dict, 
        church_id: int, 
        user_id: int, 
        db: Session
    ) -> Dict:
        """쿼리 분석 결과를 바탕으로 필요한 데이터 수집"""
        
        context = {}
        primary_intent = query_analysis["primary_intent"]
        time_context = query_analysis["time_context"]
        
        try:
            # 심방 일정 관련
            if primary_intent == "pastoral_visit_schedule":
                context["pastoral_visits"] = await self._get_pastoral_visit_schedule(
                    church_id, time_context, db
                )
            
            # 기도 요청 관련
            elif primary_intent == "prayer_requests":
                context["prayer_requests"] = await self._get_prayer_requests(
                    church_id, db
                )
            
            # 공지사항 관련
            elif primary_intent == "announcements":
                context["announcements"] = await self._get_recent_announcements(
                    church_id, db
                )
            
            # 심방 보고서 관련
            elif primary_intent == "visit_reports":
                context["visit_reports"] = await self._get_visit_reports(
                    church_id, time_context, db
                )
            
            # 성도 정보 관련
            elif primary_intent == "member_info":
                context["member_info"] = await self._get_member_summary(
                    church_id, db
                )
            
            # 일반적인 일정 관련 질문인 경우 여러 데이터 수집
            elif "schedule" in primary_intent:
                context.update({
                    "pastoral_visits": await self._get_pastoral_visit_schedule(church_id, time_context, db),
                    "announcements": await self._get_recent_announcements(church_id, db)
                })
            
        except Exception as e:
            logger.error(f"Error gathering context data: {e}")
            context["error"] = str(e)
        
        return context
    
    async def _get_pastoral_visit_schedule(
        self, church_id: int, time_context: str, db: Session
    ) -> List[Dict]:
        """심방 일정 조회"""
        
        # 시간 필터 설정
        if time_context == "today":
            start_date = date.today()
            end_date = date.today()
        elif time_context == "tomorrow":
            start_date = date.today() + timedelta(days=1)
            end_date = date.today() + timedelta(days=1)
        elif time_context == "this_week":
            start_date = date.today()
            end_date = date.today() + timedelta(days=7)
        else:
            start_date = date.today()
            end_date = date.today() + timedelta(days=30)
        
        visits = db.query(PastoralCareRequest).filter(
            PastoralCareRequest.church_id == church_id,
            PastoralCareRequest.status.in_(["approved", "scheduled"]),
            PastoralCareRequest.scheduled_date >= start_date,
            PastoralCareRequest.scheduled_date <= end_date
        ).order_by(PastoralCareRequest.scheduled_date).all()
        
        result = []
        for visit in visits:
            result.append({
                "id": visit.id,
                "requester_name": visit.requester_name,
                "request_type": visit.request_type,
                "scheduled_date": visit.scheduled_date.isoformat() if visit.scheduled_date else None,
                "scheduled_time": visit.scheduled_time.strftime("%H:%M") if visit.scheduled_time else None,
                "address": visit.address,
                "request_content": visit.request_content[:100] + "..." if visit.request_content and len(visit.request_content) > 100 else visit.request_content,
                "priority": visit.priority,
                "is_urgent": visit.is_urgent
            })
        
        return result
    
    async def _get_prayer_requests(self, church_id: int, db: Session) -> List[Dict]:
        """최근 기도 요청 조회"""
        
        prayers = db.query(PrayerRequest).filter(
            PrayerRequest.church_id == church_id,
            PrayerRequest.status == "active",
            PrayerRequest.is_public == True
        ).order_by(PrayerRequest.created_at.desc()).limit(10).all()
        
        result = []
        for prayer in prayers:
            result.append({
                "id": prayer.id,
                "requester_name": prayer.requester_name if not prayer.is_anonymous else "익명",
                "prayer_type": prayer.prayer_type,
                "prayer_content": prayer.prayer_content[:150] + "..." if prayer.prayer_content and len(prayer.prayer_content) > 150 else prayer.prayer_content,
                "prayer_count": prayer.prayer_count,
                "is_urgent": prayer.is_urgent,
                "created_at": prayer.created_at.strftime("%Y-%m-%d")
            })
        
        return result
    
    async def _get_recent_announcements(self, church_id: int, db: Session) -> List[Dict]:
        """최근 공지사항 조회"""
        
        announcements = db.query(Announcement).filter(
            Announcement.church_id == church_id,
            Announcement.is_active == True
        ).order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).limit(5).all()
        
        result = []
        for announcement in announcements:
            result.append({
                "id": announcement.id,
                "title": announcement.title,
                "content": announcement.content[:200] + "..." if announcement.content and len(announcement.content) > 200 else announcement.content,
                "category": announcement.category,
                "is_pinned": announcement.is_pinned,
                "author_name": announcement.author_name,
                "created_at": announcement.created_at.strftime("%Y-%m-%d")
            })
        
        return result
    
    async def _get_visit_reports(self, church_id: int, time_context: str, db: Session) -> List[Dict]:
        """심방 보고서 조회"""
        
        # 시간 필터
        if time_context == "this_week":
            start_date = date.today() - timedelta(days=7)
        elif time_context == "this_month":
            start_date = date.today() - timedelta(days=30)
        else:
            start_date = date.today() - timedelta(days=14)  # 기본 2주
        
        visits = db.query(Visit).filter(
            Visit.church_id == church_id,
            Visit.date >= start_date
        ).order_by(Visit.date.desc()).limit(10).all()
        
        result = []
        for visit in visits:
            result.append({
                "id": visit.id,
                "date": visit.date.isoformat(),
                "place": visit.place,
                "category_code": visit.category_code,
                "visit_type_code": visit.visit_type_code,
                "scripture": visit.scripture,
                "notes": visit.notes[:150] + "..." if visit.notes and len(visit.notes) > 150 else visit.notes,
                "grade": visit.grade,
                "pastor_comment": visit.pastor_comment[:100] + "..." if visit.pastor_comment and len(visit.pastor_comment) > 100 else visit.pastor_comment
            })
        
        return result
    
    async def _get_member_summary(self, church_id: int, db: Session) -> Dict:
        """성도 요약 정보"""
        
        # 기본 통계만 제공 (개인정보 보호)
        total_members = db.query(User).filter(
            User.church_id == church_id,
            User.is_active == True
        ).count()
        
        return {
            "total_members": total_members,
            "note": "개인정보 보호를 위해 상세 정보는 별도 요청 바랍니다."
        }
    
    def _build_system_prompt(self, query_analysis: Dict, context_data: Dict) -> str:
        """컨텍스트 데이터를 바탕으로 시스템 프롬프트 구성"""
        
        base_prompt = """
당신은 교회 업무를 도와주는 전문 AI 어시스턴트입니다.

# 역할과 책임
- 교회 담임목사, 교역자, 관리자를 위한 업무 지원
- 정확하고 도움이 되는 정보 제공
- 교회 데이터를 활용한 실무적 조언
- 친근하고 존중하는 어조 유지

# 응답 원칙
1. 구체적이고 실용적인 정보 제공
2. 시간, 장소, 연락처 등 세부사항 포함
3. 우선순위나 긴급도가 있다면 명시
4. 개인정보는 필요한 범위에서만 언급
5. 추가 도움이 필요하면 안내

# 현재 문의 유형
{intent}

# 관련 데이터
{context}

위 정보를 바탕으로 사용자의 질문에 도움이 되는 답변을 해주세요.
"""
        
        # 의도별 특별 지시사항
        intent_instructions = {
            "pastoral_visit_schedule": "일정은 시간 순서대로 정리하고, 주소와 특이사항을 포함해주세요.",
            "prayer_requests": "기도 제목은 간결하게 요약하고 긴급한 것부터 우선 언급해주세요.",
            "announcements": "중요한 공지는 먼저 언급하고, 카테고리별로 정리해주세요.",
            "visit_reports": "최근 심방 현황을 요약하고 주목할 점이 있다면 언급해주세요."
        }
        
        primary_intent = query_analysis["primary_intent"]
        intent_instruction = intent_instructions.get(primary_intent, "사용자의 질문에 최대한 도움이 되도록 답변해주세요.")
        
        # 컨텍스트 데이터 포맷팅
        context_text = ""
        for key, value in context_data.items():
            if isinstance(value, list):
                context_text += f"\n## {key.upper()}\n"
                for item in value:
                    context_text += f"- {item}\n"
            elif isinstance(value, dict):
                context_text += f"\n## {key.upper()}\n{value}\n"
            else:
                context_text += f"\n## {key.upper()}\n{value}\n"
        
        return base_prompt.format(
            intent=f"{primary_intent} - {intent_instruction}",
            context=context_text if context_text else "관련 데이터가 없습니다."
        )
    
    def _get_suggested_data_sources(self, query_analysis: Dict) -> List[str]:
        """분석된 의도를 바탕으로 권장 데이터 소스 반환"""
        
        intent_to_sources = {
            "pastoral_visit_schedule": ["pastoral_care_requests"],
            "prayer_requests": ["prayer_requests"],
            "announcements": ["announcements"],
            "visit_reports": ["visits", "visit_people"],
            "member_info": ["users", "members"],
            "donation_info": ["external_church_db"],
            "attendance_info": ["external_church_db"],
            "schedule_general": ["pastoral_care_requests", "announcements"]
        }
        
        primary_intent = query_analysis.get("primary_intent", "general_inquiry")
        return intent_to_sources.get(primary_intent, ["general"])


# 서비스 인스턴스 생성
smart_assistant_service = SmartAssistantService()