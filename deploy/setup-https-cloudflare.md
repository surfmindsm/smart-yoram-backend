# HTTPS 설정 가이드 (CloudFlare 사용)

## 옵션 1: CloudFlare 무료 SSL (권장)

### 1. CloudFlare 계정 설정
1. [CloudFlare](https://www.cloudflare.com) 가입
2. 도메인 추가 (예: smartyoram.com)
3. DNS 레코드 추가:
   - Type: A
   - Name: api (또는 @)
   - Content: 3.25.230.187
   - Proxy status: Proxied (주황색 구름)

### 2. SSL/TLS 설정
1. CloudFlare 대시보드 → SSL/TLS → Overview
2. "Flexible" 모드 선택 (CloudFlare ↔ 사용자는 HTTPS, CloudFlare ↔ EC2는 HTTP)

### 3. 프론트엔드 API URL 업데이트
```javascript
// .env.production
REACT_APP_API_URL=https://api.smartyoram.com/api/v1
```

## 옵션 2: EC2에 직접 SSL 설정 (Let's Encrypt)

### 1. 도메인 연결
EC2 IP에 도메인을 연결 (Route 53 또는 다른 DNS 서비스 사용)

### 2. EC2에서 SSL 설정
```bash
# EC2에서 실행
cd ~/smart-yoram/smart-yoram-backend

# Certbot 설치
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d api.smartyoram.com

# 자동 갱신 설정
sudo systemctl enable certbot.timer
```

### 3. Nginx HTTPS 설정
```nginx
server {
    listen 80;
    server_name api.smartyoram.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.smartyoram.com;

    ssl_certificate /etc/letsencrypt/live/api.smartyoram.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.smartyoram.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 옵션 3: 임시 해결 방법 (개발용)

### Vercel Functions 프록시
```javascript
// api/proxy/[...path].js
export default async function handler(req, res) {
  const { path } = req.query;
  const url = `http://3.25.230.187/api/v1/${path.join('/')}`;
  
  try {
    const response = await fetch(url, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...req.headers,
      },
      body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined,
    });
    
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    res.status(500).json({ error: 'Proxy error' });
  }
}
```

그리고 프론트엔드에서:
```javascript
// API URL을 Vercel Functions로 변경
REACT_APP_API_URL=/api/proxy
```

## 권장 사항

1. **CloudFlare 사용** (가장 빠른 해결책)
   - 무료 SSL
   - DDoS 보호
   - CDN 기능
   - 5분 내 설정 완료

2. **도메인이 없다면**
   - Freenom에서 무료 도메인 취득
   - 또는 CloudFlare Workers를 사용한 프록시

## EC2 보안 그룹 설정

HTTPS 사용 시 443 포트 추가:
1. EC2 콘솔 → Security Groups
2. Inbound rules → Edit
3. Add rule:
   - Type: HTTPS
   - Port: 443
   - Source: 0.0.0.0/0