# Smart Yoram Backend - EC2 배포 가이드

## 1. EC2 인스턴스 설정

### EC2 인스턴스 생성
1. AWS Console에서 EC2 인스턴스 생성
   - OS: Ubuntu 22.04 LTS
   - Instance Type: t3.micro (또는 t3.small)
   - Security Group 설정:
     - SSH (22번 포트) - 내 IP
     - HTTP (80번 포트) - 0.0.0.0/0
     - HTTPS (443번 포트) - 0.0.0.0/0
     - Custom TCP (8000번 포트) - 0.0.0.0/0 (개발용, 나중에 제거)

### EC2 접속
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

## 2. EC2 초기 설정

### 설정 스크립트 실행
```bash
# 설정 스크립트 다운로드
wget https://raw.githubusercontent.com/surfmindsm/smart-yoram-backend/main/deploy/setup_ec2.sh
chmod +x setup_ec2.sh
./setup_ec2.sh
```

### Git SSH 설정 (Private Repository 접근)

#### 옵션 1: 로컬 SSH 키 재사용
```bash
# 1. 로컬에서 EC2로 SSH 키 복사 (로컬 터미널에서 실행)
EC2_IP="your-ec2-ip"
KEY_PATH="your-key.pem"
scp -i $KEY_PATH ~/.ssh/surfmind_github* ubuntu@$EC2_IP:~/

# 2. EC2에서 SSH 키 설정 (EC2 터미널에서 실행)
mkdir -p ~/.ssh
mv ~/surfmind_github* ~/.ssh/
chmod 600 ~/.ssh/surfmind_github
chmod 644 ~/.ssh/surfmind_github.pub

# 3. SSH config 설정
cat >> ~/.ssh/config << 'EOF'
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/surfmind_github
    IdentitiesOnly yes
    StrictHostKeyChecking no
EOF
chmod 600 ~/.ssh/config

# 4. Git 설정
git config --global user.name "Surfmind"
git config --global user.email "surfmind.sm@gmail.com"

# 5. SSH 연결 테스트
ssh -T git@github.com

# 6. 프로젝트 클론 (SSH 사용)
cd ~/smart-yoram
git clone git@github.com:surfmindsm/smart-yoram-backend.git
cd smart-yoram-backend
```

#### 옵션 2: Deploy Key 사용 (권장)
```bash
# 1. EC2에서 새 SSH 키 생성
ssh-keygen -t ed25519 -C "ec2-deploy@smartyoram.com" -f ~/.ssh/deploy_key -N ""

# 2. 공개 키 확인
cat ~/.ssh/deploy_key.pub

# 3. GitHub Repository Settings > Deploy keys에 추가
# - https://github.com/surfmindsm/smart-yoram-backend/settings/keys
# - "Add deploy key" 클릭
# - 위의 공개 키 붙여넣기

# 4. SSH config 설정
cat >> ~/.ssh/config << 'EOF'
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/deploy_key
    IdentitiesOnly yes
EOF

# 5. 프로젝트 클론
cd ~/smart-yoram
git clone git@github.com:surfmindsm/smart-yoram-backend.git
cd smart-yoram-backend
```

## 3. 환경 변수 설정

### .env 파일 생성
```bash
cp .env.example .env
nano .env
```

### 필수 환경 변수 수정
```env
# Database (Supabase)
DATABASE_URL=postgresql://postgres.adzhdsajdamrflvybhxq:7Vhg9aJh5rv76zI7@aws-0-us-east-2.pooler.supabase.com:6543/postgres

# Supabase
SUPABASE_URL=https://adzhdsajdamrflvybhxq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkemhkc2FqZGFtcmZsdnliaHhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NDg5ODEsImV4cCI6MjA2OTQyNDk4MX0.pgn6M5_ihDFt3ojQmCoc3Qf8pc7LzRvQEIDT7g1nW3c

# Security - 프로덕션용 시크릿 키로 변경!
SECRET_KEY=your-production-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS - 프론트엔드 도메인 추가
BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://your-frontend-domain.com"]
```

## 4. Docker로 배포

### Docker 이미지 빌드 및 실행
```bash
# 처음 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 헬스체크
curl http://localhost:8000/
```

## 5. Nginx 설정 (도메인이 있는 경우)

### Nginx 설정 복사
```bash
# Nginx 설정 파일 복사
sudo cp deploy/nginx.conf /etc/nginx/sites-available/smartyoram

# 도메인 수정
sudo nano /etc/nginx/sites-available/smartyoram
# your-domain.com을 실제 도메인으로 변경

# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/smartyoram /etc/nginx/sites-enabled/

# 기본 설정 제거
sudo rm /etc/nginx/sites-enabled/default

# Nginx 테스트 및 재시작
sudo nginx -t
sudo systemctl reload nginx
```

### SSL 인증서 설정 (Let's Encrypt)
```bash
# 도메인이 있는 경우만
sudo certbot --nginx -d your-domain.com
```

## 6. 서비스 모니터링

### 컨테이너 상태 확인
```bash
docker-compose ps
docker stats
```

### 로그 확인
```bash
# Docker 로그
docker-compose logs -f backend

# Nginx 로그
sudo tail -f /var/log/nginx/smartyoram_access.log
sudo tail -f /var/log/nginx/smartyoram_error.log
```

## 7. 업데이트 배포

### 코드 업데이트 및 재배포
```bash
cd ~/smart-yoram/smart-yoram-backend
git pull origin main
./deploy/deploy.sh
```

## 8. 문제 해결

### 502 Bad Gateway
```bash
# Docker 컨테이너 확인
docker-compose ps
docker-compose restart

# 포트 확인
sudo netstat -tlnp | grep 8000
```

### 메모리 부족
```bash
# 스왑 파일 추가
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Docker 정리
```bash
# 불필요한 이미지 및 컨테이너 정리
docker system prune -a
```

## 9. 보안 설정

### UFW 방화벽 최종 설정
```bash
# 개발 포트 제거 (프로덕션)
sudo ufw delete allow 8000/tcp
sudo ufw status
```

### SSH 보안 강화
```bash
# SSH 설정 변경
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
# PermitRootLogin no

sudo systemctl restart sshd
```

## 10. 백업 설정

### 로그 백업
```bash
# 로그 백업 스크립트
cat > ~/backup-logs.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups
mkdir -p $BACKUP_DIR
cd ~/smart-yoram/smart-yoram-backend
tar -czf $BACKUP_DIR/logs-$(date +%Y%m%d-%H%M%S).tar.gz logs/
find $BACKUP_DIR -name "logs-*.tar.gz" -mtime +7 -delete
EOF

chmod +x ~/backup-logs.sh

# Cron 설정 (매일 새벽 3시)
crontab -e
# 0 3 * * * /home/ubuntu/backup-logs.sh
```

## 접속 정보

### 로컬 테스트
- API: http://your-ec2-public-ip:8000
- Docs: http://your-ec2-public-ip:8000/docs

### 프로덕션 (Nginx 설정 후)
- API: https://your-domain.com
- Docs: https://your-domain.com/docs

## 주의사항

1. **SECRET_KEY** 반드시 변경
2. **CORS** 설정에 실제 프론트엔드 도메인 추가
3. 프로덕션 환경에서는 8000번 포트 방화벽 차단
4. 정기적인 시스템 업데이트 수행
5. CloudWatch 또는 기타 모니터링 도구 설정 권장