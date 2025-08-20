# CI/CD 설정 가이드

## 개요
Smart Yoram Backend는 GitHub Actions를 통한 CI/CD 파이프라인을 사용합니다.
- **CI**: Pull Request 시 자동 테스트 실행
- **CD**: main 브랜치 푸시 시 EC2 인스턴스에 자동 배포

## EC2 인스턴스 정보
- **IP**: 13.211.169.169
- **Region**: ap-southeast-2 (Sydney)
- **Instance Type**: t3.small
- **OS**: Ubuntu 24.04

## GitHub Secrets 설정

GitHub 저장소의 Settings → Secrets and variables → Actions에서 다음 시크릿을 설정해야 합니다:

### 필수 Secrets

1. **EC2_SSH_KEY**
   - EC2 인스턴스 접속용 프라이빗 키 (surfmind.pem)
   - 전체 내용을 복사하여 저장
   ```
   -----BEGIN RSA PRIVATE KEY-----
   [키 내용]
   -----END RSA PRIVATE KEY-----
   ```

## EC2 서버 초기 설정

### 1. 필요한 패키지 설치
```bash
# Python 3.11 설치
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip

# Docker 설치 (옵션)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# PostgreSQL 클라이언트 설치
sudo apt install -y postgresql-client

# 기타 유틸리티
sudo apt install -y git nginx supervisor
```

### 2. 애플리케이션 디렉토리 생성
```bash
mkdir -p /home/ubuntu/smart-yoram-backend
mkdir -p /home/ubuntu/logs
mkdir -p /home/ubuntu/backups
```

### 3. 환경 변수 설정
`/home/ubuntu/smart-yoram-backend/.env` 파일 생성:
```env
DATABASE_URL=postgresql://user:password@localhost/smart_yoram
SECRET_KEY=your-secret-key-here
FIREBASE_SERVICE_ACCOUNT=/path/to/firebase-credentials.json
ENVIRONMENT=production
```

### 4. Systemd 서비스 설정 (옵션 1)
```bash
# 서비스 파일 복사
sudo cp /home/ubuntu/smart-yoram-backend/scripts/smart-yoram-backend.service /etc/systemd/system/

# 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable smart-yoram-backend
sudo systemctl start smart-yoram-backend
```

### 5. Docker Compose 설정 (옵션 2)
`docker-compose.yml` 파일이 있는 경우:
```bash
cd /home/ubuntu/smart-yoram-backend
docker-compose up -d
```

### 6. Nginx 리버스 프록시 설정
`/etc/nginx/sites-available/smart-yoram` 파일 생성:
```nginx
server {
    listen 80;
    server_name 13.211.169.169;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

활성화:
```bash
sudo ln -s /etc/nginx/sites-available/smart-yoram /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 배포 프로세스

### 자동 배포 (GitHub Actions)
1. 코드를 main 브랜치에 푸시
2. GitHub Actions가 자동으로:
   - 테스트 실행
   - EC2에 코드 배포
   - 의존성 설치
   - 데이터베이스 마이그레이션
   - 애플리케이션 재시작
   - 헬스 체크

### 수동 배포
```bash
ssh ubuntu@13.211.169.169
cd /home/ubuntu/smart-yoram-backend
./scripts/deploy.sh
```

## 모니터링

### 로그 확인
```bash
# 애플리케이션 로그
tail -f /home/ubuntu/logs/smart-yoram-backend.log

# Systemd 로그
sudo journalctl -u smart-yoram-backend -f

# Docker 로그
docker-compose logs -f
```

### 헬스 체크
```bash
curl http://13.211.169.169:8000/health
```

## 롤백

배포 실패 시 이전 버전으로 롤백:
```bash
cd /home/ubuntu/backups
# 최신 백업 확인
ls -lt backup_*.tar.gz | head -5

# 롤백
cd /home/ubuntu/smart-yoram-backend
tar -xzf /home/ubuntu/backups/backup_[timestamp].tar.gz
./scripts/deploy.sh
```

## 문제 해결

### 포트 충돌
```bash
# 8000 포트 사용 프로세스 확인
sudo lsof -i :8000
# 프로세스 종료
sudo kill -9 [PID]
```

### 권한 문제
```bash
# 파일 소유권 변경
sudo chown -R ubuntu:ubuntu /home/ubuntu/smart-yoram-backend
# 실행 권한 부여
chmod +x /home/ubuntu/smart-yoram-backend/scripts/*.sh
```

### 데이터베이스 연결 실패
```bash
# PostgreSQL 상태 확인
sudo systemctl status postgresql
# 연결 테스트
psql -h localhost -U [username] -d [database]
```

## 보안 고려사항

1. **SSH 키 관리**
   - GitHub Secrets에만 저장
   - 로컬에 복사본 최소화
   - 정기적으로 키 로테이션

2. **환경 변수**
   - 민감한 정보는 .env 파일에만
   - .env 파일은 git에 포함하지 않음
   - AWS Secrets Manager 사용 고려

3. **네트워크 보안**
   - Security Group에서 필요한 포트만 오픈
   - SSH는 특정 IP에서만 허용
   - HTTPS 설정 (Let's Encrypt)

4. **모니터링**
   - CloudWatch 알람 설정
   - 디스크 사용량 모니터링
   - 애플리케이션 로그 수집