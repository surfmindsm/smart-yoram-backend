# Simple Login History API Documentation

## 🔐 Overview

새로운 **Simple Login History API**가 구현되었습니다. 이 시스템은 이전 버전에서 발생했던 서버 오류 문제를 해결하기 위해 **안전하고 단순한** 접근 방식으로 재설계되었습니다.

### 핵심 설계 원칙

1. **Fail-Safe 설계**: 로그인 기록 실패가 실제 로그인에 영향을 주지 않음
2. **단순한 스키마**: 복잡한 JSON이나 Enum 타입 제거
3. **성능 최적화**: 적절한 인덱스로 빠른 조회
4. **안전한 에러 처리**: 모든 예외 상황 처리

---

## 📊 Database Schema

### `login_history` 테이블

```sql
CREATE TABLE login_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    status VARCHAR(20) NOT NULL,
    device_type VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 필드 설명

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `id` | INTEGER | 기본키 (자동증가) | 1, 2, 3... |
| `user_id` | INTEGER | 사용자 ID | 123 |
| `timestamp` | DATETIME | 로그인 시도 시간 | 2025-09-07 12:30:45 |
| `ip_address` | VARCHAR(45) | IP 주소 | 192.168.1.1 |
| `user_agent` | VARCHAR(500) | 브라우저 정보 | Mozilla/5.0... |
| `status` | VARCHAR(20) | 로그인 상태 | "success", "failed" |
| `device_type` | VARCHAR(50) | 기기 유형 | "desktop", "mobile" |
| `created_at` | DATETIME | 레코드 생성 시간 | 2025-09-07 12:30:45 |

---

## 🚀 API Endpoints

### 1. 최근 로그인 정보 조회

**헤더 표시용 간단한 정보**

```http
GET /api/v1/auth/login-history/recent
Authorization: Bearer {access_token}
```

#### Response

```json
{
  "id": 123,
  "timestamp": "2025-09-07T12:30:45Z",
  "ip_address": "192.168.1.100",
  "device_info": "Desktop - Chrome",
  "location": "서울, 한국"
}
```

**빈 데이터 (로그인 기록 없음)**
```json
{
  "id": null,
  "timestamp": null,
  "ip_address": null,
  "device_info": null,
  "location": "위치 정보 없음"
}
```

### 2. 로그인 기록 목록 조회

**페이지네이션과 필터 지원**

```http
GET /api/v1/auth/login-history?page=1&limit=20&start_date=2025-09-01&end_date=2025-09-07
Authorization: Bearer {access_token}
```

#### Query Parameters

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `page` | integer | 1 | 페이지 번호 (1부터 시작) |
| `limit` | integer | 20 | 페이지당 항목 수 (1-100) |
| `start_date` | string | null | 조회 시작일 (YYYY-MM-DD) |
| `end_date` | string | null | 조회 종료일 (YYYY-MM-DD) |

#### Response

```json
{
  "records": [
    {
      "id": 123,
      "user_id": 1,
      "timestamp": "2025-09-07T12:30:45Z",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "status": "success",
      "device_type": "desktop",
      "created_at": "2025-09-07T12:30:45Z"
    }
  ],
  "pagination": {
    "total": 150,
    "page": 1,
    "limit": 20,
    "total_pages": 8
  }
}
```

### 3. 로그인 통계 (관리자만)

```http
GET /api/v1/auth/login-history/stats
Authorization: Bearer {admin_access_token}
```

#### Response

```json
{
  "total_logins": 1250,
  "failed_logins": 45,
  "today_logins": 23,
  "week_logins": 187,
  "device_breakdown": {
    "desktop": 750,
    "mobile": 400,
    "tablet": 100
  }
}
```

### 4. 오래된 기록 정리 (관리자만)

```http
POST /api/v1/auth/login-history/cleanup?days=365
Authorization: Bearer {admin_access_token}
```

#### Response

```json
{
  "success": true,
  "message": "365일 이전 로그인 기록 정리 완료",
  "deleted_count": 1500,
  "cleanup_date": "2025-09-07T12:30:45Z"
}
```

---

## 🔒 권한 정책

### 일반 사용자
- ✅ 본인의 로그인 기록만 조회 가능
- ✅ 최근 로그인 정보 조회
- ❌ 통계 및 정리 기능 불가

### 관리자 (is_superuser=true)
- ✅ 모든 사용자 로그인 기록 조회
- ✅ 시스템 통계 조회
- ✅ 오래된 기록 정리

---

## 🛡️ 에러 처리

모든 API는 표준 HTTP 상태 코드를 사용합니다:

| 상태 코드 | 설명 | 예시 |
|-----------|------|------|
| 200 | 성공 | 정상적인 응답 |
| 400 | 잘못된 요청 | 날짜 형식 오류 |
| 401 | 인증 필요 | 토큰 없음/만료 |
| 403 | 권한 없음 | 관리자 전용 기능 |
| 500 | 서버 오류 | 시스템 오류 |

### 에러 응답 형식

```json
{
  "detail": "시작 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)"
}
```

---

## 💡 프론트엔드 구현 가이드

### 1. 헤더에 최근 로그인 정보 표시

```typescript
// 최근 로그인 정보 가져오기
const fetchRecentLogin = async () => {
  try {
    const response = await fetch('/api/v1/auth/login-history/recent', {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    const data = await response.json();
    
    if (data.timestamp) {
      setLastLoginInfo({
        time: new Date(data.timestamp).toLocaleString(),
        location: data.location,
        device: data.device_info
      });
    }
  } catch (error) {
    console.log('로그인 정보 조회 실패 (무시됨):', error);
    // 실패해도 UI에는 영향 없음
  }
};
```

### 2. 로그인 기록 페이지

```typescript
// 로그인 기록 목록 가져오기
const fetchLoginHistory = async (page = 1, startDate?, endDate?) => {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: '20'
  });
  
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  
  try {
    const response = await fetch(`/api/v1/auth/login-history?${params}`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    const data = await response.json();
    
    setLoginRecords(data.records);
    setPagination(data.pagination);
  } catch (error) {
    console.error('로그인 기록 조회 실패:', error);
  }
};
```

### 3. 관리자 통계 대시보드

```typescript
// 로그인 통계 가져오기 (관리자만)
const fetchLoginStats = async () => {
  try {
    const response = await fetch('/api/v1/auth/login-history/stats', {
      headers: {
        'Authorization': `Bearer ${adminToken}`
      }
    });
    
    if (response.status === 403) {
      console.log('관리자 권한이 필요합니다');
      return;
    }
    
    const stats = await response.json();
    setLoginStats(stats);
  } catch (error) {
    console.error('통계 조회 실패:', error);
  }
};
```

---

## 🧪 테스트 방법

### 로컬 테스트

```bash
# 1. 서버 시작
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. 테스트 스크립트 실행
python3 test_login_history_simple.py
python3 test_login_api_simple.py
```

### 수동 테스트

1. **로그인**: `/api/v1/auth/login/access-token`에서 토큰 획득
2. **최근 정보**: `/api/v1/auth/login-history/recent` 호출
3. **기록 목록**: `/api/v1/auth/login-history` 호출
4. **통계** (관리자): `/api/v1/auth/login-history/stats` 호출

---

## ⚠️ 주의사항

### 1. **안전한 설계**
- 로그인 기록 실패가 로그인 자체를 방해하지 않음
- 모든 기록 함수는 예외 발생 시 안전하게 처리

### 2. **성능 고려**
- 대량의 기록 조회 시 페이지네이션 사용 필수
- 적절한 날짜 범위 설정 권장

### 3. **개인정보 보호**
- 일반 사용자는 본인 기록만 조회 가능
- IP 주소 등 민감 정보 적절히 마스킹 고려

### 4. **정리 작업**
- 주기적으로 오래된 기록 정리 권장 (기본: 1년)
- 관리자만 정리 작업 수행 가능

---

## 🔄 Migration 및 배포

### 데이터베이스 마이그레이션
```bash
# 마이그레이션 파일이 생성되어 있습니다
# 프로덕션 배포 시 자동으로 적용됩니다
alembic upgrade head
```

### 기존 시스템과의 호환성
- 기존 로그인 플로우에 영향 없음
- 점진적 배포 가능
- 실패 시 자동으로 무시

---

## 📞 지원 및 문의

문제 발생 시:
1. **로그 확인**: 서버 콘솔에서 "LOGIN RECORD" 관련 메시지 확인
2. **데이터베이스 확인**: `login_history` 테이블 상태 점검
3. **테스트**: 제공된 테스트 스크립트로 기능 검증

**핵심**: 이 시스템은 실패해도 기존 로그인에 전혀 영향을 주지 않도록 설계되었습니다. 🛡️