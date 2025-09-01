# 교인정보 관리 API 명세서

## 현재 구현된 API

### POST /members/ - 교인 등록
```json
{
  "name": "string",
  "name_eng": "string", 
  "email": "string",
  "gender": "남|여",
  "birthdate": "YYYY-MM-DD",
  "phone": "string",
  "address": "string",
  "position": "string",
  "district": "string", 
  "department_code": "string",
  "position_code": "string",
  "appointed_on": "YYYY-MM-DD",
  "ordination_church": "string",
  "job_title": "string",
  "workplace": "string", 
  "workplace_phone": "string",
  "marital_status": "미혼|기혼|이혼|사별",
  "spouse_name": "string",
  "married_on": "YYYY-MM-DD"
}
```

## 레퍼런스 기준 필요한 API 확장

### 1. 교인 등록 API 확장 - POST /members/

#### 추가 필요 필드들:

```json
{
  // 기본 정보 확장
  "member_number": "string",          // 교번 (자동생성)
  "member_type": "string",            // 교인구분 (정교인/입교인/세례교인)
  "age": "number",                    // 나이 (자동계산)
  "baptism_date": "YYYY-MM-DD",      // 세례일
  "confirmation_date": "YYYY-MM-DD",  // 입교일
  
  // 교회 정보 확장  
  "church_school": "string",          // 교회학교
  "church_school_year": "number",     // 연도 (예: 2005)
  "sub_district": "string",           // 부구역
  "age_group": "성인|청소년|아동",     // 성년구분
  "region_1": "string",               // 안도구
  "region_2": "string",               // 안도구2  
  "region_3": "string",               // 안도구3
  "registration_background": "string", // 등록배경
  
  // 인도자 정보
  "introducer_1": "string",           // 입도자1
  "introducer_2": "string",           // 입도자2
  "introducer_3": "string",           // 입도자3
  
  // 연락처 세분화
  "mobile_phone": "string",           // 핸드폰
  "home_phone": "string",             // 집전화
  "evangelism_phone": "string",       // 전도폰
  "fellowship_phone": "string",       // 친목폰
  "postal_code": "string",            // 우편번호
  "last_contact_date": "YYYY-MM-DD",  // 통화일
  
  // 사역/직업 정보 확장
  "spiritual_grade": "string",        // 신급
  "job_category": "string",           // 직업 분류
  "job_detail": "string",             // 작업 (구체적 업무)
  "job_position": "string",           // 직관 (직책)
  "ministry_start_date": "YYYY-MM-DD", // 장업일
  "neighboring_church": "string",     // 이웃교화
  "position_decision": "string",      // 직관결정
  "daily_activity": "string",         // 매일
  
  // 가족 정보 확장
  "children": [                       // 자녀 배열
    {
      "name": "string",
      "order": "number"               // 자녀 순서
    }
  ],
  
  // 차량 정보
  "vehicle_1": "string",              // 차량1
  "vehicle_2": "string",              // 차량2  
  "vehicle_detail_1": "string",       // 차량호1
  "vehicle_detail_2": "string",       // 차량호2
  
  // 커스텀 필드들
  "custom_field_1": "string",         // 자유1
  "custom_field_2": "string",         // 자유2
  "custom_field_3": "string",         // 자유3
  "custom_field_4": "string",         // 자유4
  "custom_field_5": "string",         // 자유5
  "custom_field_6": "string",         // 자유6
  "custom_field_7": "string",         // 자유7
  "custom_field_8": "string",         // 자유8
  "custom_field_9": "string",         // 자유9
  
  // 특별 사항
  "special_notes": "string"           // 개인 특별 사항
}
```

### 2. 코드성 데이터 조회 API들

#### GET /codes/member-types - 교인구분 코드
```json
{
  "success": true,
  "data": [
    {"code": "FULL_MEMBER", "label": "정교인"},
    {"code": "CONFIRMED_MEMBER", "label": "입교인"},
    {"code": "BAPTIZED_MEMBER", "label": "세례교인"},
    {"code": "ASSOCIATE_MEMBER", "label": "준회원"}
  ]
}
```

#### GET /codes/districts - 구역 목록
```json
{
  "success": true,
  "data": [
    {"code": "DISTRICT_1", "label": "1구역", "sub_districts": ["1-1구역", "1-2구역"]},
    {"code": "DISTRICT_2", "label": "2구역", "sub_districts": ["2-1구역", "2-2구역"]},
    {"code": "DISTRICT_3", "label": "3구역", "sub_districts": ["3-1구역", "3-2구역"]}
  ]
}
```

#### GET /codes/church-schools - 교회학교 목록
```json
{
  "success": true,
  "data": [
    {"code": "ADULT_SCHOOL", "label": "장년부"},
    {"code": "YOUTH_SCHOOL", "label": "청년부"},
    {"code": "STUDENT_SCHOOL", "label": "학생부"},
    {"code": "CHILDREN_SCHOOL", "label": "아동부"},
    {"code": "KINDERGARTEN", "label": "유치부"}
  ]
}
```

#### GET /codes/job-categories - 직업 분류
```json
{
  "success": true,
  "data": [
    {"code": "OFFICE_WORKER", "label": "사무직"},
    {"code": "TEACHER", "label": "교사"},
    {"code": "MEDICAL", "label": "의료진"},
    {"code": "BUSINESS", "label": "사업가"},
    {"code": "STUDENT", "label": "학생"},
    {"code": "HOUSEWIFE", "label": "주부"},
    {"code": "RETIRED", "label": "은퇴"},
    {"code": "OTHER", "label": "기타"}
  ]
}
```

#### GET /codes/spiritual-grades - 신급 코드
```json
{
  "success": true,
  "data": [
    {"code": "GRADE_A", "label": "갑급"},
    {"code": "GRADE_B", "label": "을급"},
    {"code": "GRADE_C", "label": "병급"},
    {"code": "GRADE_D", "label": "정급"}
  ]
}
```

### 3. 교번 자동생성 API

#### GET /members/next-number - 다음 교번 생성
```json
{
  "success": true,
  "data": {
    "member_number": "0001234",  // 자동생성된 교번
    "format": "NNNNNNN"         // 번호 형식
  }
}
```

### 4. 교인 정보 조회/수정 API

#### GET /members/:id - 교인 상세 조회
```json
{
  "success": true,
  "data": {
    // 위의 모든 필드들 포함한 교인 상세 정보
  }
}
```

#### PUT /members/:id - 교인 정보 수정
위의 POST 요청과 동일한 구조

#### GET /members - 교인 목록 조회
```json
{
  "success": true,
  "data": {
    "members": [...],
    "total": 1000,
    "page": 1,
    "limit": 50
  }
}
```

### 5. 검증 규칙

- `member_number`: 고유값, 자동생성
- `name`: 필수값
- `email`: 필수값, 이메일 형식
- `phone` 또는 `mobile_phone`: 둘 중 하나는 필수
- `member_type`: 코드값 검증 필요
- `district`: 유효한 구역 코드인지 검증
- `children`: 배열 형태, 최대 12명까지

### 6. 에러 응답 형식
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력값이 올바르지 않습니다.",
    "details": [
      {
        "field": "email",
        "message": "올바른 이메일 형식이 아닙니다."
      }
    ]
  }
}
```

이 명세서를 바탕으로 백엔드 개발을 진행하시면 레퍼런스 수준의 교인정보 관리가 가능합니다.