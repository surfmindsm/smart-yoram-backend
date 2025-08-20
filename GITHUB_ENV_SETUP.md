# GitHub Environment Variables 설정 가이드

이 프로젝트는 GitHub Environment Variables를 사용하여 전체 .env 파일을 하나의 변수로 관리합니다.

## 설정 방법

### 방법 1: Repository Secrets 사용 (권장)

1. GitHub 저장소로 이동
2. **Settings** → **Secrets and variables** → **Actions** 클릭
3. **New repository secret** 클릭
4. **Name**: `ENV_FILE`
5. **Value**: 전체 .env 파일 내용을 그대로 복사하여 붙여넣기

### 방법 2: Environment Variables 사용 (Base64 인코딩)

먼저 .env 파일을 base64로 인코딩:

```bash
# 로컬에서 실행 (OS 자동 감지)
./scripts/encode_env_file.sh

# 또는 직접 실행
# macOS:
base64 -i .env | tr -d '\n'

# Linux:
base64 -w 0 .env

# 일반적인 방법:
base64 < .env | tr -d '\n'
```

Environment 페이지에서 **Add variable** 버튼을 클릭하고:

- **Name**: `ENV_FILE_BASE64`
- **Value**: 위 명령으로 생성된 base64 문자열 전체를 복사하여 붙여넣기

예시:
```
# Database (Supabase)
DATABASE_URL=postgresql://postgres.adzhdsajdamrflvybhxq:password@host:6543/postgres

# Supabase
SUPABASE_URL=https://adzhdsajdamrflvybhxq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://your-domain.com"]

# OpenAI API (Optional)
OPENAI_API_KEY=sk-proj-...
OPENAI_ORGANIZATION=org-...

# 기타 환경 변수들...
```

### 3. Secrets 설정 (SSH 키)

**Settings** → **Secrets and variables** → **Actions**에서:

- **Name**: `EC2_SSH_KEY`
- **Value**: EC2 인스턴스 접속용 SSH 개인키 전체 내용

### 4. Workflow 파일 수정 (이미 완료됨)

`.github/workflows/deploy.yml`에서 environment 지정:

```yaml
jobs:
  deploy:
    environment: production  # 환경 이름 지정
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to EC2
        env:
          ENV_FILE: ${{ vars.ENV_FILE }}  # Environment Variable 사용
          PRIVATE_KEY: ${{ secrets.EC2_SSH_KEY }}  # Secret 사용
```

## 장점

1. **간단한 관리**: 전체 .env 파일을 하나의 변수로 관리
2. **쉬운 업데이트**: GitHub UI에서 직접 수정 가능
3. **환경별 설정**: development, staging, production 등 환경별로 다른 설정 가능
4. **버전 관리**: GitHub이 변경 이력 자동 관리

## 주의사항

1. **줄바꿈 유지**: .env 파일 내용을 그대로 복사하여 붙여넣기
2. **따옴표 처리**: JSON 값의 따옴표가 제대로 유지되는지 확인
3. **공백 제거 안함**: 값의 앞뒤 공백이 필요한 경우 유지됨
4. **크기 제한**: GitHub Variables는 48KB까지 지원

## 로컬 개발 환경

로컬에서는 직접 .env 파일 생성:

```bash
# .env.example을 복사하여 수정
cp .env.example .env
nano .env
```

## 테스트 방법

배포 후 확인:
```bash
# EC2에 SSH 접속
ssh ubuntu@your-ec2-ip

# .env 파일 확인 (민감한 정보 주의)
cat /home/ubuntu/smart-yoram-backend/.env | head -5

# 애플리케이션 상태 확인
curl http://localhost:8000/health
```

## Environment vs Secrets

- **Environment Variables** (`vars`): 
  - 비민감한 설정 데이터
  - UI에서 값 확인 가능
  - 환경별 설정에 적합

- **Secrets** (`secrets`):
  - 민감한 정보 (SSH 키, API 키 등)
  - 한 번 설정하면 값 확인 불가
  - 암호화되어 저장

우리는 .env 파일 전체를 Environment Variable로, SSH 키만 Secret으로 관리합니다.