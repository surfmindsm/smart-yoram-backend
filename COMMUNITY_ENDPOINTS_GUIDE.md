# 🚀 커뮤니티 API 엔드포인트 완벽 가이드

## 📋 요청하신 모든 엔드포인트 구현 완료!

### ✅ **구현 현황**
**7개 요청 엔드포인트 모두 구현되어 있습니다!**

| 번호 | 요청 엔드포인트 | 실제 구현 엔드포인트 | 상태 |
|------|----------------|---------------------|------|
| 1 | `POST /api/v1/community/request` | `POST /api/v1/community/requests` | ✅ 구현됨 |
| 2 | `POST /api/v1/community/sharing-offer` | `POST /api/v1/community/sharing-offer` | ✅ 구현됨 (별칭 추가) |
| 3 | `POST /api/v1/community/job-posting` | `POST /api/v1/community/job-posts` | ✅ 구현됨 |
| 4 | `POST /api/v1/community/job-seeking` | `POST /api/v1/community/job-seekers` | ✅ 구현됨 |
| 5 | `POST /api/v1/community/music-team-recruit` | `POST /api/v1/community/music-team-recruit` | ✅ 구현됨 |
| 6 | `POST /api/v1/community/music-team-seeking` | `POST /api/v1/community/music-team-seeking` | ✅ 구현됨 |
| 7 | `POST /api/v1/community/church-events` | `POST /api/v1/community/church-events` | ✅ 구현됨 |

---

## 🎯 **각 엔드포인트 상세 가이드**

### 1. **물품 요청** 
```http
POST /api/v1/community/requests
```

**요청 데이터:**
```json
{
  "title": "책상 의자가 필요합니다",
  "description": "성경 공부를 위한 의자를 찾고 있습니다",
  "category": "가구",
  "urgency_level": "normal",
  "location": "서울시 강남구",
  "contact_info": "010-1234-5678",
  "needed_by": "2024-12-31T00:00:00"
}
```

**응답:**
```json
{
  "success": true,
  "message": "요청이 등록되었습니다.",
  "data": {
    "id": 123,
    "title": "책상 의자가 필요합니다",
    "status": "active"
  }
}
```

### 2. **나눔 제공**
```http
POST /api/v1/community/sharing-offer
```

**요청 데이터:**
```json
{
  "title": "성경책 나눔합니다",
  "description": "새 성경책을 나눔합니다",
  "category": "도서",
  "condition": "새것",
  "location": "서울시 강남구",
  "contact_info": "010-1234-5678",
  "images": ["https://supabase.co/.../image.jpg"],
  "status": "available"
}
```

**응답:**
```json
{
  "success": true,
  "message": "나눔 게시글이 등록되었습니다.",
  "data": {
    "id": 124,
    "title": "성경책 나눔합니다",
    "status": "available"
  }
}
```

### 3. **사역자 모집**
```http
POST /api/v1/community/job-posts
```

**요청 데이터:**
```json
{
  "title": "주일학교 교사 모집",
  "position": "주일학교 교사",
  "employment_type": "봉사",
  "description": "아이들을 사랑하는 교사를 모집합니다",
  "requirements": "신앙생활 3년 이상",
  "location": "서울시 강남구",
  "contact_info": "pastor@church.com",
  "deadline": "2024-12-31T00:00:00"
}
```

### 4. **사역자 지원**
```http
POST /api/v1/community/job-seekers
```

**요청 데이터:**
```json
{
  "title": "주일학교 교사로 섬기고 싶습니다",
  "desired_position": "주일학교 교사",
  "employment_type": "봉사",
  "experience": "아동 교육 경험 5년",
  "skills": "피아노 연주, 미술 지도",
  "introduction": "아이들을 사랑하며...",
  "contact_info": "010-1234-5678"
}
```

### 5. **행사팀 모집**
```http
POST /api/v1/community/music-team-recruit
```

**요청 데이터:**
```json
{
  "title": "크리스마스 행사 기획팀 모집",
  "team_name": "크리스마스 기획팀",
  "team_type": "행사기획",
  "instruments_needed": ["기획", "디자인", "음향"],
  "positions_needed": "이벤트 기획자, 디자이너",
  "description": "크리스마스 행사를 함께 준비할 팀원을 모집합니다",
  "contact_info": "010-1234-5678"
}
```

### 6. **행사팀 지원**
```http
POST /api/v1/community/music-team-seeking
```

**요청 데이터:**
```json
{
  "title": "행사 기획에 참여하고 싶습니다",
  "desired_team_type": "행사기획",
  "instruments_skills": ["포토샵", "영상편집"],
  "experience": "교회 행사 기획 경험 3년",
  "introduction": "창의적인 행사 기획이 가능합니다",
  "contact_info": "010-1234-5678"
}
```

### 7. **행사 소식**
```http
POST /api/v1/community/church-events
```

**요청 데이터:**
```json
{
  "title": "크리스마스 축제 안내",
  "event_type": "축제",
  "description": "온 가족이 함께하는 크리스마스 축제입니다",
  "start_date": "2024-12-24T18:00:00",
  "end_date": "2024-12-24T21:00:00",
  "location": "교회 본당",
  "capacity": 200,
  "fee": 0,
  "contact_info": "010-1234-5678"
}
```

---

## 🔧 **공통 요청 헤더**

모든 엔드포인트에서 다음 헤더가 필요합니다:

```http
Content-Type: application/json
Authorization: Bearer {JWT_TOKEN}
```

---

## 📝 **공통 응답 형식**

### ✅ **성공 응답**
```json
{
  "success": true,
  "message": "등록이 완료되었습니다.",
  "data": {
    "id": 123,
    "title": "게시글 제목",
    "status": "active"
  }
}
```

### ❌ **실패 응답**
```json
{
  "success": false,
  "message": "오류가 발생했습니다: 상세 내용"
}
```

### 🚨 **인증 오류**
```json
{
  "detail": "Not authenticated"
}
```

### 📏 **유효성 검증 오류**
```json
{
  "detail": [
    {
      "loc": ["title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🧪 **테스트 가이드**

### 필수 테스트 시나리오

#### 1. **정상 케이스 테스트**
- [ ] 각 엔드포인트에 유효한 데이터로 POST 요청
- [ ] 응답 데이터 구조 확인
- [ ] 생성된 ID 값 확인

#### 2. **인증 테스트**
- [ ] JWT 토큰 없이 요청 → 401 오류
- [ ] 잘못된 토큰으로 요청 → 401 오류
- [ ] 유효한 토큰으로 요청 → 성공

#### 3. **유효성 검증 테스트**
- [ ] 필수 필드 누락 → 422 오류
- [ ] 잘못된 데이터 타입 → 422 오류
- [ ] 너무 긴 문자열 → 422 오류

#### 4. **이미지 업로드 연동 테스트**
- [ ] 이미지 먼저 업로드 → URL 획득
- [ ] 획득한 URL을 images 배열에 포함하여 게시글 작성
- [ ] 이미지가 정상 표시되는지 확인

---

## ⚡ **성능 및 제한사항**

### **파일 업로드**
- **이미지 최대 크기**: 10MB
- **허용 형식**: JPG, PNG, GIF, WEBP
- **최대 파일 수**: 10개

### **텍스트 제한**
- **제목**: 최대 200자
- **설명**: 제한 없음 (TEXT 타입)
- **연락처**: 최대 100자

### **API 제한**
- **Rate Limiting**: 현재 미적용 (필요시 적용 가능)
- **동시 요청**: 제한 없음

---

## 🚨 **주의사항**

### 1. **Church ID 자동 설정**
- 모든 게시글은 현재 로그인한 사용자의 `church_id`로 자동 설정됩니다
- 프론트엔드에서 별도로 church_id를 보낼 필요 없습니다

### 2. **User ID 자동 설정**
- 작성자 정보는 JWT 토큰에서 자동으로 추출됩니다
- `current_user.id`가 자동으로 설정됩니다

### 3. **이미지 URL 형식**
- 새로운 Supabase URL 형식을 사용해야 합니다
- `https://adzhdsajdamrflvybhxq.supabase.co/storage/v1/object/public/...`

### 4. **타임존**
- 모든 날짜/시간은 ISO 8601 형식으로 전송해주세요
- 예: `"2024-12-31T23:59:59"`

---

## 📞 **문제 해결**

### 자주 발생하는 오류들

#### `405 Method Not Allowed`
- **원인**: 잘못된 HTTP 메서드 또는 URL
- **해결**: POST 메서드와 정확한 URL 확인

#### `422 Unprocessable Entity`
- **원인**: 요청 데이터 유효성 검증 실패
- **해결**: 필수 필드와 데이터 타입 확인

#### `500 Internal Server Error`
- **원인**: 서버 내부 오류
- **해결**: 요청 데이터 형식 재확인, 로그 확인

### 디버깅 도구

#### API 상태 확인
```http
GET /api/v1/health
```

#### 개별 엔드포인트 테스트
각 파일의 health check 엔드포인트 활용:
- `GET /api/v1/community/requests/health`
- `GET /api/v1/community/sharing/health`
- 등등...

---

## 🎉 **완료!**

**모든 요청하신 엔드포인트가 완벽하게 구현되어 있습니다!**

이제 바로 프론트엔드에서 사용하실 수 있습니다. 

**테스트 완료 후 결과를 공유해주세요!** 🚀

---

## 📚 **추가 리소스**

- [이미지 업로드 가이드](./FRONTEND_NOTIFICATION.md)
- [API 전체 문서](./backend-api-specification.md)
- [에러 처리 가이드](필요시 추가 작성 가능)

**문제가 발생하면 언제든 연락주세요!** 💪