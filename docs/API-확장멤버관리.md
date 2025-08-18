# 확장 멤버 관리 API 문서

## 개요
Smart Yoram 확장 멤버 관리 API는 교인의 상세 정보, 연락처, 사역 이력, 성례 기록 등을 종합적으로 관리하는 기능을 제공합니다.

## 인증
모든 API는 JWT 토큰을 통한 인증이 필요합니다.
```
Authorization: Bearer <your-jwt-token>
```

---

## 1. 종합 멤버 정보 조회

### 1.1 멤버 확장 정보 조회
**GET** `/api/v1/members/{member_id}/enhanced`

모든 관련 데이터(연락처, 주소, 사역, 성례 등)를 포함한 멤버 정보를 조회합니다.

**Response:**
```json
{
    "id": 1,
    "church_id": 1,
    "code": "M2024001",
    "name": "홍길동",
    "name_eng": "Hong Gil Dong",
    "contacts": [
        {
            "id": 1,
            "member_id": 1,
            "type": "mobile",
            "value": "010-1234-5678",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "member_id": 1,
            "type": "email",
            "value": "hong@example.com",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "addresses": [
        {
            "id": 1,
            "member_id": 1,
            "address_id": 1,
            "is_primary": true,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "vehicles": [
        {
            "id": 1,
            "member_id": 1,
            "car_type": "소나타",
            "plate_no": "12가3456",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "ministries": [
        {
            "id": 1,
            "member_id": 1,
            "department_code": "WORSHIP",
            "position_code": "ELDER",
            "appointed_on": "2024-01-01",
            "ordination_church": "중앙교회",
            "job_title": "회사원",
            "workplace": "삼성전자",
            "workplace_phone": "02-1234-5678",
            "resign_on": null,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "sacraments": [
        {
            "id": 1,
            "member_id": 1,
            "type": "세례",
            "date": "2020-04-12",
            "church_name": "중앙교회",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "marriages": [
        {
            "id": 1,
            "member_id": 1,
            "status": "기혼",
            "spouse_member_id": 2,
            "married_on": "2018-05-20",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "transfers": [],
    "status_history": [
        {
            "id": 1,
            "member_id": 1,
            "status": "active",
            "started_at": "2024-01-01",
            "ended_at": null,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

---

## 2. 연락처(Contact) 관리

### 2.1 멤버 연락처 목록 조회
**GET** `/api/v1/members/{member_id}/contacts`

**Response:**
```json
[
    {
        "id": 1,
        "member_id": 1,
        "type": "mobile",
        "value": "010-1234-5678",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": 2,
        "member_id": 1,
        "type": "email",
        "value": "hong@example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

### 2.2 멤버 연락처 추가
**POST** `/api/v1/members/{member_id}/contacts`

**Request Body:**
```json
{
    "type": "home_phone",
    "value": "02-1234-5678"
}
```

**연락처 타입:**
- `mobile`: 휴대폰
- `home_phone`: 집 전화
- `work_phone`: 직장 전화
- `email`: 이메일
- `fax`: 팩스

---

## 3. 사역(Ministry) 관리

### 3.1 멤버 사역 이력 조회
**GET** `/api/v1/members/{member_id}/ministries`

**Response:**
```json
[
    {
        "id": 1,
        "member_id": 1,
        "department_code": "WORSHIP",
        "position_code": "ELDER",
        "appointed_on": "2024-01-01",
        "ordination_church": "중앙교회",
        "job_title": "부장",
        "workplace": "삼성전자",
        "workplace_phone": "02-1234-5678",
        "resign_on": null,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

### 3.2 멤버 사역 추가
**POST** `/api/v1/members/{member_id}/ministries`

**Request Body:**
```json
{
    "department_code": "EDUCATION",
    "position_code": "TEACHER",
    "appointed_on": "2024-02-01",
    "job_title": "교사",
    "workplace": "ABC 초등학교",
    "workplace_phone": "02-9876-5432"
}
```

**주요 부서 코드:**
- `WORSHIP`: 예배부
- `EDUCATION`: 교육부
- `MISSION`: 선교부
- `YOUTH`: 청년부
- `CHILDREN`: 아동부

**주요 직분 코드:**
- `PASTOR`: 목사
- `ELDER`: 장로
- `DEACON`: 집사
- `TEACHER`: 교사
- `LEADER`: 부장/회장

---

## 4. 성례(Sacrament) 관리

### 4.1 멤버 성례 기록 조회
**GET** `/api/v1/members/{member_id}/sacraments`

**Response:**
```json
[
    {
        "id": 1,
        "member_id": 1,
        "type": "세례",
        "date": "2020-04-12",
        "church_name": "중앙교회",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": 2,
        "member_id": 1,
        "type": "입교",
        "date": "2020-04-26",
        "church_name": "중앙교회",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

### 4.2 멤버 성례 기록 추가
**POST** `/api/v1/members/{member_id}/sacraments`

**Request Body:**
```json
{
    "type": "세례",
    "date": "2024-04-14",
    "church_name": "새빛교회"
}
```

**성례 유형:**
- `유아세례`: 유아 세례
- `세례`: 세례 (침례)
- `입교`: 입교
- `성찬`: 성찬

---

## 5. 이명/전출입(Transfer) 관리

### 5.1 멤버 이명 기록 조회
**GET** `/api/v1/members/{member_id}/transfers`

**Response:**
```json
[
    {
        "id": 1,
        "member_id": 1,
        "type": "in",
        "church_name": "구)중앙교회",
        "date": "2024-01-01",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

### 5.2 멤버 이명 기록 추가
**POST** `/api/v1/members/{member_id}/transfers`

**Request Body:**
```json
{
    "type": "out",
    "church_name": "새소망교회",
    "date": "2024-03-15"
}
```

**이명 유형:**
- `in`: 전입 (다른 교회에서 우리 교회로)
- `out`: 전출 (우리 교회에서 다른 교회로)

---

## 6. 코드(Code) 관리

### 6.1 교회 코드 목록 조회
**GET** `/api/v1/members/codes`

**Query Parameters:**
- `type` (string, optional): 코드 유형으로 필터링

**Response:**
```json
[
    {
        "id": 1,
        "church_id": 1,
        "type": "position",
        "code": "PASTOR",
        "label": "목사",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": 2,
        "church_id": 1,
        "type": "position",
        "code": "ELDER",
        "label": "장로",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

### 6.2 새 코드 생성
**POST** `/api/v1/members/codes`

**Request Body:**
```json
{
    "type": "department",
    "code": "MUSIC",
    "label": "찬양부"
}
```

**코드 유형:**
- `position`: 직분
- `department`: 부서
- `district`: 구역/교구
- `visit_type`: 심방 유형
- `marital_status`: 결혼 상태

---

## 7. 사용 예시

### 7.1 새 교인의 상세 정보 등록

```bash
# 1. 기본 멤버 정보는 기존 API로 생성
curl -X POST "http://localhost:8000/api/v1/members" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "김영수",
    "name_eng": "Kim Young Soo",
    "code": "M2024002",
    "birthdate": "1985-03-15",
    "gender": "M"
  }'

# 2. 연락처 추가
curl -X POST "http://localhost:8000/api/v1/members/1/contacts" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "mobile",
    "value": "010-9876-5432"
  }'

curl -X POST "http://localhost:8000/api/v1/members/1/contacts" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "value": "kim@example.com"
  }'

# 3. 세례 기록 추가
curl -X POST "http://localhost:8000/api/v1/members/1/sacraments" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "세례",
    "date": "2024-04-07",
    "church_name": "새빛교회"
  }'

# 4. 사역 배정
curl -X POST "http://localhost:8000/api/v1/members/1/ministries" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "department_code": "WORSHIP",
    "position_code": "DEACON",
    "appointed_on": "2024-05-01"
  }'
```

### 7.2 교인 종합 정보 조회

```bash
# 모든 관련 정보를 포함한 교인 조회
curl -X GET "http://localhost:8000/api/v1/members/1/enhanced" \
  -H "Authorization: Bearer <token>"
```

### 7.3 부서별 코드 조회

```bash
# 직분 코드만 조회
curl -X GET "http://localhost:8000/api/v1/members/codes?type=position" \
  -H "Authorization: Bearer <token>"

# 부서 코드만 조회
curl -X GET "http://localhost:8000/api/v1/members/codes?type=department" \
  -H "Authorization: Bearer <token>"
```

---

## 8. 데이터 검증 규칙

### 8.1 연락처
- `type`: 필수, 정해진 값 중 하나여야 함
- `value`: 필수, 타입에 따른 형식 검증

### 8.2 사역
- `department_code`, `position_code`: 해당 교회의 코드 테이블에 존재해야 함
- `appointed_on`: 날짜 형식 (YYYY-MM-DD)

### 8.3 성례
- `type`: 정해진 성례 유형 중 하나여야 함
- `date`: 날짜 형식 (YYYY-MM-DD)

### 8.4 이명
- `type`: "in" 또는 "out"만 허용
- `date`: 날짜 형식 (YYYY-MM-DD)

---

## 9. 에러 코드

| HTTP Status | 설명 | 예시 |
|-------------|------|------|
| 400 | 잘못된 요청 | 필수 필드 누락, 잘못된 데이터 형식 |
| 401 | 인증 실패 | JWT 토큰 없음 또는 만료 |
| 403 | 권한 없음 | 다른 교회 교인 정보 접근 시도 |
| 404 | 리소스 없음 | 존재하지 않는 교인 ID |
| 422 | 검증 오류 | 데이터 타입 불일치, 제약 조건 위반 |

---

## 10. 향후 기능

1. **일괄 처리**: 여러 교인의 정보를 한 번에 업데이트
2. **이력 관리**: 모든 변경 사항의 상세 이력 추적
3. **자동화**: 생일, 기념일 등의 자동 알림 기능
4. **통계**: 부서별, 직분별 통계 및 보고서 생성

---

## 11. 보안 및 개인정보보호

1. **접근 제어**: 교회별 데이터 격리, 역할 기반 접근 제어
2. **데이터 검증**: 모든 입력 데이터의 서버 사이드 검증
3. **감사 로그**: 중요한 정보 변경 시 자동 로그 기록
4. **암호화**: 민감한 정보의 암호화 저장

기술적 문의사항은 GitHub Issues를 통해 제출해 주세요.