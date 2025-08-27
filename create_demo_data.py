#!/usr/bin/env python3
"""
교회 ID 9999 데모 사이트용 목업 데이터 생성 스크립트
"""
import asyncio
from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.announcement import Announcement
from app.models.pastoral_care import PastoralCareRequest, PrayerRequest
from app.models.visit import Visit, VisitPeople
from app.models.user import User
from app.models.church import Church


def create_demo_data():
    """데모 데이터 생성"""
    db = SessionLocal()
    
    try:
        church_id = 9999
        
        # 교회 확인 및 생성
        demo_church = db.query(Church).filter(Church.id == church_id).first()
        if not demo_church:
            demo_church = Church(
                id=church_id,
                name="데모 교회",
                address="서울시 강남구 데모로 123",
                phone="02-1234-5678",
                email="contact@demo.smartyoram.com",
                pastor_name="김목사",
                subscription_status="active",
                subscription_plan="premium",
                member_limit=500,
                is_active=True
            )
            db.add(demo_church)
            db.flush()  # Get the ID
            print(f"✅ 데모 교회 생성: {demo_church.name}")
        else:
            print(f"✅ 데모 교회 확인: {demo_church.name}")
        
        # 관리자 사용자 확인 및 생성
        admin_user = db.query(User).filter(
            User.church_id == church_id,
            User.email == "admin@demo.smartyoram.com"
        ).first()
        
        if not admin_user:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            admin_user = User(
                church_id=church_id,
                email="admin@demo.smartyoram.com",
                username="demo_admin",
                full_name="데모 관리자",
                phone="010-1111-2222",
                role="admin",
                hashed_password=pwd_context.hash("demo123!"),
                is_active=True
            )
            db.add(admin_user)
            db.flush()  # Get the ID
            print(f"✅ 데모 관리자 사용자 생성: {admin_user.full_name} (ID: {admin_user.id})")
        else:
            print(f"✅ 데모 관리자 사용자 확인: {admin_user.full_name} (ID: {admin_user.id})")
        
        # 1. 공지사항 데이터 생성
        create_sample_announcements(db, church_id, admin_user.id)
        
        # 2. 심방 요청 데이터 생성  
        create_sample_pastoral_care_requests(db, church_id, admin_user.id)
        
        # 3. 중보기도 요청 데이터 생성
        create_sample_prayer_requests(db, church_id, admin_user.id)
        
        # 4. 심방 기록 데이터 생성
        create_sample_visits(db, church_id)
        
        db.commit()
        print("🎉 데모 데이터 생성 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_sample_announcements(db: Session, church_id: int, author_id: int):
    """공지사항 샘플 데이터 생성"""
    print("📢 공지사항 데모 데이터 생성 중...")
    
    announcements = [
        {
            "title": "2024년 송구영신 예배 안내",
            "content": "올해 송구영신 예배를 12월 31일 오후 11시부터 진행합니다.\n\n📍 장소: 본당\n⏰ 시간: 오후 11:00 ~ 새벽 1:00\n🎵 특별찬양: 청년부, 성가대\n\n하나님께서 허락하신 한 해를 감사하며, 새해를 주님께 맡겨드리는 귀한 시간이 되길 바랍니다.",
            "category": "worship",
            "subcategory": "special_service",
            "target_audience": "all",
            "is_pinned": True,
        },
        {
            "title": "새해 새벽기도회 시작",
            "content": "새해를 맞아 새벽기도회를 시작합니다.\n\n📅 기간: 2024년 1월 1일 ~ 1월 21일 (3주간)\n⏰ 시간: 새벽 5:30 ~ 6:30\n📖 말씀: 시편 묵상\n\n새해 첫 시작을 하나님과 함께하는 성도님들의 많은 참여 바랍니다.",
            "category": "worship",
            "subcategory": "prayer_meeting",
            "target_audience": "all",
            "is_pinned": True,
        },
        {
            "title": "청년부 겨울수련회 모집",
            "content": "청년부 겨울수련회를 개최합니다!\n\n📅 일정: 2024년 1월 26일(금) ~ 28일(일) 2박 3일\n📍 장소: 평창 수련원\n💰 참가비: 12만원 (교통비, 숙박비, 식비 포함)\n📝 신청: 1월 14일까지 청년부 단톡방 또는 김목사님께\n\n'새해, 새로운 비전'을 주제로 진행됩니다. 청년들의 많은 참여 바랍니다!",
            "category": "event",
            "subcategory": "retreat",
            "target_audience": "youth",
            "is_pinned": False,
        },
        {
            "title": "김영희 성도 아들 대학 합격 감사",
            "content": "김영희 성도의 아들 김준호 형제가 서울대학교 공학부에 합격했습니다.\n\n그동안 기도해 주신 모든 성도님들께 감사드리며, 하나님께서 허락하신 은혜에 감사드립니다.\n\n앞으로도 하나님의 영광을 위해 살아가는 청년으로 성장할 수 있도록 계속 기도 부탁드립니다.",
            "category": "member_news",
            "subcategory": "thanksgiving",
            "target_audience": "all",
            "is_pinned": False,
        },
        {
            "title": "교회 주차장 이용 안내",
            "content": "주일 예배시 원활한 주차를 위해 다음 사항을 안내드립니다.\n\n• 오전 9시 이전 도착 시: 1층 주차장 이용 가능\n• 오전 9시 이후 도착 시: 지하 주차장 또는 인근 공영주차장 이용\n• 장애인 및 거동 불편한 성도: 교회 앞 전용 주차구역 이용\n\n서로 배려하는 마음으로 질서있는 주차 부탁드립니다.",
            "category": "general",
            "subcategory": "facility",
            "target_audience": "all",
            "is_pinned": False,
        }
    ]
    
    for announcement_data in announcements:
        announcement = Announcement(
            church_id=church_id,
            author_id=author_id,
            author_name="데모 관리자",
            **announcement_data
        )
        db.add(announcement)
    
    print("✅ 공지사항 5개 생성 완료")


def create_sample_pastoral_care_requests(db: Session, church_id: int, user_id: int):
    """심방 요청 샘플 데이터 생성"""
    print("🏠 심방 요청 데모 데이터 생성 중...")
    
    requests = [
        {
            "member_id": user_id,
            "requester_name": "박은미",
            "requester_phone": "010-2345-6789",
            "request_type": "hospital",
            "request_content": "어머님이 갑자기 입원하셔서 많이 힘들어하고 계십니다. 가족들과 함께 기도해 주시고 위로의 말씀을 전해주시면 감사하겠습니다.",
            "preferred_date": date.today() + timedelta(days=2),
            "preferred_time_start": time(14, 0),
            "preferred_time_end": time(16, 0),
            "status": "pending",
            "priority": "high",
            "address": "서울시 강남구 논현동 삼성서울병원 12층 1203호",
            "contact_info": "병실 직통전화: 02-3410-1203",
            "is_urgent": True
        },
        {
            "member_id": user_id,
            "requester_name": "이정수",
            "requester_phone": "010-3456-7890",
            "request_type": "counseling",
            "request_content": "직장에서 어려운 일이 생겨서 많이 스트레스받고 있습니다. 신앙적인 조언을 듣고 싶어서 심방을 요청드립니다.",
            "preferred_date": date.today() + timedelta(days=5),
            "preferred_time_start": time(19, 0),
            "preferred_time_end": time(21, 0),
            "status": "approved",
            "priority": "normal",
            "address": "서울시 서초구 서초동 123-45 아파트 101동 503호",
            "contact_info": "평일 오후 7시 이후 연락 가능",
            "is_urgent": False
        },
        {
            "member_id": user_id,
            "requester_name": "최민호",
            "requester_phone": "010-4567-8901",
            "request_type": "general",
            "request_content": "결혼 1주년을 맞아 새 집으로 이사했습니다. 새 집을 축복해 주시고 가정예배를 드리고 싶습니다.",
            "preferred_date": date.today() + timedelta(days=7),
            "preferred_time_start": time(15, 0),
            "preferred_time_end": time(17, 0),
            "status": "scheduled",
            "priority": "normal",
            "scheduled_date": date.today() + timedelta(days=7),
            "scheduled_time": time(15, 30),
            "address": "경기도 성남시 분당구 정자동 456-78 신축아파트 205동 1204호",
            "contact_info": "주말 언제든 가능",
            "is_urgent": False
        },
        {
            "member_id": user_id,
            "requester_name": "김나영",
            "requester_phone": "010-5678-9012",
            "request_type": "urgent",
            "request_content": "아버님이 갑자기 쓰러지셔서 중환자실에 계십니다. 가족들이 모두 불안해하고 있어서 급히 기도 부탁드립니다.",
            "preferred_date": date.today() + timedelta(days=1),
            "preferred_time_start": time(10, 0),
            "preferred_time_end": time(12, 0),
            "status": "completed",
            "priority": "urgent",
            "scheduled_date": date.today(),
            "scheduled_time": time(16, 0),
            "completion_notes": "가족들과 함께 기도하며 위로의 시간을 가졌습니다. 아버님의 상태가 많이 호전되어 감사드립니다.",
            "address": "서울시 용산구 한남동 대형병원 중환자실",
            "contact_info": "면회시간: 오후 2-6시, 저녁 7-9시",
            "is_urgent": True,
            "completed_at": datetime.now() - timedelta(days=1)
        }
    ]
    
    for request_data in requests:
        request = PastoralCareRequest(
            church_id=church_id,
            **request_data
        )
        db.add(request)
    
    print("✅ 심방 요청 4개 생성 완료")


def create_sample_prayer_requests(db: Session, church_id: int, user_id: int):
    """중보기도 요청 샘플 데이터 생성"""
    print("🙏 중보기도 요청 데모 데이터 생성 중...")
    
    prayers = [
        {
            "member_id": user_id,
            "requester_name": "홍길동",
            "requester_phone": "010-1111-2222",
            "prayer_type": "healing",
            "prayer_content": "어머님이 당뇨 합병증으로 고생하고 계십니다. 치료가 잘 되어 건강을 회복하시도록 기도 부탁드립니다.",
            "is_anonymous": False,
            "is_urgent": False,
            "status": "active",
            "is_public": True,
            "prayer_count": 15,
            "expires_at": datetime.now() + timedelta(days=30)
        },
        {
            "member_id": user_id,
            "requester_name": "이름없음",
            "requester_phone": None,
            "prayer_type": "family",
            "prayer_content": "큰아들이 취업 준비를 하고 있는데 계속 떨어져서 많이 좌절하고 있습니다. 하나님의 때에 좋은 회사에 취업할 수 있도록 기도해 주세요.",
            "is_anonymous": True,
            "is_urgent": False,
            "status": "active",
            "is_public": True,
            "prayer_count": 23,
            "expires_at": datetime.now() + timedelta(days=30)
        },
        {
            "member_id": user_id,
            "requester_name": "박믿음",
            "requester_phone": "010-2222-3333",
            "prayer_type": "thanksgiving",
            "prayer_content": "딸이 무사히 출산했습니다! 건강한 손녀를 허락해 주신 하나님께 감사드립니다. 산모와 아기가 건강하게 자랄 수 있도록 계속 기도 부탁드립니다.",
            "is_anonymous": False,
            "is_urgent": False,
            "status": "answered",
            "is_public": True,
            "answered_testimony": "하나님의 은혜로 딸과 손녀가 모두 건강합니다. 기도해 주신 모든 분들께 감사드립니다.",
            "prayer_count": 31,
            "closed_at": datetime.now() - timedelta(days=3),
            "expires_at": datetime.now() + timedelta(days=7)
        },
        {
            "member_id": user_id,
            "requester_name": "김소망",
            "requester_phone": "010-3333-4444",
            "prayer_type": "work",
            "prayer_content": "새로 시작한 사업이 어려움에 처해 있습니다. 하나님의 도우심으로 사업이 잘 되어 직원들 월급도 제때 줄 수 있도록 기도 부탁드립니다.",
            "is_anonymous": False,
            "is_urgent": True,
            "status": "active",
            "is_public": True,
            "prayer_count": 8,
            "expires_at": datetime.now() + timedelta(days=30)
        },
        {
            "member_id": user_id,
            "requester_name": "최평안",
            "requester_phone": "010-4444-5555",
            "prayer_type": "spiritual",
            "prayer_content": "신앙생활이 침체되어 있습니다. 말씀을 읽어도 은혜가 되지 않고 기도도 형식적으로 하게 됩니다. 다시 뜨거운 믿음을 회복할 수 있도록 기도해 주세요.",
            "is_anonymous": False,
            "is_urgent": False,
            "status": "active",
            "is_public": False,
            "admin_notes": "개인적인 신앙 고민이므로 비공개 처리",
            "prayer_count": 5,
            "expires_at": datetime.now() + timedelta(days=30)
        }
    ]
    
    for prayer_data in prayers:
        prayer = PrayerRequest(
            church_id=church_id,
            **prayer_data
        )
        db.add(prayer)
    
    print("✅ 중보기도 요청 5개 생성 완료")


def create_sample_visits(db: Session, church_id: int):
    """심방 기록 샘플 데이터 생성"""
    print("📝 심방 기록 데모 데이터 생성 중...")
    
    visits = [
        {
            "date": date.today() - timedelta(days=7),
            "place": "김영희 성도댁",
            "term_year": 2024,
            "term_unit": "1학기",
            "category_code": "가정심방",
            "visit_type_code": "방문심방",
            "hymn_no": "찬송가 310장",
            "scripture": "시편 23편 1-6절",
            "notes": "새해 인사 및 가정 근황 파악. 아들 대학 합격으로 인한 감사 인사. 올해 신앙 계획에 대해 이야기하며 격려.",
            "grade": "A",
            "pastor_comment": "믿음이 좋고 적극적으로 교회 활동에 참여하는 가정. 계속 격려와 관심 필요."
        },
        {
            "date": date.today() - timedelta(days=5),
            "place": "분당서울대병원 1203호",
            "term_year": 2024,
            "term_unit": "1학기",
            "category_code": "병원심방",
            "visit_type_code": "방문심방",
            "hymn_no": "찬송가 405장",
            "scripture": "로마서 8장 28절",
            "notes": "박은미 성도 어머님 문병. 수술 후 회복 중이시며 가족들과 함께 기도. 하나님의 치유하심을 구하는 시간.",
            "grade": "B+",
            "pastor_comment": "환자분이 신자는 아니지만 기도에 협조적. 가족들의 신앙이 더욱 견고해지는 계기가 되기를 기도함."
        },
        {
            "date": date.today() - timedelta(days=3),
            "place": "이정수 성도댁",
            "term_year": 2024,
            "term_unit": "1학기",
            "category_code": "가정심방",
            "visit_type_code": "방문심방",
            "hymn_no": "찬송가 460장",
            "scripture": "빌립보서 4장 6-7절",
            "notes": "직장 문제로 어려움을 겪고 있는 성도 상담 및 격려. 기도와 말씀으로 위로하며 하나님께 맡기도록 권면.",
            "grade": "A-",
            "pastor_comment": "진실한 성도로 어려운 상황에서도 신앙을 지키려고 노력함. 지속적인 관심과 기도 필요."
        },
        {
            "date": date.today() - timedelta(days=1),
            "place": "최민호 성도 신혼집",
            "term_year": 2024,
            "term_unit": "1학기",
            "category_code": "가정심방",
            "visit_type_code": "방문심방",
            "hymn_no": "찬송가 585장",
            "scripture": "여호수아 24장 15절",
            "notes": "새집으로 이사한 신혼부부 축복 기도. 가정 예배드리며 신앙으로 가정을 세워가도록 격려.",
            "grade": "A+",
            "pastor_comment": "젊은 신혼부부로 신앙에 대한 열정이 좋음. 가정 예배 정착을 위해 지속적으로 도움 제공 필요."
        }
    ]
    
    for visit_data in visits:
        visit = Visit(
            church_id=church_id,
            **visit_data
        )
        db.add(visit)
    
    print("✅ 심방 기록 4개 생성 완료")


if __name__ == "__main__":
    create_demo_data()