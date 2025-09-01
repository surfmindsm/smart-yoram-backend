# Enhanced Member Fields Documentation

## 📋 개요
Smart Yoram 교인 관리 시스템에 25개의 새로운 필드가 추가되어 보다 상세하고 체계적인 교인 정보 관리가 가능해졌습니다.

## 🆕 새로 추가된 필드들

### 1. 교회 관련 정보 (Enhanced Church Information)

| 필드명 | 타입 | 설명 | 예시값 |
|--------|------|------|--------|
| `member_type` | String | 교인구분 | "정교인", "학습교인", "세례교인" |
| `confirmation_date` | Date | 입교일 | "2023-12-25" |
| `sub_district` | String | 부구역 | "A구역", "청년부구역" |
| `age_group` | String | 나이그룹 | "성인", "청년", "학생", "어린이" |

### 2. 지역 정보 (Regional Information)

| 필드명 | 타입 | 설명 | 예시값 |
|--------|------|------|--------|
| `region_1` | String | 안도구 1 | "서울시" |
| `region_2` | String | 안도구 2 | "강남구" |
| `region_3` | String | 안도구 3 | "역삼동" |
| `postal_code` | String | 우편번호 | "06234" |

### 3. 인도자 정보 (Inviter Information)

| 필드명 | 타입 | 설명 | 예시값 |
|--------|------|------|--------|
| `inviter3_member_id` | Integer | 세 번째 인도자 ID | 123 |

**참고**: `inviter1_member_id`, `inviter2_member_id`는 기존에 존재했음

### 4. 연락 정보 (Contact Details)

| 필드명 | 타입 | 설명 | 예시값 |
|--------|------|------|--------|
| `last_contact_date` | Date | 마지막 연락일 | "2024-01-15" |

### 5. 신앙 정보 (Spiritual Information)

| 필드명 | 타입 | 설명 | 예시값 |
|--------|------|------|--------|
| `spiritual_grade` | String | 신급 | "A급", "B급", "초신자" |

### 6. 직업 정보 (Enhanced Job Information)

| 필드명 | 타입 | 설명 | 예시값 |
|--------|------|------|--------|
| `job_category` | String | 직업분류 | "사무직", "교육직", "의료진" |
| `job_detail` | String | 구체적 업무 | "소프트웨어 개발", "초등학교 교사" |
| `job_position` | String | 직책/직위 | "팀장", "과장", "원장" |

### 7. 사역 정보 (Ministry Information)

| 필드명 | 타입 | 설명 | 예시값 |
|--------|------|------|--------|
| `ministry_start_date` | Date | 사역 시작일 | "2023-01-01" |
| `neighboring_church` | String | 이웃교회 | "은혜교회", "사랑교회" |
| `position_decision` | String | 직분 결정 | "장로 추천", "권사 임명" |
| `daily_activity` | Text | 일상 활동 | "새벽기도 참석, 구역모임 리더" |

### 8. 자유 필드 (Custom Fields)

| 필드명 | 타입 | 설명 | 사용 예시 |
|--------|------|------|----------|
| `custom_field_1` | String | 자유필드 1 | "취미: 등산" |
| `custom_field_2` | String | 자유필드 2 | "특기: 피아노" |
| `custom_field_3` | String | 자유필드 3 | "관심분야: 선교" |
| ... | ... | ... | ... |
| `custom_field_12` | String | 자유필드 12 | "기타 정보" |

### 9. 특별 정보 (Special Information)

| 필드명 | 타입 | 설명 | 예시값 |
|--------|------|------|--------|
| `special_notes` | Text | 개인 특별사항 | "건강상 주의사항, 가족관계 특이사항 등" |

## 🔗 API 사용법

### GET /api/v1/members/
**응답 예시:**
```json
{
  "id": 1,
  "name": "홍길동",
  "email": "hong@example.com",
  "phone": "010-1234-5678",
  
  // 새로 추가된 필드들
  "member_type": "정교인",
  "confirmation_date": "2023-12-25",
  "sub_district": "A구역",
  "age_group": "성인",
  
  "region_1": "서울시",
  "region_2": "강남구", 
  "region_3": "역삼동",
  "postal_code": "06234",
  
  "inviter3_member_id": 123,
  "last_contact_date": "2024-01-15",
  "spiritual_grade": "A급",
  
  "job_category": "사무직",
  "job_detail": "소프트웨어 개발",
  "job_position": "팀장",
  
  "ministry_start_date": "2023-01-01",
  "neighboring_church": "은혜교회",
  "position_decision": "장로 추천",
  "daily_activity": "새벽기도 참석, 구역모임 리더",
  
  "custom_field_1": "취미: 등산",
  "custom_field_2": "특기: 피아노",
  // ... custom_field_12까지
  
  "special_notes": "건강상 주의사항 있음"
}
```

### POST /api/v1/members/ (교인 추가)
**요청 예시:**
```json
{
  "name": "김철수",
  "email": "kim@example.com", 
  "phone": "010-9876-5432",
  "address": "서울시 강남구 역삼동 123-45",
  
  // 새 필드들 (모두 optional)
  "member_type": "정교인",
  "confirmation_date": "2024-01-01",
  "sub_district": "B구역",
  "age_group": "청년",
  
  "region_1": "서울시",
  "region_2": "강남구",
  "region_3": "역삼동", 
  "postal_code": "06234",
  
  "spiritual_grade": "초신자",
  "job_category": "교육직",
  "job_detail": "고등학교 교사",
  "job_position": "부장교사",
  
  "custom_field_1": "바이올린 연주 가능",
  "custom_field_2": "청년부 찬양팀",
  
  "special_notes": "매주 수요일 저녁 시간 참석 어려움"
}
```

## 📝 프론트엔드 구현 가이드

### 1. 교인 등록 폼 확장
```javascript
const memberFormFields = {
  // 기존 필드들
  name: '',
  email: '',
  phone: '',
  address: '',
  
  // 새 필드들
  member_type: '',
  confirmation_date: '',
  sub_district: '',
  age_group: '',
  
  region_1: '',
  region_2: '', 
  region_3: '',
  postal_code: '',
  
  spiritual_grade: '',
  job_category: '',
  job_detail: '',
  job_position: '',
  
  ministry_start_date: '',
  neighboring_church: '',
  position_decision: '',
  daily_activity: '',
  
  custom_field_1: '',
  custom_field_2: '',
  // ... custom_field_12까지
  
  special_notes: ''
};
```

### 2. 드롭다운 옵션 예시
```javascript
const memberTypeOptions = [
  { value: '정교인', label: '정교인' },
  { value: '학습교인', label: '학습교인' },
  { value: '세례교인', label: '세례교인' },
  { value: '방문자', label: '방문자' }
];

const ageGroupOptions = [
  { value: '어린이', label: '어린이 (0-12세)' },
  { value: '학생', label: '학생 (13-19세)' },
  { value: '청년', label: '청년 (20-35세)' },
  { value: '성인', label: '성인 (36-65세)' },
  { value: '시니어', label: '시니어 (65세+)' }
];

const spiritualGradeOptions = [
  { value: '초신자', label: '초신자' },
  { value: 'B급', label: 'B급' },
  { value: 'A급', label: 'A급' },
  { value: '리더', label: '리더' }
];

const jobCategoryOptions = [
  { value: '사무직', label: '사무직' },
  { value: '교육직', label: '교육직' },
  { value: '의료진', label: '의료진' },
  { value: '서비스업', label: '서비스업' },
  { value: '자영업', label: '자영업' },
  { value: '학생', label: '학생' },
  { value: '주부', label: '주부' },
  { value: '기타', label: '기타' }
];
```

### 3. 폼 섹션 구성 제안
```javascript
const formSections = [
  {
    title: "기본 정보",
    fields: ["name", "email", "phone", "address"]
  },
  {
    title: "교회 정보", 
    fields: ["member_type", "confirmation_date", "sub_district", "age_group"]
  },
  {
    title: "지역 정보",
    fields: ["region_1", "region_2", "region_3", "postal_code"]
  },
  {
    title: "신앙 정보",
    fields: ["spiritual_grade", "ministry_start_date", "daily_activity"]
  },
  {
    title: "직업 정보", 
    fields: ["job_category", "job_detail", "job_position"]
  },
  {
    title: "추가 정보",
    fields: ["neighboring_church", "position_decision"]
  },
  {
    title: "자유 필드",
    fields: ["custom_field_1", "custom_field_2", "custom_field_3", "custom_field_4"]
  },
  {
    title: "특별 사항",
    fields: ["special_notes"]
  }
];
```

## ⚠️ 주의사항

### 1. 모든 새 필드는 Optional
- 기존 시스템과의 호환성을 위해 모든 새 필드는 `null` 허용
- 필수값 검증 없이 부분적으로 입력 가능

### 2. 데이터 타입 주의
- Date 필드: `YYYY-MM-DD` 형식 사용
- Text vs String: `daily_activity`, `special_notes`는 긴 텍스트 입력 가능

### 3. 외래키 관계
- `inviter3_member_id`는 같은 교회의 다른 교인 ID 참조
- 존재하지 않는 ID 입력 시 에러 발생

### 4. 성능 고려사항
- 검색 성능을 위해 자주 사용되는 필드에는 인덱스 추가됨
- `member_type`, `age_group`, `spiritual_grade`, `job_category` 등

## 🚀 다음 단계
1. 프론트엔드에서 새 필드들을 단계적으로 추가
2. 사용자 테스트를 통한 UI/UX 개선
3. 드롭다운 옵션들을 관리자가 설정할 수 있도록 확장
4. 필드별 권한 설정 기능 추가

---

**📞 문의사항**: 구현 중 문제가 있거나 추가 설명이 필요한 경우 백엔드 팀에 문의해 주세요.