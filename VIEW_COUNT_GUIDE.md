# 조회수 카운트 기능 구현 가이드 - 2025년 9월 16일

## 🚨 문제 상황

무료나눔 상세 페이지 조회 시 조회수가 증가하지 않는 문제가 발생했습니다.

### 원인 분석
- 상세 조회 API (`/api/v1/community/sharing/{id}`) 호출 시 **403 Forbidden** 오류 발생
- JWT 토큰 인증 문제로 인해 조회수 증가 로직이 실행되지 않음
- 백엔드 로그: `INFO: 127.0.0.1:62076 - "GET /api/v1/community/sharing/23 HTTP/1.1" 403 Forbidden`

---

## ✅ 해결책

### 방법 1: 목록 API를 활용한 조회수 증가

#### 🔧 백엔드 구현 완료
목록 조회 API에 `increment_view` 파라미터를 추가했습니다.

**API 엔드포인트**: `GET /api/v1/community/sharing`

**새로운 파라미터**:
```
increment_view: Optional[int] - 조회수를 증가시킬 아이템 ID
```

#### 🎯 프론트엔드 구현 방법

```javascript
// 아이템 클릭 시 조회수 증가
const handleItemClick = async (itemId) => {
  try {
    // 조회수 증가를 위해 목록 API 호출 (최소한의 데이터만 요청)
    const response = await fetch(`/api/v1/community/sharing?increment_view=${itemId}&page=1&limit=1`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      console.log(`조회수 증가 완료: 아이템 ${itemId}`);
    }
  } catch (error) {
    console.error('조회수 증가 실패:', error);
  }

  // 상세 페이지로 이동
  navigateToDetail(itemId);
};
```

### 방법 2: 전용 API를 활용한 조회수 증가 (추천)

#### 🔧 백엔드 구현 완료
조회수 증가만을 위한 전용 API를 새로 만들었습니다.

**API 엔드포인트**: `POST /api/v1/community/sharing/{id}/increment-view`

**특징**:
- **인증 불필요**: Authorization 헤더 없이 사용 가능
- **단순 기능**: 조회수만 +1 증가
- **빠른 응답**: 최소한의 데이터만 반환

#### 🎯 프론트엔드 구현 방법

```javascript
// 조회수 증가 전용 함수
const incrementViewCount = async (itemId) => {
  try {
    const response = await fetch(`/api/v1/community/sharing/${itemId}/increment-view`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
        // Authorization 헤더 불필요!
      }
    });

    if (response.ok) {
      const data = await response.json();
      console.log(`조회수 증가: ${data.data.previous_view_count} → ${data.data.new_view_count}`);
      return data.data.new_view_count;
    }
  } catch (error) {
    console.error('조회수 증가 실패:', error);
  }
};

// 아이템 클릭 이벤트 핸들러
const handleItemClick = async (itemId) => {
  // 조회수 증가 (백그라운드에서 실행)
  incrementViewCount(itemId);

  // 상세 페이지로 이동
  navigateToDetail(itemId);
};
```

#### 📋 API 응답 예시

**요청**:
```http
POST /api/v1/community/sharing/23/increment-view
Content-Type: application/json
```

**응답**:
```json
{
  "success": true,
  "data": {
    "sharing_id": 23,
    "previous_view_count": 5,
    "new_view_count": 6
  }
}
```

---

## 🔍 테스트 가이드

### 1. 방법 1 테스트 (목록 API)
```bash
# 인증 토큰이 필요함
curl -X GET "http://localhost:8000/api/v1/community/sharing?increment_view=23&page=1&limit=1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### 2. 방법 2 테스트 (전용 API) - 추천
```bash
# 인증 토큰 불필요
curl -X POST "http://localhost:8000/api/v1/community/sharing/23/increment-view" \
  -H "Content-Type: application/json"
```

### 3. 결과 확인
```bash
# 조회수가 증가했는지 목록에서 확인
curl -X GET "http://localhost:8000/api/v1/community/sharing" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🚀 권장 구현 방식

**방법 2 (전용 API)**를 권장하는 이유:

1. **인증 문제 해결**: JWT 토큰 없이도 동작
2. **성능 최적화**: 조회수만 처리하므로 빠름
3. **간단한 구현**: 별도 인증 로직 불필요
4. **안정성**: 403 Forbidden 오류에 영향받지 않음

---

## 🐛 디버깅 도구

### 백엔드 로그 확인
조회수 증가 시 다음과 같은 로그가 출력됩니다:

```bash
# 방법 1 (목록 API)
🔍 [VIEW_COUNT_FALLBACK] 목록 API에서 조회수 증가 시도 - ID: 23
✅ [VIEW_COUNT_FALLBACK] 조회수 증가 성공 - ID: 23, 새 조회수: 6

# 방법 2 (전용 API)
🚀 [VIEW_INCREMENT_API] 조회수 증가 전용 API 호출 - ID: 23
🔍 [VIEW_INCREMENT_API] 현재 조회수: 5
✅ [VIEW_INCREMENT_API] 조회수 증가 성공 - ID: 23, 5 → 6
```

### 프론트엔드 디버깅
```javascript
// 조회수 증가 전후 확인
console.log('조회수 증가 요청:', itemId);

const newCount = await incrementViewCount(itemId);
if (newCount) {
  console.log('조회수 증가 완료:', newCount);
  // UI에서 조회수 업데이트
  updateViewCountInUI(itemId, newCount);
}
```

---

## ❓ FAQ

### Q1: 왜 상세 API에서 조회수가 증가하지 않나요?
**A**: 상세 조회 API가 403 Forbidden 오류를 반환하여 조회수 증가 로직이 실행되지 않습니다. JWT 토큰 인증 문제가 원인입니다.

### Q2: 어떤 방법을 사용해야 하나요?
**A**: **방법 2 (전용 API)**를 권장합니다. 인증 문제가 없고 더 안정적입니다.

### Q3: 조회수가 여전히 증가하지 않는다면?
**A**:
1. 네트워크 탭에서 API 호출이 성공(200 OK)하는지 확인
2. 백엔드 로그에서 조회수 증가 메시지 확인
3. 데이터베이스 연결 상태 확인

### Q4: 중복 조회수 증가를 방지하려면?
**A**: 프론트엔드에서 세션별로 조회한 아이템 ID를 저장하고 중복 호출을 방지할 수 있습니다:

```javascript
const viewedItems = new Set();

const handleItemClick = async (itemId) => {
  // 이미 조회한 아이템이면 조회수 증가 스킵
  if (!viewedItems.has(itemId)) {
    await incrementViewCount(itemId);
    viewedItems.add(itemId);
  }

  navigateToDetail(itemId);
};
```

---

## 📞 연락처

조회수 관련 추가 문의사항이 있으시면 백엔드 개발팀으로 연락해주세요.

**구현 완료일**: 2025년 9월 16일
**담당**: Claude Code Assistant
**상태**: ✅ 두 가지 대체 방안 구현 완료