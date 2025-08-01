# Smart Yoram 교회 관리 시스템 API 사용 설명서

## 📋 목차
1. [개요](#개요)
2. [인증](#인증)
3. [사용자 관리](#사용자-관리)
4. [교인 관리](#교인-관리)
5. [출석 관리](#출석-관리)
6. [SMS 기능](#sms-기능)
7. [QR 코드 관리](#qr-코드-관리)
8. [일정 관리](#일정-관리)
9. [가족 관계 관리](#가족-관계-관리)
10. [모바일 교인증](#모바일-교인증)
11. [엑셀 연동](#엑셀-연동)
12. [통계 및 리포트](#통계-및-리포트)
13. [오류 처리](#오류-처리)
14. [추가 엔드포인트 (별도 문서)](./API-추가엔드포인트.md)

---

## 🌟 개요

Smart Yoram은 교회 교적 관리를 위한 종합 REST API 시스템입니다.

**Base URL**: `https://your-domain.com/api/v1`  
**Content-Type**: `application/json`  
**인증 방식**: Bearer Token (JWT)

### 주요 기능
- 교인 정보 관리 (프로필 사진, 상태 관리)
- 한글 초성 검색 지원
- 출석 체크 및 통계
- SMS 발송 기능
- QR 코드 출석 시스템
- 가족 관계 관리
- 모바일 교인증
- 일정 및 생일 관리
- 엑셀 업로드/다운로드
- 실시간 통계 대시보드
- 공지사항 및 오늘의 말씀

---

## 🔐 인증

### 로그인
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@church.com&password=yourpassword
```

**응답**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### 인증 헤더 사용
모든 API 요청에 다음 헤더를 포함해야 합니다:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 권한 레벨
- **admin**: 모든 기능 접근 가능
- **pastor**: 교인 관리, 통계 조회 가능
- **member**: 제한된 조회 기능만 가능

---

## 👥 사용자 관리

### 현재 사용자 정보 조회
```http
GET /users/me
Authorization: Bearer {token}
```

**응답**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@church.com",
  "full_name": "관리자",
  "church_id": 1,
  "role": "admin",
  "is_active": true
}
```

### 사용자 목록 조회 (관리자만)
```http
GET /users/?skip=0&limit=100
Authorization: Bearer {token}
```

### 새 사용자 생성 (관리자만)
```http
POST /users/
Authorization: Bearer {token}
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@church.com",
  "full_name": "새 사용자",
  "password": "securepassword",
  "role": "member"
}
```

---

## 🙋 교인 관리

### 교인 목록 조회
```http
GET /members/?skip=0&limit=100&search={검색어}&member_status={상태}
Authorization: Bearer {token}
```

**검색 기능**:
- 일반 검색: `search=김철수` (이름, 전화번호 검색)
- 초성 검색: `search=ㄱㅊㅅ` (김철수 검색)
- 상태 필터: `member_status=active` (active/inactive/transferred)

**응답**:
```json
[
  {
    "id": 1,
    "name": "김철수",
    "gender": "남",
    "date_of_birth": "1980-05-15",
    "phone_number": "010-1234-5678",
    "address": "서울시 강남구",
    "position": "집사",
    "district": "1구역",
    "church_id": 1,
    "profile_photo_url": "/static/uploads/members/photo.jpg",
    "member_status": "active",
    "registration_date": "2024-01-01",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### 교인 상세 조회
```http
GET /members/{member_id}
Authorization: Bearer {token}
```

### 새 교인 등록
```http
POST /members/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "김철수",
  "gender": "남",
  "date_of_birth": "1980-05-15",
  "phone_number": "010-1234-5678",
  "address": "서울시 강남구",
  "position": "집사",
  "district": "1구역",
  "church_id": 1
}
```

### 교인 정보 수정
```http
PUT /members/{member_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "김철수",
  "phone_number": "010-9876-5432",
  "member_status": "active"
}
```

### 프로필 사진 업로드
```http
POST /members/{member_id}/upload-photo
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: (이미지 파일 - JPG, PNG, GIF, WEBP 지원, 최대 5MB)
```

**응답**:
```json
{
  "id": 1,
  "name": "김철수",
  "profile_photo_url": "/static/uploads/members/1_20240101_123456_abc123.jpg"
}
```

### 프로필 사진 삭제
```http
DELETE /members/{member_id}/delete-photo
Authorization: Bearer {token}
```

---

## 📊 출석 관리

### 출석 기록 조회
```http
GET /attendances/?skip=0&limit=100&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

### 출석 체크
```http
POST /attendances/
Authorization: Bearer {token}
Content-Type: application/json

{
  "member_id": 1,
  "attendance_date": "2024-01-07",
  "attendance_type": "주일예배",
  "is_present": true,
  "notes": "정상 출석"
}
```

### 출석 정보 수정
```http
PUT /attendances/{attendance_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "is_present": false,
  "notes": "결석"
}
```

---

## 📱 SMS 기능

### 개별 SMS 발송 (관리자만)
```http
POST /sms/send
Authorization: Bearer {token}
Content-Type: application/json

{
  "recipient_phone": "010-1234-5678",
  "recipient_member_id": 1,
  "message": "안녕하세요! 이번 주일예배에 참석해 주세요.",
  "sms_type": "invitation"
}
```

### 단체 SMS 발송 (관리자만)
```http
POST /sms/send-bulk
Authorization: Bearer {token}
Content-Type: application/json

{
  "recipient_member_ids": [1, 2, 3, 4, 5],
  "message": "이번 주일예배는 오전 11시입니다.",
  "sms_type": "notice"
}
```

### SMS 발송 기록 조회
```http
GET /sms/history?skip=0&limit=100
Authorization: Bearer {token}
```

### SMS 템플릿 조회
```http
GET /sms/templates
Authorization: Bearer {token}
```

**응답**:
```json
[
  {
    "id": 1,
    "name": "주일예배 안내",
    "message": "[{church_name}] 안녕하세요 {name}님! 이번 주일예배에 참석하여 은혜받는 시간 되시길 바랍니다."
  }
]
```

---

## 🔳 QR 코드 관리

### 교인용 QR 코드 생성
```http
POST /qr-codes/generate/{member_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "qr_type": "attendance",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**응답**:
```json
{
  "id": 1,
  "church_id": 1,
  "member_id": 1,
  "code": "1:1:abc123def456",
  "qr_type": "attendance",
  "is_active": true,
  "expires_at": "2024-12-31T23:59:59Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### QR 코드 이미지 조회
```http
GET /qr-codes/{code}/image
```
응답: PNG 이미지 파일

### QR 코드 스캔 및 출석 체크
```http
POST /qr-codes/verify/{code}?attendance_type=주일예배
Authorization: Bearer {token}
```

**응답 (성공)**:
```json
{
  "status": "success",
  "message": "Attendance marked successfully",
  "member": {
    "id": 1,
    "name": "김철수",
    "profile_photo_url": "/static/uploads/members/photo.jpg"
  },
  "attendance": {
    "id": 123,
    "attendance_date": "2024-01-07",
    "attendance_type": "주일예배",
    "is_present": true
  }
}
```

### 교인의 활성 QR 코드 조회
```http
GET /qr-codes/member/{member_id}
Authorization: Bearer {token}
```

---

## 📅 일정 관리

### 일정 목록 조회
```http
GET /calendar/?skip=0&limit=100&start_date=2024-01-01&end_date=2024-01-31&event_type=birthday
Authorization: Bearer {token}
```

### 새 일정 생성 (관리자만)
```http
POST /calendar/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "새해 감사예배",
  "description": "새해를 맞이하는 특별 감사예배",
  "event_type": "service",
  "event_date": "2024-01-01",
  "event_time": "11:00",
  "is_recurring": false
}
```

### 일정 수정 (관리자만)
```http
PUT /calendar/{event_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "수정된 제목",
  "description": "수정된 설명"
}
```

### 일정 삭제 (관리자만)
```http
DELETE /calendar/{event_id}
Authorization: Bearer {token}
```

### 다가오는 생일 조회
```http
GET /calendar/birthdays?days_ahead=30
Authorization: Bearer {token}
```

**응답**:
```json
[
  {
    "member_id": 1,
    "member_name": "김철수",
    "birthday": "2024-01-15",
    "age": 44,
    "days_until": 8
  }
]
```

### 생일 일정 자동 생성 (관리자만)
```http
POST /calendar/birthdays/create-events
Authorization: Bearer {token}
```

---

## 👨‍👩‍👧‍👦 가족 관계 관리

### 가족 관계 생성
```http
POST /family/relationships
Authorization: Bearer {token}
Content-Type: application/json

{
  "member_id": 1,
  "related_member_id": 2,
  "relationship_type": "부모"
}
```

**관계 유형**: 부모, 자녀, 배우자, 형제, 자매, 조부모, 손자녀, 삼촌, 이모, 고모, 조카

### 교인의 가족 관계 조회
```http
GET /family/relationships/{member_id}
Authorization: Bearer {token}
```

### 가족 트리 조회
```http
GET /family/tree/{member_id}
Authorization: Bearer {token}
```

**응답**:
```json
{
  "root_member": {
    "id": 1,
    "name": "김철수",
    "relationship_type": "본인",
    "profile_photo_url": "/static/uploads/members/photo.jpg",
    "date_of_birth": "1980-05-15",
    "phone_number": "010-1234-5678"
  },
  "family_members": [
    {
      "id": 2,
      "name": "김미영",
      "relationship_type": "배우자",
      "profile_photo_url": null,
      "date_of_birth": "1985-03-20",
      "phone_number": "010-9876-5432"
    }
  ]
}
```

### 가족 관계 삭제
```http
DELETE /family/relationships/{relationship_id}
Authorization: Bearer {token}
```

---

## 📱 모바일 교인증

### 교인증 데이터 조회
```http
GET /member-card/{member_id}/card
Authorization: Bearer {token}
```

**응답**:
```json
{
  "member": {
    "id": 1,
    "name": "김철수",
    "profile_photo_url": "/static/uploads/members/photo.jpg",
    "phone_number": "010-1234-5678",
    "position": "집사",
    "district": "1구역",
    "age": 44,
    "member_status": "active"
  },
  "church": {
    "name": "성광교회",
    "address": "서울시 강남구",
    "phone": "02-1234-5678"
  },
  "qr_code": {
    "code": "card:1:1:abc123",
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
  },
  "statistics": {
    "recent_attendance_count": 4,
    "member_since": "2024년 01월"
  }
}
```

### 모바일 교인증 HTML 조회
```http
GET /member-card/{member_id}/card/html
Authorization: Bearer {token}
```
응답: 모바일 최적화된 HTML 교인증

### 교인증 QR 코드 재생성
```http
POST /member-card/{member_id}/card/regenerate-qr
Authorization: Bearer {token}
```

---

## 📊 엑셀 연동

### 교인 명단 엑셀 업로드 (관리자만)
```http
POST /excel/members/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: (Excel 파일 - .xlsx 또는 .xls)
```

**업로드 파일 형식**:
| 이름 | 성별 | 생년월일 | 전화번호 | 주소 | 직분 | 구역 |
|------|------|----------|----------|------|------|------|
| 김철수 | 남 | 1980-05-15 | 010-1234-5678 | 서울시 강남구 | 집사 | 1구역 |

**응답**:
```json
{
  "message": "Excel upload completed",
  "created": 10,
  "updated": 5,
  "errors": []
}
```

### 교인 명단 엑셀 다운로드
```http
GET /excel/members/download
Authorization: Bearer {token}
```
응답: Excel 파일 다운로드

### 엑셀 업로드 템플릿 다운로드
```http
GET /excel/members/template
Authorization: Bearer {token}
```
응답: 양식이 포함된 Excel 템플릿 파일

### 출석 기록 엑셀 다운로드
```http
GET /excel/attendance/download?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

---

## 📈 통계 및 리포트

### 출석 통계 요약
```http
GET /statistics/attendance/summary?start_date=2024-01-01&end_date=2024-01-31&attendance_type=주일예배
Authorization: Bearer {token}
```

**응답**:
```json
{
  "summary": {
    "total_members": 100,
    "average_attendance": 85.5,
    "average_attendance_rate": 85.5,
    "period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    }
  },
  "attendance_data": [
    {
      "date": "2024-01-07",
      "present_count": 90,
      "total_members": 100,
      "attendance_rate": 90.0
    }
  ]
}
```

### 교인별 출석 통계
```http
GET /statistics/attendance/by-member?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

### 교인 인구통계
```http
GET /statistics/members/demographics
Authorization: Bearer {token}
```

**응답**:
```json
{
  "gender_distribution": [
    {"gender": "남", "count": 45},
    {"gender": "여", "count": 55}
  ],
  "age_distribution": [
    {"age_group": "20-29", "count": 15},
    {"age_group": "30-39", "count": 25},
    {"age_group": "40-49", "count": 30}
  ],
  "position_distribution": [
    {"position": "집사", "count": 20},
    {"position": "권사", "count": 15}
  ],
  "district_distribution": [
    {"district": "1구역", "count": 25},
    {"district": "2구역", "count": 30}
  ]
}
```

### 교인 증가 추이
```http
GET /statistics/members/growth?months=12
Authorization: Bearer {token}
```

**응답**:
```json
{
  "period": {
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "months": 12
  },
  "growth_data": [
    {
      "month": "2023-01",
      "new_members": 5,
      "transfers_out": 1,
      "net_growth": 4,
      "total_members": 104
    }
  ],
  "summary": {
    "total_new_members": 50,
    "total_transfers_out": 10,
    "net_growth": 40,
    "current_total_members": 100
  }
}
```

---

## ⚠️ 오류 처리

### HTTP 상태 코드
- `200`: 성공
- `201`: 생성 성공
- `400`: 잘못된 요청
- `401`: 인증 필요
- `403`: 권한 없음
- `404`: 리소스 없음
- `422`: 유효성 검사 실패
- `500`: 서버 오류

### 오류 응답 형식
```json
{
  "detail": "오류 메시지"
}
```

### 유효성 검사 오류
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 📚 참고 사항

### 페이지네이션
대부분의 목록 API는 `skip`과 `limit` 매개변수를 지원합니다:
- `skip`: 건너뛸 항목 수 (기본값: 0)
- `limit`: 반환할 최대 항목 수 (기본값: 100)

### 날짜 형식
- 날짜: `YYYY-MM-DD` (예: `2024-01-15`)
- 날짜+시간: `YYYY-MM-DDTHH:MM:SSZ` (예: `2024-01-15T14:30:00Z`)

### 파일 업로드 제한
- 이미지: 최대 5MB, JPG/PNG/GIF/WEBP 지원
- 엑셀: .xlsx, .xls 파일만 지원

### 한글 초성 검색
교인 검색 시 한글 초성으로 검색 가능:
- `ㄱㅊㅅ` → 김철수 검색
- `ㅂㅇㄱ` → 박영기 검색

---

## 🚀 빠른 시작 예제

### 1. 로그인하고 교인 목록 가져오기
```javascript
// 1. 로그인
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=admin@church.com&password=yourpassword'
});
const { access_token } = await loginResponse.json();

// 2. 교인 목록 조회
const membersResponse = await fetch('/api/v1/members/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const members = await membersResponse.json();
```

### 2. QR 코드로 출석 체크
```javascript
// QR 코드 스캔 후
const qrCode = "scanned_qr_code";
const response = await fetch(`/api/v1/qr-codes/verify/${qrCode}`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const result = await response.json();

if (result.status === 'success') {
  console.log(`${result.member.name}님 출석 완료!`);
}
```

### 3. 단체 SMS 발송
```javascript
const response = await fetch('/api/v1/sms/send-bulk', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    recipient_member_ids: [1, 2, 3, 4, 5],
    message: "이번 주일예배는 오전 11시입니다.",
    sms_type: "notice"
  })
});
```

---

이 API 문서는 Smart Yoram 교회 관리 시스템의 모든 기능을 포괄적으로 다룹니다. 추가 질문이나 기술 지원이 필요하시면 개발팀에 문의해 주세요.

**개발 완료일**: 2024년 1월 30일  
**최종 업데이트**: 2024년 8월 1일  
**API 버전**: v1.0  
**문서 버전**: 1.1