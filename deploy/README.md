# Smart Yoram Backend - EC2 배포 가이드

## 사전 준비사항

1. AWS EC2 인스턴스 (Ubuntu 22.04 LTS 권장)
2. 도메인 (선택사항, HTTPS 설정시 필요)
3. EC2 보안 그룹 설정:
   - SSH (22번 포트)
   - HTTP (80번 포트)
   - HTTPS (443번 포트)

## 배포 단계

### 1. EC2 인스턴스 접속
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2. 초기 설정 스크립트 실행
```bash
# 스크립트 다운로드 및 실행
curl -O https://raw.githubusercontent.com/your-repo/smart-yoram-backend/main/deploy/setup_ec2.sh
chmod +x setup_ec2.sh
./setup_ec2.sh
```

### 3. 소스코드 클론
```bash
cd ~/smart-yoram
git clone https://github.com/your-repo/smart-yoram-backend.git
cd smart-yoram-backend
```

### 4. 환경 변수 설정
```bash
# .env 파일 수정
nano .env

# 필요한 값들 수정:
# - SECRET_KEY: 프로덕션용 시크릿 키로 변경
# - BACKEND_CORS_ORIGINS: 프론트엔드 도메인 추가
```

### 5. Docker로 실행
```bash
# 첫 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f
```

### 6. Nginx 설정 (도메인이 있는 경우)
```bash
# Nginx 설정 파일 복사
sudo cp deploy/nginx.conf /etc/nginx/sites-available/smartyoram

# 도메인 수정
sudo nano /etc/nginx/sites-available/smartyoram
# your-domain.com을 실제 도메인으로 변경

# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/smartyoram /etc/nginx/sites-enabled/

# Nginx 테스트 및 재시작
sudo nginx -t
sudo systemctl reload nginx
```

### 7. SSL 인증서 설정 (Let's Encrypt)
```bash
sudo certbot --nginx -d your-domain.com
```

### 8. Systemd 서비스 설정 (선택사항)
```bash
# 서비스 파일 복사
sudo cp deploy/systemd/smartyoram.service /etc/systemd/system/

# 로그 디렉토리 생성
sudo mkdir -p /var/log/smartyoram
sudo chown ubuntu:ubuntu /var/log/smartyoram

# 서비스 활성화 및 시작
sudo systemctl enable smartyoram
sudo systemctl start smartyoram
sudo systemctl status smartyoram
```

## 운영 명령어

### 배포 업데이트
```bash
cd ~/smart-yoram/smart-yoram-backend
./deploy/deploy.sh
```

### 로그 확인
```bash
# Docker 로그
docker-compose logs -f

# Systemd 로그 (systemd 사용시)
sudo journalctl -u smartyoram -f
```

### 컨테이너 재시작
```bash
docker-compose restart
```

### 백업
```bash
# 데이터베이스는 Supabase에서 관리되므로 별도 백업 불필요
# 로그 백업만 필요시 수행
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

## 모니터링

### 헬스체크
```bash
curl http://localhost:8000/
```

### 리소스 모니터링
```bash
# Docker 상태
docker stats

# 시스템 리소스
htop
```

## 문제 해결

### 502 Bad Gateway
- Docker 컨테이너가 실행중인지 확인: `docker-compose ps`
- 백엔드 로그 확인: `docker-compose logs backend`

### 데이터베이스 연결 오류
- Supabase 대시보드에서 연결 상태 확인
- .env 파일의 DATABASE_URL 확인
- 네트워크 연결 확인

### 메모리 부족
- 스왑 파일 추가:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 보안 권장사항

1. **환경 변수**
   - SECRET_KEY를 강력한 값으로 변경
   - 프로덕션 환경에 맞게 CORS 설정

2. **방화벽**
   - 필요한 포트만 열기
   - SSH 포트 변경 고려

3. **정기 업데이트**
   ```bash
   sudo apt update && sudo apt upgrade -y
   docker pull python:3.11-slim
   ```

4. **백업**
   - Supabase 대시보드에서 정기 백업 설정
   - 로그 파일 정기 백업

## 비용 최적화

1. **EC2 인스턴스**
   - t3.micro 또는 t3.small로 시작
   - 필요시 스케일업

2. **스토리지**
   - 로그 로테이션 설정
   - 불필요한 Docker 이미지 정리: `docker system prune -a`

3. **네트워크**
   - CloudFlare 같은 CDN 사용 고려