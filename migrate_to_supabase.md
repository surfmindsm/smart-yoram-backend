# Supabase 마이그레이션 가이드

## 왜 FastAPI + Supabase DB를 추천하는가?

### 1. 현재 코드 재사용
- 이미 완성된 FastAPI 백엔드를 그대로 사용
- 데이터베이스 연결만 변경하면 됨
- 모든 비즈니스 로직 유지

### 2. Supabase의 장점 활용
- 관리형 PostgreSQL 데이터베이스
- 자동 백업 및 복원
- Row Level Security (RLS)
- 실시간 구독 기능 (필요시)

### 3. Edge Functions의 한계
- Python 지원 안됨 (TypeScript/JavaScript만 가능)
- 복잡한 비즈니스 로직 구현 어려움
- 로컬 개발 환경 구축 복잡
- 디버깅 어려움

## 마이그레이션 단계

### 1. Supabase 프로젝트 설정
1. Supabase 대시보드에서 Database Password 확인
2. Settings > Database > Connection string 복사

### 2. 환경 변수 설정
```bash
cp .env.supabase.example .env
# .env 파일 수정하여 실제 비밀번호 입력
```

### 3. PostgreSQL 드라이버 설치
```bash
pip install psycopg2-binary
```

### 4. 데이터베이스 마이그레이션
```bash
# Alembic으로 테이블 생성
alembic upgrade head

# 초기 데이터 생성
python init_db.py
```

### 5. FastAPI 서버 실행
```bash
uvicorn app.main:app --reload
```

## 추가 기능 활용

### Supabase Storage (파일 업로드)
```python
# 주보 PDF 파일 업로드 시 활용
from supabase import create_client

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
supabase.storage.from_('bulletins').upload(file_path, file_data)
```

### Row Level Security (RLS)
```sql
-- 교회별 데이터 격리
CREATE POLICY "Users can only see their church members" ON members
FOR SELECT USING (church_id = auth.jwt() ->> 'church_id');
```

### 실시간 구독
```javascript
// 프론트엔드에서 실시간 출석 현황 구독
const subscription = supabase
  .from('attendances')
  .on('INSERT', handleNewAttendance)
  .subscribe()
```

## 결론

**FastAPI + Supabase Database** 조합이 가장 효율적입니다:
- ✅ 기존 코드 100% 재사용
- ✅ 강력한 백엔드 기능 유지
- ✅ Supabase의 관리형 DB 장점 활용
- ✅ 필요시 Storage, Realtime 등 추가 기능 사용 가능

Edge Functions는 간단한 webhook이나 트리거 용도로만 사용하는 것을 추천합니다.