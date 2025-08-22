# 목양 관리 API 위치 기능 업데이트 (v1.2.0)

## 📋 개요

목양 관리(Pastoral Care) API에 지도 기반 위치 관리 기능이 추가되었습니다. 사용자가 방문 주소와 위치 정보를 입력할 수 있고, 관리자가 지도 기반으로 요청을 관리할 수 있습니다.

**업데이트 일자**: 2025년 8월 22일  
**API 버전**: v1.2.0  
**브랜치**: `feat/geo2`

---

## 🆕 새로 추가된 필드들

### 기존 요청 생성/수정 API에 추가된 선택적 필드들:

```typescript
interface PastoralCareRequest {
  // 기존 필드들 (변경 없음)
  id: number;
  requester_name: string;
  requester_phone: string;
  request_type: string;
  request_content: string;
  preferred_date?: string;
  preferred_time_start?: string;
  preferred_time_end?: string;
  priority: string;
  
  // 🆕 새로 추가된 위치 관련 필드들
  address?: string;          // 방문 주소 (기본주소 + 상세주소)
  latitude?: number;         // 위도 (예: 37.5665000)
  longitude?: number;        // 경도 (예: 126.9780000)
  contact_info?: string;     // 추가 연락처 정보
  is_urgent?: boolean;       // 긴급 여부 (기본값: false)
  
  // 기존 응답 필드들 (변경 없음)
  status: string;
  created_at: string;
  // ... 기타 필드들
}
```

---

## 🔗 API 엔드포인트 변경사항

### 1. 기존 API 업데이트 (하위 호환성 보장)

모든 기존 API는 **하위 호환성을 완벽히 보장**하며, 새 필드들은 모두 **선택사항(optional)**입니다.

#### 1.1. 새 요청 생성
**`POST /api/v1/pastoral-care/requests`**

```javascript
// 기존 방식 (계속 작동)
{
  "requester_name": "김철수",
  "requester_phone": "010-1234-5678",
  "request_content": "병원 심방 요청"
}

// 🆕 새로운 방식 (위치 정보 포함)
{
  "requester_name": "김철수", 
  "requester_phone": "010-1234-5678",
  "request_content": "병원 심방 요청",
  "address": "서울대학교병원 본관 301호",
  "latitude": 37.5819,
  "longitude": 126.9668,
  "contact_info": "딸 연락처: 010-9876-5432, 병실직통: 02-2072-2114",
  "is_urgent": true
}
```

#### 1.2. 요청 수정
**`PUT /api/v1/pastoral-care/requests/{request_id}`**
**`PUT /api/v1/pastoral-care/admin/requests/{request_id}`** (관리자용)

동일하게 새 필드들을 포함하여 수정 가능합니다.

---

### 2. 새로운 API 엔드포인트 (관리자 전용)

#### 2.1. 위치 기반 검색
**`POST /api/v1/pastoral-care/admin/requests/search/location`**

특정 좌표 중심으로 반경 내의 목양 요청을 검색하고 거리순으로 정렬합니다.

```javascript
// 요청
{
  "latitude": 37.5665,
  "longitude": 126.9780,
  "radius_km": 5.0  // 반경 5km (기본값)
}

// 응답
[
  {
    "id": 123,
    "requester_name": "김철수",
    "address": "서울시 중구 세종대로 110",
    "latitude": 37.5663,
    "longitude": 126.9779,
    "distance_km": 0.15,  // 🆕 거리 정보 (km)
    "is_urgent": true,
    // ... 기타 필드들
  }
]
```

#### 2.2. 긴급 요청 조회  
**`GET /api/v1/pastoral-care/admin/requests/urgent`**

긴급 표시된 활성 상태의 목양 요청들을 조회합니다.

```javascript
// 응답: PastoralCareRequest[] 형태
[
  {
    "id": 124,
    "requester_name": "박영희",
    "is_urgent": true,
    "status": "pending",
    // ... 기타 필드들
  }
]
```

#### 2.3. 위치 정보 포함 요청 조회
**`GET /api/v1/pastoral-care/admin/requests/with-location`**

위치 정보(주소, 좌표)가 입력된 목양 요청들만 조회합니다.

```javascript
// 응답: 위치 정보가 있는 요청들
[
  {
    "id": 125,
    "address": "서울시 강남구 테헤란로 123",
    "latitude": 37.5019,
    "longitude": 127.0398,
    // ... 기타 필드들
  }
]
```

---

## 🎨 프론트엔드 구현 가이드

### 1. 폼 입력 필드 추가

```jsx
// 목양 요청 생성/수정 폼에 추가할 필드들
function PastoralCareRequestForm() {
  return (
    <form>
      {/* 기존 필드들 */}
      <input name="requester_name" placeholder="요청자명" required />
      <input name="requester_phone" placeholder="연락처" required />
      <textarea name="request_content" placeholder="요청 내용" required />
      
      {/* 🆕 새로 추가할 위치 관련 필드들 */}
      <input 
        name="address" 
        placeholder="방문 주소 (예: 서울대병원 301호)" 
      />
      
      <div className="location-fields">
        <input 
          name="latitude" 
          type="number" 
          step="0.0000001"
          placeholder="위도" 
        />
        <input 
          name="longitude" 
          type="number" 
          step="0.0000001" 
          placeholder="경도" 
        />
        <button type="button" onClick={getCurrentLocation}>
          현재 위치
        </button>
      </div>
      
      <textarea 
        name="contact_info" 
        placeholder="추가 연락처 (병실 직통전화, 가족 연락처 등)" 
      />
      
      <label>
        <input name="is_urgent" type="checkbox" />
        긴급 요청
      </label>
    </form>
  );
}
```

### 2. 지도 연동 예시

```javascript
// 카카오맵 또는 네이버맵 연동 예시
function AddressToCoordinates() {
  const handleAddressSearch = async (address) => {
    try {
      // 주소 -> 좌표 변환 (예: 카카오 지도 API)
      const coords = await geocodeAddress(address);
      setLatitude(coords.lat);
      setLongitude(coords.lng);
    } catch (error) {
      console.error('주소 변환 실패:', error);
    }
  };
  
  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude);
          setLongitude(position.coords.longitude);
        },
        (error) => console.error('위치 정보 획득 실패:', error)
      );
    }
  };
}
```

### 3. 관리자 위치 기반 검색 구현

```jsx
// 관리자 패널의 위치 기반 검색
function LocationBasedSearch() {
  const [searchLocation, setSearchLocation] = useState({
    latitude: 37.5665,  // 서울 시청 좌표 기본값
    longitude: 126.9780,
    radius_km: 5.0
  });
  
  const handleLocationSearch = async () => {
    try {
      const response = await fetch('/api/v1/pastoral-care/admin/requests/search/location', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchLocation)
      });
      
      const requestsWithDistance = await response.json();
      
      // 지도에 마커 표시 및 거리순 리스트 표시
      displayRequestsOnMap(requestsWithDistance);
    } catch (error) {
      console.error('위치 검색 실패:', error);
    }
  };
}
```

---

## 📱 UI/UX 권장사항

### 1. 사용자 입력 폼
- **주소 입력**: 자동완성 기능 제공 (카카오/네이버 주소 검색 API 활용)
- **위치 버튼**: "현재 위치 사용" 버튼으로 GPS 좌표 자동 입력
- **긴급 표시**: 체크박스 또는 토글 스위치로 명확하게 표시
- **추가 연락처**: 여러 연락처 입력 가능하도록 텍스트영역 제공

### 2. 관리자 대시보드
- **긴급 요청 알림**: 메인 대시보드에 긴급 요청 개수 배지 표시
- **지도 뷰**: 위치 정보가 있는 요청들을 지도에 마커로 표시
- **거리 표시**: 검색 결과에 거리 정보를 "1.2km" 형태로 표시
- **필터링**: "위치 정보 있음", "긴급 요청만" 등의 필터 옵션

### 3. 반응형 고려사항
- **모바일**: 위치 입력 시 GPS 사용 권장
- **데스크톱**: 지도 뷰어로 시각적 관리 가능
- **접근성**: 위치 정보 동의 및 프라이버시 안내 필수

---

## 🔧 기술 세부사항

### 1. 데이터 타입 정보
```typescript
interface LocationQuery {
  latitude: number;        // 소수점 8자리 정밀도
  longitude: number;       // 소수점 8자리 정밀도
  radius_km?: number;      // 기본값: 5.0km
}

interface PastoralCareRequestWithDistance extends PastoralCareRequest {
  distance_km?: number;    // 소수점 2자리 (km 단위)
}
```

### 2. 거리 계산 방식
- **공식**: Haversine 공식 사용 (지구 곡률 고려한 정확한 거리)
- **단위**: 킬로미터(km), 소수점 2자리까지
- **정밀도**: 약 10m 단위의 정확도

### 3. 데이터베이스 인덱스
- `idx_pastoral_care_location` (latitude, longitude)
- `idx_pastoral_care_is_urgent` (is_urgent)

---

## ⚠️ 주의사항 및 제한사항

### 1. 데이터 검증
- **위도**: -90 ~ 90 범위
- **경도**: -180 ~ 180 범위  
- **주소**: 최대 500자
- **추가 연락처**: 최대 500자

### 2. 개인정보 보호
- 위치 정보 수집 시 사용자 동의 필수
- 정확한 좌표 정보는 관리자만 조회 가능
- 일반 사용자는 자신의 요청만 위치 정보 확인

### 3. 성능 고려사항
- 위치 기반 검색은 교회별로 제한됨 (church_id 필터링)
- 대량 데이터 시 반경 검색에 시간이 소요될 수 있음
- 캐싱 고려 권장 (동일 위치 반복 검색 시)

---

## 🧪 테스트 시나리오

### 1. 기본 기능 테스트
- [ ] 기존 API 호출 (새 필드 없이) 정상 작동 확인
- [ ] 새 필드 포함 요청 생성/수정 테스트
- [ ] 위치 기반 검색 (다양한 반경으로)
- [ ] 긴급 요청 필터링 테스트

### 2. 경계값 테스트
- [ ] 위도/경도 범위 초과 값 입력
- [ ] 매우 긴 주소/연락처 정보 입력
- [ ] 0km 반경 검색 (동일 위치)
- [ ] 매우 큰 반경 검색 (100km 이상)

### 3. 권한 테스트
- [ ] 일반 사용자의 관리자 전용 API 접근 차단
- [ ] 교회별 데이터 격리 확인
- [ ] 타 교회 데이터 접근 차단

---

## 💾 데이터베이스 마이그레이션 

**⚠️ 중요**: API를 사용하기 전에 데이터베이스에 새 컬럼들을 추가해야 합니다.

### 자동 마이그레이션 (권장)
```bash
# 백엔드 프로젝트 디렉토리에서
alembic upgrade head
```

### 수동 마이그레이션 (필요시)
프로젝트 루트의 `MANUAL_MIGRATION_PASTORAL_CARE.sql` 파일을 실행하세요:

```sql
-- 새 컬럼들 추가
ALTER TABLE public.pastoral_care_requests 
ADD COLUMN IF NOT EXISTS address VARCHAR(500),
ADD COLUMN IF NOT EXISTS latitude NUMERIC(10,8),
ADD COLUMN IF NOT EXISTS longitude NUMERIC(11,8),
ADD COLUMN IF NOT EXISTS contact_info VARCHAR(500),
ADD COLUMN IF NOT EXISTS is_urgent BOOLEAN DEFAULT FALSE;

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_pastoral_care_location 
ON public.pastoral_care_requests (latitude, longitude);

CREATE INDEX IF NOT EXISTS idx_pastoral_care_is_urgent 
ON public.pastoral_care_requests (is_urgent);
```

### 마이그레이션 확인
```sql
-- 컬럼 확인
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'pastoral_care_requests' 
AND table_schema = 'public'
ORDER BY ordinal_position;

-- 인덱스 확인  
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'pastoral_care_requests';
```

---

## 📞 문의 및 지원

구현 중 문제가 발생하거나 추가 기능이 필요한 경우:

1. **GitHub Issues**: 버그 리포트 및 기능 요청
2. **API 문서**: `/api/v1/docs` (Swagger UI)
3. **마이그레이션 문제**: `MANUAL_MIGRATION_PASTORAL_CARE.sql` 파일 참조
4. **백엔드 팀 연락처**: [담당자 정보]

---

## 📝 변경 로그

### v1.2.0 (2025-08-22)
- ✅ 목양 요청에 위치 필드 5개 추가
- ✅ 위치 기반 검색 API 구현
- ✅ 긴급 요청 필터링 기능
- ✅ 거리 계산 (Haversine 공식)
- ✅ 데이터베이스 마이그레이션 완료
- ✅ 하위 호환성 보장

---

> 🚀 **Happy Coding!**  
> 이 업데이트로 목양 관리가 한층 더 효율적이고 직관적으로 개선될 것입니다.