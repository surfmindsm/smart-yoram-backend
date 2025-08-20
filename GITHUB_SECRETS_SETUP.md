# GitHub Secrets 설정 가이드

이 프로젝트는 GitHub Actions를 통한 자동 배포 시 GitHub Secrets를 사용하여 환경 변수를 안전하게 관리합니다.

## 필수 GitHub Secrets 설정

GitHub 저장소의 Settings → Secrets and variables → Actions에서 다음 Secrets를 추가해야 합니다:

### 1. EC2 배포 관련
- `EC2_SSH_KEY`: EC2 인스턴스 접속용 SSH 개인키 (전체 내용 복사)

### 2. 데이터베이스
- `DATABASE_URL`: PostgreSQL 연결 문자열
  ```
  postgresql://username:password@host:port/database
  ```

### 3. Supabase
- `SUPABASE_URL`: Supabase 프로젝트 URL
  ```
  https://[PROJECT_REF].supabase.co
  ```
- `SUPABASE_ANON_KEY`: Supabase Anon Key

### 4. 보안
- `SECRET_KEY`: JWT 토큰 서명용 비밀키 (랜덤 문자열)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 액세스 토큰 만료 시간 (분 단위, 예: 10080)

### 5. CORS
- `BACKEND_CORS_ORIGINS`: 허용할 프론트엔드 도메인 목록 (JSON 배열 형식)
  ```json
  ["http://localhost:3000", "https://your-frontend-domain.com"]
  ```

### 6. 선택 사항
- `OPENAI_API_KEY`: OpenAI API 키 (AI 기능 사용 시)
- `OPENAI_ORGANIZATION`: OpenAI Organization ID
- `API_KEYS`: 추가 API 키
- `FIRST_SUPERUSER`: 초기 관리자 이메일 (기본값: admin@smartyoram.com)
- `FIRST_SUPERUSER_PASSWORD`: 초기 관리자 비밀번호 (기본값: changeme)

## GitHub Secrets 추가 방법

1. GitHub 저장소로 이동
2. Settings 탭 클릭
3. 왼쪽 메뉴에서 "Secrets and variables" → "Actions" 선택
4. "New repository secret" 버튼 클릭
5. Name과 Value 입력 후 "Add secret" 클릭

## 예시: DATABASE_URL 추가

```
Name: DATABASE_URL
Value: postgresql://postgres.adzhdsajdamrflvybhxq:password@aws-0-us-east-2.pooler.supabase.com:6543/postgres
```

## 예시: BACKEND_CORS_ORIGINS 추가

```
Name: BACKEND_CORS_ORIGINS
Value: ["http://localhost:3000", "http://localhost:8080", "https://smart-yoram-admin.vercel.app"]
```

## 주의사항

1. **보안**: Secret 값은 한 번 입력하면 다시 볼 수 없습니다. 안전한 곳에 백업하세요.
2. **JSON 형식**: `BACKEND_CORS_ORIGINS`는 유효한 JSON 배열 형식이어야 합니다.
3. **따옴표**: JSON 값에는 큰따옴표(")를 사용하세요.
4. **공백**: Secret 값의 앞뒤 공백은 자동으로 제거되지 않으므로 주의하세요.

## 로컬 개발 환경

로컬 개발 시에는 `.env` 파일을 직접 생성하여 사용합니다:

```bash
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력
nano .env
```

**중요**: `.env` 파일은 절대 Git에 커밋하지 마세요!