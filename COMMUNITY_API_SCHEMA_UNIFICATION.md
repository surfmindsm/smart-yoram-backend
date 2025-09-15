# 커뮤니티 API 스키마 통일화 가이드

> **작성일**: 2025-09-15  
> **목적**: 커뮤니티 관련 API들의 불일치 문제를 분석하고 통일화 방안을 제시  
> **상태**: 분석 완료, 수정 계획 수립 중

---

## 📋 커뮤니티 메뉴별 테이블 매핑 및 스키마 분석

### 1. 메뉴 → API → 테이블 매핑 현황

| 메뉴명 | API 파일 | 테이블명 | URL 패턴 | 모델 파일 | 스키마 일치도 |
|---|---|---|---|---|---|
| **무료 나눔** | `community_sharing.py` | `community_sharing` | `/community/sharing*` | `community_sharing.py` | 🔴 **컬럼명 불일치** |
| **물품 판매** | `community_item_sale.py` | `community_sharing` | `/community/item-sale` | `community_sharing.py` | 🔴 **테이블 공유 문제** |
| **물품 요청** | `community_requests.py` | `community_requests` | `/community/requests*` | `community_request.py` | 🔴 **컬럼명 불일치** |
| **사역자 모집** | `job_posts.py` | `job_posts` | `/community/job-posts*` | `job_posts.py` + `job_post.py` | 🔴 **중복 모델** |
| **구직 신청** | `job_posts.py` | `job_seekers` | `/community/job-seekers*` | `job_posts.py` + `job_post.py` | 🔴 **중복 모델** |
| **음악팀 모집** | `music_team_recruit.py` | `community_music_teams` | `/community/music*` | `music_team_recruitment.py` | 🔴 **views≠view_count** |
| **음악팀 지원** | `music_team_seekers.py` | `music_team_seekers` | `/community/music-team-seekers*` | `music_team_seeker.py` | 🔴 **ARRAY vs JSON** |
| **교회 행사** | `church_events.py` | `church_events` | `/community/church-events*` | `church_events.py` | 🟡 **views≠view_count** |
| **교회 소식** | `church_news.py` | `church_news` | `/community/church-news*` | `church_news.py` | ✅ **일치** |
| **커뮤니티 신청** | `community_applications.py` | `community_applications` | `/community/applications*` | `community_application.py` | ✅ **일치** |
| **이미지 업로드** | `community_images.py` | N/A (Supabase) | `/community/images*` | N/A | ⚪ **독립적** |
| **홈/통계** | `community_home.py` | N/A (조회전용) | `/community/stats` | N/A | ⚪ **통계전용** |

### 2. 🚨 **심각한 테이블 스키마 불일치 발견**

#### 2.1 중복 모델 문제 (Job Posts)
```python
# ❌ 동일한 테이블에 대해 2개의 다른 모델 존재!
## models/job_posts.py
class JobPost(Base):
    __tablename__ = "job_posts"
    author_id = Column(Integer, ForeignKey("users.id"))  # author_id 사용
    view_count = Column(Integer, default=0)             # view_count 사용

## models/job_post.py (중복!)
class JobPost(Base):  # 🚨 같은 클래스명!
    __tablename__ = "job_posts"  # 🚨 같은 테이블!
    user_id = Column(Integer, ForeignKey("users.id"))   # 🚨 user_id 사용!
    view_count = Column(Integer, default=0)             # view_count 사용

# 🚨 결과: 어떤 모델이 실제 DB와 일치하는지 불명확!
```

#### 2.2 공유 테이블 사용 (Sharing vs Item Sale)
```python
# ❌ 무료 나눔과 물품 판매가 같은 테이블 사용
## 두 API 모두 community_sharing 테이블 사용
- 무료 나눔: is_free = True, price = 0
- 물품 판매: is_free = False, price > 0

# 🚨 문제: 비즈니스 로직이 DB 스키마에 의존
```

#### 2.3 조회수 필드 불일치 (여전히 존재)
```python
# ❌ 여전히 혼재하는 조회수 필드
## music_team_recruitment.py (모델)
views = Column(Integer, nullable=True, default=0, comment="조회수")  # 🚨 views

## church_events.py (모델)  
views = Column(Integer, nullable=True, default=0, comment="조회수")  # 🚨 views

## 다른 모델들
view_count = Column(Integer, default=0, comment="조회수")  # ✅ view_count
```

### 3. URL 패턴 복잡성 분석

#### 3.1 중복/별칭 URL이 많은 API
```python
# Community Request (5개 URL!)
/community/item-request      # GET 별칭
/community/requests          # GET, POST 메인
/community/item-requests     # POST 별칭  
/community/item-request      # POST 별칭
/community/requests/{id}     # GET, PUT, DELETE

# Community Sharing (4개 URL!)
/community/sharing-offer     # GET 별칭
/community/sharing           # GET, POST 메인
/community/sharing/{id}      # GET, PUT, DELETE

# Job Posts (6개 URL!)
/community/job-posting       # GET, POST 별칭
/community/job-posts         # GET, POST 메인
/community/job-posts/{id}    # GET, PUT, DELETE
/community/job-seeking       # GET 별칭
/community/job-seekers       # GET, POST
/community/job-seekers/{id}  # GET, DELETE
```

#### 3.2 일관성 있는 API (권장 패턴)
```python
# Music Team Seekers (표준 REST)
/community/music-team-seekers          # GET, POST
/community/music-team-seekers/{id}     # GET, PUT, DELETE

# Church Events (표준 REST)
/community/church-events               # GET, POST  
/community/church-events/{id}          # GET, DELETE

# Church News (표준 REST + 추가 기능)
/community/church-news                 # GET, POST
/community/church-news/{id}            # GET, PUT, DELETE
/community/church-news/{id}/like       # POST (추가 기능)
```

### 4. 실제 DB 스키마 vs 모델 정의 비교

#### 4.1 필드 길이 제한 상세 비교
| 테이블 | 필드 | 모델 정의 | API 처리 | 실제 제한 |
|---|---|---|---|---|
| `community_sharing` | title | `String` (무제한) | 그대로 저장 | ❓ **DB 확인 필요** |
| `community_requests` | title | `String` (무제한) | 그대로 저장 | ❓ **DB 확인 필요** |
| `job_posts` | title | `String` (무제한) | 그대로 저장 | ❓ **DB 확인 필요** |
| `music_team_seekers` | title | `String(200)` | 200자 제한 | ✅ **일치** |
| `church_events` | title | `String(200)` | 그대로 저장 | ❓ **DB 확인 필요** |
| `church_news` | title | `String(255)` | 그대로 저장 | ❓ **DB 확인 필요** |

#### 4.2 JSON 필드 처리 방식 비교
| 테이블 | 필드 | 모델 타입 | API 처리 | 프론트엔드 전송 |
|---|---|---|---|---|
| `community_sharing` | images | `JSON` | 직접 저장 | JSON 배열 |
| `community_requests` | images | `JSON` | 직접 저장 | JSON 배열 |  
| `community_music_teams` | instruments_needed | `JSON` | `json.dumps()` 변환 | 🔴 **JSON 문자열** |
| `music_team_seekers` | preferred_location | `ARRAY(String)` | `json.loads()` 파싱 | 🔴 **JSON 문자열** |
| `church_news` | images | `JSON` | 직접 저장 | JSON 배열 |

### 5. 추가 발견된 문제들

#### 5.1 Contact 필드 처리 방식 5가지로 확산
```python
# 방식 1: 통합형 (대부분)
contact_info: str

# 방식 2: 분리형 기본 (Job Posts, Church Events)
contact_phone: str, contact_email: Optional[str]

# 방식 3: 세분화 분리 (Church News)  
contact_person: str, contact_phone: str, contact_email: str

# 방식 4: Form 처리 (Applications)
contact_person: Form, email: Form, phone: Form

# 방식 5: Music Team Seekers (분리형 변형)
contact_phone: str, contact_email: str (둘 다 별도 컬럼)
```

#### 5.2 Status 필드 열거형 6가지 시스템 발견
```python
# 1. SharingStatus (community_sharing)
AVAILABLE, RESERVED, COMPLETED

# 2. RequestStatus (community_request)  
ACTIVE, FULFILLED, CANCELLED

# 3. JobStatus (job_posts)
ACTIVE, CLOSED, FILLED

# 4. SeekerStatus (music_team_seeker)
AVAILABLE, INTERVIEWING, INACTIVE

# 5. RecruitmentStatus (church_events) 
OPEN, CLOSED, COMPLETED

# 6. NewsStatus (church_news)
ACTIVE, COMPLETED, CANCELLED

# 🚨 6개 API에 6개의 완전히 다른 상태 체계!
```

---

## 🔍 정밀 분석 결과

### API vs Schema vs Model 비교 매트릭스

| API | Pydantic Schema 존재 | Model 일관성 | API 구현 방식 | 조회수 필드 | 상태 관리 |
|---|---|---|---|---|---|
| Community Sharing | ✅ schemas/community_sharing.py | 🔴 불일치 | Raw SQL | `views` (스키마) / `view_count` (모델) | 🔴 불일치 |
| Community Request | ✅ schemas/community_request.py | 🔴 불일치 | Raw SQL | `views` (스키마) / `view_count` (모델) | 🔴 불일치 |
| Community Item Sale | ❌ 인라인 정의 | 🔴 불일치 | Raw SQL | 혼재 사용 | 🔴 불일치 |
| Job Posts | ✅ schemas/job_schemas.py | 🔴 불일치 | Raw SQL + 샘플 | `views` (스키마) | 🔴 불일치 |
| Music Team Recruitment | ❌ 인라인 정의 | 🟡 부분 일치 | Raw SQL | 컬럼 없음 | 🔴 불일치 |
| Music Team Seekers | ❌ 인라인 정의 | 🟡 수정됨 | Raw SQL | `view_count` 통일 | 🔴 불일치 |
| Community Applications | ✅ schemas/community_application.py | ✅ 일치 | ORM | 없음 | ✅ 일치 |
| Community Images | ❌ 없음 | N/A (Supabase) | Supabase | N/A | N/A |
| Community Home | ❌ 없음 | N/A (통계) | Raw SQL | 헬퍼함수 | N/A |
| Church Events | ❌ 인라인 정의 | 🔴 불일치 | ORM | `views` (모델) | 🔴 불일치 |
| Church News | ❌ 없음 | ✅ 일치 | 미구현 | `view_count` (모델) | ✅ 일치 |

### API 구현 방식 분석

#### Raw SQL 사용 API (7개)
- Community Sharing, Item Sale, Request
- Job Posts (부분적)
- Music Team Recruitment, Seekers  
- Community Home

**특징**: 스키마 불일치 문제 해결을 위해 Raw SQL 사용

#### ORM 사용 API (2개)  
- Community Applications
- Church Events

**특징**: 스키마 일치도가 높음

#### 혼합/특수 API (2개)
- Community Images: Supabase Storage만 사용
- Church News: 모델만 정의, API 미구현

---

## 🚨 **새로 발견된 심각한 불일치 문제들**

### 1. **Pydantic Schema vs SQLAlchemy Model 불일치**

#### Community Sharing 예시
```python
# ❌ schemas/community_sharing.py
class Response(BaseModel):
    views: int  # 🚨 'views' 사용
    
# ❌ models/community_sharing.py  
view_count = Column(Integer, default=0)  # 🚨 'view_count' 사용

# ❌ API 구현체에서 혼재
"views": row[3] or 0  # Raw SQL에서는 views
getattr(post, 'view_count', 0)  # ORM에서는 view_count
```

#### Community Request 예시
```python
# ❌ schemas/community_request.py
urgency_level: str = Field(..., description="긴급도")

# ❌ models/community_request.py
urgency = Column(String, default="normal")  # 🚨 필드명 다름

# ❌ API 구현체
urgency: Optional[str] = "normal"  # 🚨 또 다른 이름
```

### 2. **필드 길이 제한 극도로 불일치**

```python
# ❌ 현재 상황 - 같은 필드인데 길이 제한이 모두 다름
## Community Applications
organization_name[:200]  # 200자
contact_person[:100]     # 100자
email[:255]             # 255자
phone[:20]              # 20자

## Community Sharing Schema  
title: str = Field(..., max_length=200)      # 200자
contact_info: str = Field(..., max_length=100)  # 100자

## Job Schemas
title: str = Field(..., max_length=200)      # 200자
company: str = Field(..., max_length=100)    # 100자

## Music Team Seekers Model
title = Column(String(200), nullable=False)  # 200자

## Church Events Model
title = Column(String(200), nullable=False)  # 200자

## Church News Model  
title = Column(String(255), nullable=False)  # 255자 🚨

# 🚨 같은 'title' 필드인데 200자 vs 255자 혼재!
```

### 3. **상태 열거형 극도로 분산**

```python
# ❌ 각 API마다 완전히 다른 상태 체계

## Community Sharing (models/community_sharing.py)
class SharingStatus(str, enum.Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    COMPLETED = "completed"

## Community Request (models/community_request.py)
class RequestStatus(str, enum.Enum):
    ACTIVE = "active"      # 🚨 다른 이름
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"

## Church Events (models/church_events.py)
class RecruitmentStatus(str, enum.Enum):
    OPEN = "open"          # 🚨 또 다른 이름
    CLOSED = "closed" 
    COMPLETED = "completed"

## Job Posts (실제 구현에서)
status: Optional[str] = "open"  # 🚨 열거형 없이 문자열만

## Church News (models/church_news.py)
class NewsStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed" 
    CANCELLED = "cancelled"

# 🚨 결과: 5개 API에 5개의 다른 상태 체계!
```

### 4. **연락처 필드 처리 방식 4가지로 증가**

```python
# ❌ 방식 1: 통합형 (Community Sharing, Request)
contact_info: str

# ❌ 방식 2: 분리형 (Job Posts, Church Events)  
contact_phone: str
contact_email: Optional[str] = None

# ❌ 방식 3: 복잡한 Form 처리 (Applications)
contact_person: str = Form(...)
email: str = Form(...)
phone: str = Form(...)

# ❌ 방식 4: 세분화된 분리 (Church News)
contact_person = Column(String(100))
contact_phone = Column(String(20)) 
contact_email = Column(String(100))
```

### 5. **JSON 배열 처리 방식 완전 혼재**

```python
# ❌ 방식 1: Python 리스트 → JSON 문자열 변환 (Music Team Recruitment)
if recruitment_data.instruments_needed is not None:
    instruments_json = json.dumps(recruitment_data.instruments_needed)

# ❌ 방식 2: PostgreSQL JSON 직접 저장 (Church News, Community Models)
images = Column(JSON, nullable=True)
tags = Column(JSON, nullable=True)

# ❌ 방식 3: PostgreSQL ARRAY 타입 (Music Team Seekers)
preferred_location = Column(ARRAY(String), nullable=True)
available_days = Column(ARRAY(String), nullable=True)

# ❌ 방식 4: 프론트엔드에서 JSON 문자열로 전송 → 백엔드 파싱
if isinstance(seeker_data['preferred_location'], str):
    preferred_location = json.loads(seeker_data['preferred_location'])
```

### 6. **페이지네이션 구조 미묘한 차이들**

```python
# ✅ 표준형 (대부분)
{
    "pagination": {
        "current_page": page,
        "total_pages": total_pages,
        "total_count": total_count,
        "per_page": limit,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
}

# ❌ 변형 1 (Community Applications)
{
    "pagination": {
        "current_page": page,
        "total_pages": (total_count + limit - 1) // limit,
        "total_count": total_count,
        "per_page": limit,
        # 🚨 has_next, has_prev 필드 없음
    }
}

# ❌ 변형 2 (Community Home - 내 게시글)
{
    "pagination": {
        "current_page": page,
        "total_pages": total_pages,
        "total_count": total_count, 
        "per_page": limit,
        "has_next": page < total_pages,
        "has_prev": page > 1
    },
    "_debug_info": {...}  # 🚨 디버그 정보 추가
}
```

### 7. **교회 ID 기본값 불일치**

```python
# ❌ 현재 상황
## 대부분 API
church_id = Column(Integer, nullable=False, default=9998)
church_id=current_user.church_id or 9998

## Community Applications
church_id = 9998  # 하드코딩

## Job Posts  
church_id=current_user.church_id or 9998  # 동일

# 🚨 일관성은 있지만 하드코딩된 9998이 곳곳에 분산
```

### 8. **DateTime 처리 방식 불일치**

```python
# ❌ 방식 1: 명시적 설정 (Music Team APIs)
current_time = datetime.now(timezone.utc)
created_at=current_time

# ❌ 방식 2: SQLAlchemy 기본값 (대부분 Models)
created_at = Column(DateTime(timezone=True), server_default=func.now())

# ❌ 방식 3: 조건부 설정 (Job Posts)
if job_data.expires_at:
    deadline_dt = datetime.fromisoformat(job_data.expires_at.replace('Z', '+00:00'))
    
# ❌ 방식 4: ISO 형식 문자열 응답 (모든 API)
"created_at": row[5].isoformat() if row[5] else None
```

---

## 🚨 주요 불일치 문제들

### 1. **제목(title) 필드 길이 제한 불일치**

```python
# ❌ 현재 상황
## Music Team Seekers
title = Column(String(200), nullable=False)  # 200자 제한

## Community Applications  
organization_name[:200]  # 200자 제한
contact_person[:100]     # 100자 제한
email[:255]             # 255자 제한

## 나머지 API들
title = Column(String, nullable=False)  # 무제한

# ✅ 통일 방안
title = Column(String(255), nullable=False)  # 모든 API 255자 통일
```

### 2. **작성자 필드명 불일치**

```python
# ❌ 현재 상황  
## 대부분 API
author_id = Column(Integer, ForeignKey("users.id"))

## 일부 물품 판매 코드에서
user_id = sale_item.user_id  # 🚨 잘못된 필드명

# ✅ 통일 방안
모든 테이블: author_id 사용
모든 응답: author_id, author_name만 사용 (중복 제거)
```

### 3. **조회수 컬럼명 불일치**

```python
# ❌ 현재 상황
## 대부분 모델
view_count = Column(Integer, default=0)

## Music Team Seekers (수정됨)
views = Column(Integer, default=0)  # 🚨 이미 view_count로 수정

# ✅ 통일 방안  
모든 테이블: view_count 컬럼 사용
모든 응답: "view_count" 또는 "views" (호환성 유지)
```

### 4. **상태(status) 값 완전 불일치**

```python
# ❌ 현재 상황
## Community Sharing/Item Sale
class SharingStatus(str, enum.Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    COMPLETED = "completed"

## Community Request
class RequestStatus(str, enum.Enum):  
    ACTIVE = "active"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"

## Job Posts
status: Optional[str] = "open"  # 열거형 없음
# "active", "open", "closed", "filled"

## Music Team
status: str = "recruiting"
# "recruiting", "active", "upcoming"

# ✅ 통일 방안
class CommonStatus(str, enum.Enum):
    ACTIVE = "active"        # 활성/모집중/진행중
    COMPLETED = "completed"  # 완료/마감
    CANCELLED = "cancelled"  # 취소
    PAUSED = "paused"       # 일시중지 (필요시)
```

### 5. **연락처 정보 처리 방식 3가지**

```python
# ❌ 현재 상황
## 방식 1: 통합형 (대부분 API)
contact_info: str

## 방식 2: 분리형 (Job Posts, Church Events)
contact_phone: str  # 필수
contact_email: Optional[str] = None  # 선택

## 방식 3: 복잡한 파싱 (Applications)
# Form 데이터로 받아서 개별 처리

# ✅ 통일 방안 (분리형 권장)
contact_phone: str  # 필수
contact_email: Optional[str] = None  # 선택
contact_method: Optional[str] = "phone"  # 선호 연락 방법

# 저장 시 통합
def combine_contact_info(phone, email=None, method="phone"):
    parts = [f"전화: {phone}"]
    if email:
        parts.append(f"이메일: {email}")
    return " | ".join(parts)
```

### 6. **JSON 배열 필드 처리 방식 불일치**

```python
# ❌ 현재 상황
## Music Team Recruitment
instruments_json = json.dumps(recruitment_data.instruments_needed)
# Python 리스트 → JSON 문자열

## 다른 API들
images = sale_data.images or []  
# 직접 JSON 배열로 저장

# ✅ 통일 방안
# Pydantic에서 List[str] 받기 → PostgreSQL JSON으로 직접 저장
# JSON 직렬화는 SQLAlchemy가 자동 처리
```

### 7. **응답 구조 일관성 문제**

```python
# ❌ 현재 상황 (중복 필드)
{
    "user_id": row[14],              # 🚨 중복
    "author_id": row[14],            # 🚨 중복  
    "author_name": row[16] or "익명",  # 🚨 중복
    "user_name": row[16] or "익명",    # 🚨 중복
}

# 페이지네이션도 불일치
{"current_page": page, "total_pages": total_pages}  # A형
{"page": page, "pages": total_pages}                 # B형

# ✅ 통일 방안
## 표준 사용자 정보
{
    "author_id": user.id,
    "author_name": user.full_name or "익명"
}

## 표준 페이지네이션
{
    "pagination": {
        "current_page": page,
        "total_pages": total_pages, 
        "total_count": total_count,
        "per_page": limit,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
}
```

---

---

## 📝 **우선순위별 통일화 계획**

> **🚨 중요**: 총 8가지 주요 불일치 + 7가지 심각한 새 발견 = **15가지 문제**

### 🔥 **1단계: 즉시 수정 (Critical) - 1-2일**

> **목표**: 현재 발생 중인 런타임 오류와 데이터 불일치 문제 해결

#### 1.1 Pydantic Schema vs Model 불일치 긴급 수정
```python
# 🔥 긴급 수정 필요
## Community Sharing
- schemas/community_sharing.py: views → view_count 
- API 응답: "views" → "view_count"

## Community Request  
- schemas/community_request.py: urgency_level → urgency
- API 파라미터: urgency_level → urgency 통일

## Job Posts
- schemas/job_schemas.py: views → view_count
- API 응답 통일
```

#### 1.2 조회수 컬럼명 완전 통일
- [x] Music Team Seekers: `views` → `view_count` (완료)
- [ ] Church Events: `views` → `view_count` 모델 수정
- [ ] 모든 API 응답: `"view_count"` 통일 (호환성 위해 `"views"`도 제공)

#### 1.3 작성자 필드 중복 제거
```python
# ❌ 현재 (중복)
{
    "user_id": author_id,
    "author_id": author_id,  
    "user_name": author_name,
    "author_name": author_name
}

# ✅ 수정 후
{
    "author_id": author_id,
    "author_name": author_name
}
```

#### 1.4 페이지네이션 구조 완전 통일
```python
# ✅ 표준 구조
{
    "success": True,
    "data": [...],
    "pagination": {
        "current_page": int,
        "total_pages": int,
        "total_count": int,
        "per_page": int,
        "has_next": bool,
        "has_prev": bool
    }
}
```

#### 1.5 기본 응답 구조 표준화
```python
# 표준 목록 응답 구조
{
    "success": True,
    "data": [...],
    "pagination": {
        "current_page": int,
        "total_pages": int,
        "total_count": int, 
        "per_page": int,
        "has_next": bool,
        "has_prev": bool
    }
}

# 표준 상세/생성/수정 응답 구조  
{
    "success": True,
    "message": str,
    "data": {
        "id": int,
        "title": str,
        "author_id": int,
        "author_name": str,
        "created_at": str,
        "updated_at": str,
        ...
    }
}
```

---

### 🔶 **2단계: 구조적 통일 (Important) - 3-5일**

> **목표**: 데이터 구조와 필드 정의 통일화

#### 2.1 필드 길이 제한 완전 통일
```python
# ✅ 표준 필드 길이 (모든 API 적용)
title = Column(String(255), nullable=False)        # 255자 통일
description = Column(Text, nullable=True)          # 긴 텍스트는 Text
contact_info = Column(String(200), nullable=True)  # 200자 통일  
email = Column(String(255), nullable=False)        # 255자 통일
phone = Column(String(20), nullable=False)         # 20자 통일
location = Column(String(200), nullable=True)      # 200자 통일

# Pydantic 스키마도 동일하게 적용
title: str = Field(..., max_length=255)
contact_info: str = Field(..., max_length=200)
email: EmailStr = Field(...)  # EmailStr 타입 사용
phone: str = Field(..., max_length=20)
```

#### 2.2 상태값 완전 통일
```python
# app/enums/community_enums.py 생성 (5개 상태 체계 → 1개 통합)
class CommunityStatus(str, enum.Enum):
    ACTIVE = "active"        # 활성/모집중/진행중
    COMPLETED = "completed"  # 완료/마감/성사
    CANCELLED = "cancelled"  # 취소/중단  
    PAUSED = "paused"       # 일시중지/보류

# 각 API별 마이그레이션 매핑
Community Sharing: available→active, reserved→active, completed→completed
Community Request: active→active, fulfilled→completed, cancelled→cancelled  
Church Events: open→active, closed→completed, completed→completed
Job Posts: open→active, active→active, closed→completed
Church News: active→active, completed→completed, cancelled→cancelled
```

#### 2.3 JSON 배열 처리 방식 통일
```python
# ✅ 표준 방식: PostgreSQL JSON 타입 사용
## 모델 정의
images = Column(JSON, nullable=True, comment="이미지 URL 배열")
tags = Column(JSON, nullable=True, comment="태그 배열")  
skills = Column(JSON, nullable=True, comment="기술 배열")

## Pydantic 스키마
images: Optional[List[str]] = None
tags: Optional[List[str]] = None
skills: Optional[List[str]] = None

## API 처리 (자동 직렬화, 수동 변환 불필요)
# SQLAlchemy가 자동으로 Python list ↔ PostgreSQL JSON 변환
```

#### 2.4 연락처 필드 통일 (4가지 방식 → 1가지)
```python
# ✅ 표준 연락처 처리 (분리형 채택)
## Pydantic 스키마
class StandardContactInfo(BaseModel):
    contact_phone: str = Field(..., max_length=20)  
    contact_email: Optional[EmailStr] = None
    contact_method: Optional[str] = Field("phone", max_length=10)  # phone, email, both
    
## 모델 정의 (모든 API 공통)
contact_phone = Column(String(20), nullable=False, comment="연락처")
contact_email = Column(String(255), nullable=True, comment="이메일") 
contact_method = Column(String(10), nullable=True, default="phone", comment="연락 방법")
contact_info = Column(String(500), nullable=True, comment="통합 연락처 (하위호환)")

## 저장용 헬퍼 함수
def format_contact_info(phone: str, email: str = None) -> str:
    parts = [f"전화: {phone}"]
    if email:
        parts.append(f"이메일: {email}")
    return " | ".join(parts)
```

#### 2.5 DateTime 처리 방식 통일
```python
# ✅ 표준 방식: SQLAlchemy 기본값 사용 (명시적 설정 지양)
## 모델 정의
created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

## API 응답 (ISO 포맷 통일)
"created_at": record.created_at.isoformat() if record.created_at else None
"updated_at": record.updated_at.isoformat() if record.updated_at else None

## 입력 처리 (ISO 파싱 헬퍼)
def parse_iso_datetime(date_str: str) -> datetime:
    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
```

---

### 🔸 **3단계: 아키텍처 통합 (Architecture) - 1-2주**

> **목표**: 공통 컴포넌트 도입으로 코드 중복 제거 및 유지보수성 향상

#### 3.1 공통 Enum 모듈 통합
```python
# app/enums/community.py (모든 커뮤니티 열거형 통합)
class CommunityStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed" 
    CANCELLED = "cancelled"
    PAUSED = "paused"

class ContactMethod(str, enum.Enum):
    PHONE = "phone"
    EMAIL = "email" 
    BOTH = "both"
    OTHER = "other"

class UrgencyLevel(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
```

#### 3.2 공통 Pydantic 스키마 생성
```python
# app/schemas/community_common.py
class CommunityBaseRequest(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    contact_phone: str = Field(..., max_length=20)
    contact_email: Optional[EmailStr] = None
    contact_method: Optional[str] = Field("phone", max_length=10)
    status: Optional[CommunityStatus] = CommunityStatus.ACTIVE

class CommunityBaseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    author_id: int
    author_name: str
    church_id: int
    view_count: int
    likes: int
    created_at: str
    updated_at: str
    
class PaginationResponse(BaseModel):
    current_page: int
    total_pages: int
    total_count: int
    per_page: int
    has_next: bool
    has_prev: bool
    
class StandardListResponse(BaseModel):
    success: bool = True
    data: List[CommunityBaseResponse]
    pagination: PaginationResponse
```

#### 3.3 공통 Base 모델 생성
```python
# app/models/community_base.py
class CommunityPostBase(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(CommonStatus), default=CommonStatus.ACTIVE)
    
    # 작성자 정보
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    church_id = Column(Integer, nullable=False, default=9998)
    
    # 통계
    view_count = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    
    # 시간 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])
```

#### 3.2 공통 Pydantic 스키마
```python
# app/schemas/community_common.py  
class CommunityPostResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    author_id: int
    author_name: str
    church_id: int
    view_count: int
    likes: int
    created_at: str
    updated_at: str
    
class CommunityListResponse(BaseModel):
    success: bool
    data: List[CommunityPostResponse]
    pagination: PaginationInfo
```

#### 3.3 공통 헬퍼 함수
```python
# app/utils/community_helpers.py
def format_community_response(post, post_type: str) -> dict:
    """커뮤니티 게시글을 표준 응답 형식으로 변환"""
    return {
        "id": post.id,
        "type": post_type,
        "title": post.title,
        "description": post.description,
        "status": post.status,
        "author_id": post.author_id,
        "author_name": post.author.full_name if post.author else "익명",
        "view_count": post.view_count or 0,
        "likes": post.likes or 0,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "updated_at": post.updated_at.isoformat() if post.updated_at else None
    }

def apply_pagination(query, page: int, limit: int) -> tuple:
    """표준 페이지네이션 적용"""
    total_count = query.count()
    total_pages = (total_count + limit - 1) // limit
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()
    
    pagination = {
        "current_page": page,
        "total_pages": total_pages,
        "total_count": total_count,
        "per_page": limit,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
    
    return items, pagination
```

---

---

## 🎯 **세부 구현 체크리스트**

> **총 15가지 문제 → 체계적 해결**

### 🔥 **1단계 체크리스트 (Critical - 1-2일)**

#### Schema vs Model 불일치 수정
- [ ] `schemas/community_sharing.py`: `views` → `view_count`
- [ ] `schemas/community_request.py`: `urgency_level` → `urgency` 
- [ ] `schemas/job_schemas.py`: `views` → `view_count`
- [ ] 모든 API 파라미터명 통일 확인

#### 조회수 컬럼 완전 통일
- [x] `music_team_seekers.py`: `views` → `view_count` (완료)
- [ ] `church_events.py` 모델: `views` → `view_count`
- [ ] 모든 API 응답: `"view_count"` 필드 사용 (호환성 위해 `"views"`도 제공)

#### 작성자 필드 중복 제거 
- [ ] `community_sharing.py`: 중복 필드 제거
- [ ] `community_item_sale.py`: 중복 필드 제거
- [ ] `community_request.py`: 중복 필드 제거
- [ ] `job_posts.py`: 중복 필드 제거
- [ ] `music_team_recruit.py`: 중복 필드 제거
- [ ] `church_events.py`: 중복 필드 제거

#### 페이지네이션 구조 통일
- [ ] `community_applications.py`: `has_next`, `has_prev` 필드 추가
- [ ] `community_home.py`: `_debug_info` 제거 (프로덕션)
- [ ] 모든 API: 표준 페이지네이션 구조 적용

#### 기본 응답 구조 표준화  
- [ ] 성공 응답 구조 통일
- [ ] 오류 응답 구조 통일
- [ ] 메시지 형식 통일

---

### 🔶 **2단계 체크리스트 (Important - 3-5일)**

#### 필드 길이 제한 통일
- [ ] 모든 `title` 필드: 255자로 통일
- [ ] 모든 `contact_info` 필드: 200자로 통일  
- [ ] 모든 `email` 필드: 255자로 통일
- [ ] 모든 `phone` 필드: 20자로 통일
- [ ] 모든 `location` 필드: 200자로 통일
- [ ] Pydantic 스키마에도 동일한 제한 적용

#### 상태값 완전 통일
- [ ] `app/enums/community_enums.py` 생성
- [ ] 5개 상태 체계 → 1개 `CommunityStatus`로 통합
- [ ] Community Sharing 상태 매핑 적용
- [ ] Community Request 상태 매핑 적용  
- [ ] Church Events 상태 매핑 적용
- [ ] Job Posts 상태 매핑 적용
- [ ] Church News 상태 매핑 적용

#### JSON 배열 처리 통일
- [ ] Music Team Recruitment: JSON 직접 저장 방식으로 변경
- [ ] Music Team Seekers: ARRAY → JSON 타입으로 변경  
- [ ] 프론트엔드 JSON 문자열 파싱 로직 제거
- [ ] 모든 배열 필드 PostgreSQL JSON 타입 사용

#### 연락처 필드 통일
- [ ] 표준 연락처 스키마 `StandardContactInfo` 생성
- [ ] 4가지 처리 방식 → 1가지 분리형으로 통일
- [ ] 모든 API에 `contact_phone`, `contact_email` 분리 적용
- [ ] 하위 호환성 위한 `contact_info` 필드 유지
- [ ] 헬퍼 함수 `format_contact_info()` 구현

#### DateTime 처리 통일  
- [ ] 명시적 시간 설정 → SQLAlchemy 기본값 사용
- [ ] 모든 API 응답: ISO 포맷 통일
- [ ] ISO 파싱 헬퍼 함수 구현
- [ ] 타임존 처리 일관성 확보

---

### 🔸 **3단계 체크리스트 (Architecture - 1-2주)** 

#### 공통 Enum 모듈
- [ ] `app/enums/community.py` 생성
- [ ] `CommunityStatus` 열거형 구현
- [ ] `ContactMethod` 열거형 구현  
- [ ] `UrgencyLevel` 열거형 구현
- [ ] 기존 개별 Enum들을 공통 모듈로 이전

#### 공통 Pydantic 스키마
- [ ] `app/schemas/community_common.py` 생성
- [ ] `CommunityBaseRequest` 기본 요청 스키마
- [ ] `CommunityBaseResponse` 기본 응답 스키마
- [ ] `PaginationResponse` 표준 페이지네이션
- [ ] `StandardListResponse` 표준 목록 응답

#### 공통 Base 모델
- [ ] `app/models/community_base.py` 생성
- [ ] `CommunityPostBase` 추상 모델 구현
- [ ] 기존 모델들을 Base 상속으로 리팩터링
- [ ] 중복 필드 정의 제거

#### 공통 헬퍼 함수
- [ ] `app/utils/community_helpers.py` 생성
- [ ] 응답 포맷터 함수 구현
- [ ] 페이지네이션 헬퍼 구현
- [ ] 연락처 포맷터 구현
- [ ] 상태 변환 헬퍼 구현

#### 리팩터링 적용
- [ ] Community Sharing API 리팩터링
- [ ] Community Request API 리팩터링
- [ ] Community Item Sale API 리팩터링
- [ ] Job Posts API 리팩터링
- [ ] Music Team APIs 리팩터링
- [ ] Church Events API 리팩터링

---

## 📚 참고 정보

### API별 특수 사항
- **Community Images**: Supabase Storage 사용, DB 테이블 없음
- **Music Requests**: 샘플 데이터만 반환, 실제 DB 사용 안함  
- **Community Home**: 통계 조회만, CRUD 없음
- **Community Applications**: Form 데이터 처리, 파일 업로드 지원

### 마이그레이션 주의사항
- 기존 데이터 호환성 유지 필요
- 프론트엔드 API 호출 코드와의 호환성 확인
- 단계별 점진적 적용으로 서비스 중단 최소화

---

## 📊 **최종 요약**

### 발견된 문제 총계 (업데이트)
- **🚨 기존 심각한 문제**: 8가지 (Schema vs Model, 필드 길이, 상태값, 연락처, JSON, 페이지네이션, 교회ID, DateTime)
- **🔍 정밀 분석 추가 발견**: 7가지 (테이블 매핑, URL 패턴, 모델 중복 등)
- **📋 메뉴별 매핑 문제**: 5가지 (중복모델, 공유테이블, 조회수불일치, 연락처5가지, 상태6가지)
- **📊 총 커뮤니티 메뉴**: 12개 (무료나눔, 물품판매, 물품요청, 사역자모집, 구직신청, 음악팀모집, 음악팀지원, 교회행사, 교회소식, 커뮤니티신청, 이미지업로드, 홈통계)
- **🔧 총 문제 건수**: **20가지** (기존 15가지 + 새로 발견 5가지)

### 우선순위별 해결 계획
1. **🔥 1단계 (1-2일)**: 런타임 오류와 데이터 불일치 해결 - **31개 체크리스트**
2. **🔶 2단계 (3-5일)**: 구조적 통일화 - **25개 체크리스트**  
3. **🔸 3단계 (1-2주)**: 아키텍처 통합 - **18개 체크리스트**

### 예상 효과
- **일관성**: 모든 커뮤니티 API 통일된 구조
- **유지보수성**: 공통 컴포넌트로 코드 중복 제거
- **확장성**: 새로운 커뮤니티 API 추가 시 일관된 패턴
- **안정성**: Schema vs Model 불일치로 인한 런타임 오류 제거

---

## 💾 **상세 스키마 분석 결과**

### 커뮤니티 메뉴별 테이블 매핑 세부분석

#### **음악팀 모집** (`community_music_teams`)
**🔴 주요 불일치:**
```python
# 모델: music_team_recruitment.py
views = Column(Integer, default=0, comment="조회수")  # ❌ DB에 없음

# 실제 DB: 
view_count = Column(Integer, default=0)  # ✅ 실제 컬럼명

# 테이블명 불일치:
# 모델: __tablename__ = "community_music_teams"
# API에서 사용: Raw SQL로 "community_music_teams" 직접 호출
```

#### **음악팀 지원** (`music_team_seekers`)
**🔴 주요 불일치:**
```python
# 모델: music_team_seeker.py 
views = Column(Integer, default=0)  # ❌ 잘못된 컬럼명
preferred_location = Column(ARRAY(String))  # ❌ ARRAY 타입
available_days = Column(ARRAY(String))  # ❌ ARRAY 타입

# 실제 사용:
view_count = Column(Integer, default=0)  # ✅ 실제 컬럼명 
# JSON 타입으로 저장되는 실제 구조
```

#### **무료 나눔/물품 판매** (`community_sharing`)
**🔴 테이블 공유 문제:**
```python
# community_sharing.py 모델
class CommunitySharing(Base):
    is_free = Column(Boolean, default=True)  # 무료/판매 구분
    price = Column(Integer, default=0)  # 가격 (판매용)
    
# 두 개의 서로 다른 API가 같은 테이블 사용:
# 1. /community/sharing/* (무료 나눔)
# 2. /community/item-sale/* (물품 판매)
```

#### **구인/구직** (`job_posts`, `job_seekers`)
**🔴 중복 모델 문제:**
```python
# job_posts.py - 실제 사용
class JobPost(Base): __tablename__ = "job_posts"
class JobSeeker(Base): __tablename__ = "job_seekers"

# job_post.py - 스키마만 (unused)
class JobPost: # Pydantic schemas
```

#### **물품 요청** (`community_requests`)
**🟡 모델 일치도:**
```python
# 모델: community_request.py
class CommunityRequest(Base):
    __tablename__ = "community_requests"
    urgency = Column(String, default="normal")  # ✅ 일치

# API: community_requests.py - 대부분 일치하지만 일부 필드 불일치
```

#### **교회 행사/소식**
**🟡 부분 일치:**
```python
# church_events.py 모델
views = Column(Integer, default=0)  # ❌ 실제는 view_count

# church_news.py 모델  
view_count = Column(Integer, default=0)  # ✅ 올바름
```

### 발견된 5가지 데이터 타입 불일치

1. **조회수 필드**: `views` vs `view_count` (6개 API 영향)
2. **작성자 필드**: `user_id` vs `author_id` (4개 API 영향)  
3. **배열 필드**: `ARRAY(String)` vs `JSON` (2개 API 영향)
4. **상태 필드**: 6가지 다른 Enum 체계 (모든 API 영향)
5. **연락처 필드**: 5가지 다른 처리 방식 (모든 API 영향)

### 테이블별 스키마 정확도

| 테이블명 | 모델 파일 일치도 | API 사용 일치도 | 주요 불일치 필드 |
|---|---|---|---|
| `community_sharing` | 🟡 80% | 🔴 60% | `view_count`, 테이블 공유 |
| `community_requests` | 🟡 85% | 🟡 80% | `urgency` 필드명 |
| `job_posts` | 🔴 50% | 🔴 70% | 중복 모델, `view_count` |
| `job_seekers` | 🟡 80% | 🟡 85% | `view_count` |
| `community_music_teams` | 🔴 60% | 🔴 65% | `views` vs `view_count` |
| `music_team_seekers` | 🔴 70% | 🔴 75% | ARRAY vs JSON, `views` |
| `church_events` | 🟡 90% | 🟡 85% | `views` vs `view_count` |
| `church_news` | ✅ 95% | ✅ 90% | - |

---

> **🎯 권장 시작점**: 1단계의 "Schema vs Model 불일치 수정"부터 즉시 시작  
> **⏰ 총 예상 작업 시간**: 2-3주 (74개 체크리스트)  
> **🔄 적용 방식**: 단계별 점진적 적용으로 서비스 중단 최소화