# Redis & Celery 배포 가이드

## Overview
Redis와 Celery를 Docker Compose로 함께 배포하는 가이드입니다.

## 🚀 빠른 시작

### 1. 환경 변수 설정
`.env` 파일에 다음 추가:
```bash
# Redis
REDIS_URL=redis://redis:6379/0

# Firebase (푸시 알림용)
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
```

### 2. Firebase 인증 파일
Firebase Console에서 서비스 계정 키를 다운로드하여 `firebase-credentials.json`으로 저장

### 3. Docker Compose 실행
```bash
# 모든 서비스 시작
docker-compose up -d

# 특정 서비스만 시작
docker-compose up -d backend redis

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

## 📊 서비스 구성

### 포트 정보
- **Backend API**: 8000
- **Redis**: 6379
- **Flower (Celery 모니터링)**: 5555

### 서비스 확인
```bash
# 서비스 상태 확인
docker-compose ps

# Redis 연결 테스트
docker-compose exec redis redis-cli ping

# Celery 워커 상태 확인
docker-compose logs celery_worker

# API 헬스체크
curl http://localhost:8000/
```

## 🔧 운영 명령어

### Redis 관리
```bash
# Redis CLI 접속
docker-compose exec redis redis-cli

# Redis 모니터링
docker-compose exec redis redis-cli monitor

# Redis 메모리 사용량
docker-compose exec redis redis-cli info memory
```

### Celery 관리
```bash
# Celery 워커 재시작
docker-compose restart celery_worker

# Celery 큐 상태 확인
docker-compose exec celery_worker celery -A app.core.celery_app inspect active

# Celery 스케줄 작업 확인
docker-compose exec celery_worker celery -A app.core.celery_app inspect scheduled
```

### Flower 모니터링
브라우저에서 http://localhost:5555 접속

## 🚨 트러블슈팅

### Redis 연결 실패
```bash
# Redis 컨테이너 확인
docker-compose ps redis

# Redis 로그 확인
docker-compose logs redis

# 네트워크 확인
docker network ls
docker network inspect smart-yoram-backend_default
```

### Celery 워커 실행 안됨
```bash
# Celery 로그 확인
docker-compose logs celery_worker

# 수동으로 Celery 실행 테스트
docker-compose run --rm celery_worker celery -A app.core.celery_app worker --loglevel=debug
```

### 메모리 부족
```bash
# Docker 리소스 정리
docker system prune -a

# Redis 메모리 설정 (docker-compose.yml)
redis:
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

## 🔒 보안 설정

### Redis 패스워드 설정
```yaml
# docker-compose.yml
redis:
  command: redis-server --requirepass your-redis-password

# .env
REDIS_URL=redis://:your-redis-password@redis:6379/0
```

### 방화벽 설정
```bash
# EC2 보안그룹에서 필요한 포트만 열기
- 8000: API (외부 접근 필요)
- 6379: Redis (내부만)
- 5555: Flower (개발 환경만)
```

## 📈 성능 최적화

### Redis 설정
```bash
# Redis 영속성 비활성화 (캐시로만 사용 시)
redis:
  command: redis-server --save "" --appendonly no
```

### Celery 워커 설정
```yaml
# 워커 개수 조정
celery_worker:
  command: celery -A app.core.celery_app worker --loglevel=info --concurrency=4
```

## 🏭 프로덕션 배포

### 1. AWS ElastiCache 사용 (권장)
```bash
# .env
REDIS_URL=redis://your-elasticache-endpoint:6379/0
```

### 2. Docker Compose 프로덕션 설정
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    image: your-registry/smart-yoram-backend:latest
    # ... 나머지 설정

  # Redis는 ElastiCache 사용으로 제외
  # redis: 제외

  celery_worker:
    image: your-registry/smart-yoram-backend:latest
    # ... 나머지 설정
```

### 3. 환경별 실행
```bash
# 개발 환경
docker-compose up -d

# 프로덕션 환경 (ElastiCache 사용)
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 모니터링

### 1. Redis 모니터링
```bash
# Redis 상태 확인
redis-cli info stats
redis-cli info clients
redis-cli info memory
```

### 2. Celery 모니터링
- Flower UI: http://localhost:5555
- 작업 성공/실패 통계
- 워커 상태 확인
- 큐 길이 모니터링

### 3. 로그 수집
```bash
# 모든 로그를 파일로 저장
docker-compose logs -f > logs/docker-compose.log

# 특정 서비스 로그만
docker-compose logs -f celery_worker > logs/celery.log
```

## 🔄 백업 및 복구

### Redis 데이터 백업
```bash
# Redis 데이터 덤프
docker-compose exec redis redis-cli BGSAVE

# 백업 파일 복사
docker cp $(docker-compose ps -q redis):/data/dump.rdb ./backups/
```

### 복구
```bash
# 백업 파일 복원
docker cp ./backups/dump.rdb $(docker-compose ps -q redis):/data/
docker-compose restart redis
```