# 재정 관리 API 문서

## 개요
Smart Yoram 재정 관리 API는 교회의 헌금, 기부자, 영수증 관리를 위한 종합적인 기능을 제공합니다.

## 인증
모든 API는 JWT 토큰을 통한 인증이 필요합니다.
```
Authorization: Bearer <your-jwt-token>
```

## 기본 응답 구조
```json
{
    "success": true,
    "data": {},
    "message": "Success"
}
```

## 에러 응답 구조
```json
{
    "detail": "Error message"
}
```

---

## 1. 기부자(Donor) 관리

### 1.1 기부자 목록 조회
**GET** `/api/v1/financial/donors`

**Query Parameters:**
- `skip` (integer, optional): 건너뛸 항목 수 (기본값: 0)
- `limit` (integer, optional): 가져올 항목 수 (기본값: 100)

**Response:**
```json
[
    {
        "id": 1,
        "member_id": 123,
        "legal_name": "홍길동",
        "address": "서울시 강남구 역삼동",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

### 1.2 기부자 생성
**POST** `/api/v1/financial/donors`

**Request Body:**
```json
{
    "member_id": 123,
    "legal_name": "홍길동",
    "address": "서울시 강남구 역삼동",
    "rrn_encrypted": "encrypted_rrn_here"
}
```

### 1.3 기부자 상세 조회
**GET** `/api/v1/financial/donors/{donor_id}`

---

## 2. 헌금(Offering) 관리

### 2.1 헌금 목록 조회
**GET** `/api/v1/financial/offerings`

**Query Parameters:**
- `donor_id` (integer, optional): 기부자 ID로 필터링
- `fund_type` (string, optional): 헌금 유형으로 필터링
- `start_date` (date, optional): 시작 날짜 (YYYY-MM-DD)
- `end_date` (date, optional): 종료 날짜 (YYYY-MM-DD)
- `skip` (integer, optional): 건너뛸 항목 수
- `limit` (integer, optional): 가져올 항목 수

**Response:**
```json
[
    {
        "id": 1,
        "donor_id": 1,
        "church_id": 1,
        "offered_on": "2024-01-07",
        "fund_type": "십일조",
        "amount": "100000.00",
        "note": "1월 십일조",
        "input_user_id": 1,
        "created_at": "2024-01-07T10:00:00Z",
        "updated_at": "2024-01-07T10:00:00Z"
    }
]
```

### 2.2 헌금 기록 생성
**POST** `/api/v1/financial/offerings`

**Request Body:**
```json
{
    "donor_id": 1,
    "church_id": 1,
    "offered_on": "2024-01-07",
    "fund_type": "십일조",
    "amount": "100000.00",
    "note": "1월 십일조"
}
```

---

## 3. 헌금 유형(Fund Type) 관리

### 3.1 헌금 유형 목록 조회
**GET** `/api/v1/financial/fund-types`

**Query Parameters:**
- `is_active` (boolean, optional): 활성 상태로 필터링 (기본값: true)

**Response:**
```json
[
    {
        "id": 1,
        "church_id": 1,
        "code": "TITHE",
        "name": "십일조",
        "description": "매월 소득의 십분의 일",
        "is_active": true,
        "sort_order": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

### 3.2 헌금 유형 생성
**POST** `/api/v1/financial/fund-types`

**Request Body:**
```json
{
    "church_id": 1,
    "code": "THANKSGIVING",
    "name": "감사헌금",
    "description": "감사의 마음으로 드리는 헌금",
    "is_active": true,
    "sort_order": 2
}
```

---

## 4. 영수증(Receipt) 관리

### 4.1 영수증 목록 조회
**GET** `/api/v1/financial/receipts`

**Query Parameters:**
- `tax_year` (integer, optional): 귀속연도로 필터링
- `donor_id` (integer, optional): 기부자 ID로 필터링
- `skip`, `limit`: 페이지네이션

**Response:**
```json
[
    {
        "id": 1,
        "church_id": 1,
        "donor_id": 1,
        "tax_year": 2024,
        "issue_no": "2024-00001",
        "issued_by": 1,
        "issued_at": "2024-12-31T15:30:00Z",
        "canceled_at": null,
        "created_at": "2024-12-31T15:30:00Z",
        "updated_at": "2024-12-31T15:30:00Z"
    }
]
```

### 4.2 영수증 생성
**POST** `/api/v1/financial/receipts`

**Request Body:**
```json
{
    "church_id": 1,
    "donor_id": 1,
    "tax_year": 2024,
    "issue_no": "2024-00001"
}
```

---

## 5. 통계 및 보고서

### 5.1 헌금 요약 통계
**GET** `/api/v1/financial/statistics/offerings-summary`

**Query Parameters:**
- `start_date` (date, required): 시작 날짜
- `end_date` (date, required): 종료 날짜
- `group_by` (string, required): 그룹화 기준 ("fund_type" 또는 "month")

**Response (fund_type로 그룹화):**
```json
[
    {
        "fund_type": "십일조",
        "total_amount": "1200000.00",
        "offering_count": 12,
        "period_start": "2024-01-01",
        "period_end": "2024-12-31"
    },
    {
        "fund_type": "감사헌금",
        "total_amount": "500000.00",
        "offering_count": 8,
        "period_start": "2024-01-01",
        "period_end": "2024-12-31"
    }
]
```

**Response (month로 그룹화):**
```json
[
    {
        "fund_type": "2024-01",
        "total_amount": "150000.00",
        "offering_count": 5,
        "period_start": "2024-01-01",
        "period_end": "2024-12-31"
    }
]
```

### 5.2 기부자 요약 통계
**GET** `/api/v1/financial/statistics/donor-summary`

**Query Parameters:**
- `start_date` (date, required): 시작 날짜
- `end_date` (date, required): 종료 날짜
- `limit` (integer, optional): 상위 기부자 수 (기본값: 50, 최대: 100)

**Response:**
```json
[
    {
        "donor_id": 1,
        "donor_name": "홍길동",
        "total_amount": "1200000.00",
        "offering_count": 12,
        "fund_types": ["십일조", "감사헌금", "건축헌금"]
    },
    {
        "donor_id": 2,
        "donor_name": "김철수",
        "total_amount": "800000.00",
        "offering_count": 10,
        "fund_types": ["십일조", "선교헌금"]
    }
]
```

---

## 에러 코드

| HTTP Status | 코드 | 설명 |
|-------------|------|------|
| 400 | Bad Request | 잘못된 요청 데이터 |
| 401 | Unauthorized | 인증되지 않은 사용자 |
| 403 | Forbidden | 권한 없음 |
| 404 | Not Found | 리소스를 찾을 수 없음 |
| 422 | Validation Error | 데이터 검증 실패 |
| 500 | Internal Server Error | 서버 내부 오류 |

---

## 사용 예시

### 1. 새로운 헌금 기록 생성 과정

```bash
# 1. 기부자 생성 (교인이 아닌 경우)
curl -X POST "http://localhost:8000/api/v1/financial/donors" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "legal_name": "홍길동",
    "address": "서울시 강남구 역삼동"
  }'

# 2. 헌금 기록 생성
curl -X POST "http://localhost:8000/api/v1/financial/offerings" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "donor_id": 1,
    "church_id": 1,
    "offered_on": "2024-01-07",
    "fund_type": "십일조",
    "amount": "100000.00",
    "note": "1월 첫째 주 십일조"
  }'
```

### 2. 월별 헌금 통계 조회

```bash
curl -X GET "http://localhost:8000/api/v1/financial/statistics/offerings-summary?start_date=2024-01-01&end_date=2024-12-31&group_by=month" \
  -H "Authorization: Bearer <token>"
```

### 3. 특정 기부자의 헌금 내역 조회

```bash
curl -X GET "http://localhost:8000/api/v1/financial/offerings?donor_id=1&start_date=2024-01-01&end_date=2024-12-31" \
  -H "Authorization: Bearer <token>"
```

---

## 보안 고려사항

1. **개인정보보호**: 주민등록번호는 암호화되어 저장됩니다.
2. **권한 관리**: 재정 정보는 적절한 권한을 가진 사용자만 접근 가능합니다.
3. **감사 로그**: 모든 재정 관련 작업은 로그로 기록됩니다.
4. **데이터 검증**: 모든 입력 데이터는 서버에서 검증됩니다.

---

## 향후 기능

1. **영수증 PDF 생성**: 기부금 영수증 PDF 자동 생성 및 다운로드
2. **자동 집계**: 정기적인 재정 보고서 자동 생성
3. **Excel 내보내기**: 헌금 데이터의 Excel 파일 내보내기
4. **알림 기능**: 헌금 목표 달성 시 알림 발송

---

## 지원 및 문의

기술적 문의사항이나 버그 리포트는 GitHub Issues를 통해 제출해 주세요.