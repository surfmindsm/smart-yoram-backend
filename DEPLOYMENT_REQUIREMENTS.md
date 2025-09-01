# 배포 요구사항 - 시스템 공지사항 기능

## 🚀 배포 후 필수 작업

### 1. 데이터베이스 마이그레이션 실행

프로덕션 서버에서 다음 명령어 실행:

```bash
# 마이그레이션 실행 (새로운 테이블 생성)
alembic upgrade head

# 또는 직접 SQL 실행
psql -d your_database -f create_system_announcements_tables.sql
```

### 2. 시스템 관리자 계정 생성

프로덕션 DB에서 다음 SQL 실행:

```sql
-- 시스템 관리자 계정 생성 (church_id = 0)
INSERT INTO users (username, email, full_name, hashed_password, church_id, role, is_active, is_superuser)
VALUES (
    'system_superadmin', 
    'system@smartyoram.com', 
    '시스템 최고관리자', 
    '$2b$12$LQv3c4yqu...' -- bcrypt hash of 'admin123!'
    0, 
    'system_admin', 
    true, 
    true
)
ON CONFLICT (username) DO NOTHING;

-- church_id = 0인 시스템 교회 생성 (필요한 경우)
INSERT INTO churches (id, name, is_active)
VALUES (0, '시스템', true)
ON CONFLICT (id) DO NOTHING;
```

### 3. 비밀번호 해시 생성

Python으로 비밀번호 해시 생성:

```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash("admin123!")
print(hashed_password)
```

### 4. 환경 변수 확인

다음 환경 변수들이 설정되어 있는지 확인:

```env
DATABASE_URL=postgresql://...
SECRET_KEY=your_secret_key
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
```

## 🔍 배포 후 확인사항

### 1. API 엔드포인트 테스트

**시스템 관리자로 로그인:**
```bash
curl -X POST "https://your-domain.com/api/v1/auth/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=system_superadmin&password=admin123!"
```

**시스템 공지사항 생성 테스트:**
```bash
curl -X POST "https://your-domain.com/api/v1/system-announcements/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "테스트 시스템 공지",
    "content": "시스템 공지사항 테스트입니다.",
    "priority": "normal",
    "start_date": "2025-09-01",
    "end_date": "2025-09-10",
    "is_active": true
  }'
```

### 2. 데이터베이스 테이블 확인

```sql
-- 테이블 존재 확인
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('system_announcements', 'system_announcement_reads');

-- 시스템 관리자 계정 확인
SELECT username, church_id, role FROM users WHERE church_id = 0;
```

## 🐛 트러블슈팅

### 500 Internal Server Error가 발생하는 경우

1. **테이블이 존재하지 않음**: 마이그레이션 실행
2. **시스템 관리자 계정 없음**: SQL로 직접 생성
3. **권한 문제**: church_id = 0인 사용자만 시스템 공지사항 관리 가능

### 로그인이 실패하는 경우

1. **사용자명/비밀번호 확인**: `system_superadmin` / `admin123!`
2. **계정 존재 확인**: DB에서 사용자 조회
3. **비밀번호 해시 확인**: bcrypt으로 올바르게 해시된 비밀번호인지 확인

### CORS 에러가 발생하는 경우

`app/main.py`에서 CORS 설정 확인:
```python
allow_origins=[
    "http://localhost:3000",
    "https://your-frontend-domain.com",
    "*"  # 개발 중 임시
]
```

## 📋 생성된 테이블 구조

### `system_announcements`
- 시스템 차원의 공지사항 저장
- 우선순위, 게시기간, 대상 교회 설정 가능
- 시스템 관리자(church_id=0)만 관리

### `system_announcement_reads`  
- 시스템 공지사항 읽음 처리 기록
- user_id + church_id + system_announcement_id의 조합으로 추적

## 🔗 관련 파일

- `app/models/announcement.py` - 모델 정의
- `app/api/api_v1/endpoints/system_announcements.py` - API 엔드포인트
- `app/schemas/system_announcement.py` - 요청/응답 스키마
- `alembic/versions/create_system_announcements_table.py` - 마이그레이션 파일

---

**배포 담당자는 위 단계를 순서대로 실행한 후 API 테스트를 진행해주세요.**