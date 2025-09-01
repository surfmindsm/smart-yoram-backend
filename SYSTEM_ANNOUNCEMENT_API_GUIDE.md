# 시스템 공지사항 API 가이드

## 개요
시스템 관리자(church_id = 0)가 전체 또는 특정 교회들에게 공지사항을 전달할 수 있는 기능입니다.

## 시스템 관리자 계정 정보
- **사용자명**: `system_superadmin`
- **비밀번호**: `admin123!`
- **권한**: `system_admin`
- **church_id**: `0` (시스템 테넌트)

## 1. 공지 대상 선택 옵션

### target_type 필드
공지사항의 대상을 지정하는 필드입니다:

- `"all"`: 모든 교회에 공지 (전체 공지)
- `"specific"`: 특정 교회들만 선택해서 공지
- `"single"`: 단일 교회에만 공지

### 각 옵션별 사용법

#### 1) 전체 공지 (`target_type: "all"`)
```json
{
  "title": "전체 시스템 점검 안내",
  "content": "모든 교회에 공지되는 내용입니다.",
  "target_type": "all",
  "priority": "important",
  "start_date": "2025-09-01",
  "end_date": "2025-09-10"
}
```

#### 2) 특정 교회들 공지 (`target_type: "specific"`)
```json
{
  "title": "특정 교회들 대상 공지",
  "content": "선택된 교회들에만 공지되는 내용입니다.",
  "target_type": "specific", 
  "target_church_ids": [1, 6, 9999],
  "priority": "normal",
  "start_date": "2025-09-01",
  "end_date": null
}
```

#### 3) 단일 교회 공지 (`target_type: "single"`)
```json
{
  "title": "개별 교회 공지",
  "content": "특정 한 교회에만 공지되는 내용입니다.",
  "target_type": "single",
  "church_id": 6,
  "priority": "urgent", 
  "start_date": "2025-09-01",
  "end_date": "2025-09-03"
}
```

## 2. API 엔드포인트

### 2.1 교회 목록 조회 (드롭다운용)
```
GET /api/announcements/churches
Authorization: Bearer <token>
```

**응답:**
```json
[
  {
    "id": 1,
    "name": "성광교회",
    "pastor_name": "김목사",
    "address": "서울시 강남구",
    "member_count": 150
  },
  {
    "id": 6,  
    "name": "새생명교회",
    "pastor_name": "이목사",
    "address": "서울시 서초구",
    "member_count": 200
  }
]
```

### 2.2 공지사항 생성
```
POST /api/announcements/admin
Authorization: Bearer <token>
Content-Type: application/json
```

**요청 본문:**
```json
{
  "title": "공지사항 제목",
  "content": "공지사항 내용",
  "category": "system",
  "priority": "normal",        // "urgent", "important", "normal"
  "target_type": "specific",   // "all", "specific", "single" 
  "target_church_ids": [1, 6], // target_type이 "specific"일 때만
  "church_id": null,           // target_type이 "single"일 때만
  "start_date": "2025-09-01",  // 필수
  "end_date": "2025-09-10",    // 선택 (null 가능)
  "is_active": true
}
```

### 2.3 공지사항 수정
```
PUT /api/announcements/admin/{announcement_id}
Authorization: Bearer <token>
```

### 2.4 공지사항 삭제  
```
DELETE /api/announcements/admin/{announcement_id}
Authorization: Bearer <token>
```

### 2.5 모든 공지사항 조회
```
GET /api/announcements/admin
Authorization: Bearer <token>
```

## 3. 프론트엔드 구현 가이드

### 3.1 공지사항 작성 폼 구조

```typescript
interface AnnouncementForm {
  title: string;
  content: string;
  category: string;
  priority: 'urgent' | 'important' | 'normal';
  target_type: 'all' | 'specific' | 'single';
  target_church_ids?: number[];  // target_type이 'specific'일 때
  church_id?: number;            // target_type이 'single'일 때  
  start_date: string;            // YYYY-MM-DD 형식
  end_date?: string;             // YYYY-MM-DD 형식 또는 null
  is_active: boolean;
}
```

### 3.2 대상 선택 UI 로직

```typescript
const handleTargetTypeChange = (targetType: string) => {
  setFormData(prev => ({
    ...prev,
    target_type: targetType,
    target_church_ids: targetType === 'specific' ? [] : undefined,
    church_id: targetType === 'single' ? null : undefined
  }));
};

// target_type에 따른 조건부 렌더링
{formData.target_type === 'specific' && (
  <MultiSelectChurches 
    churches={churches}
    selected={formData.target_church_ids}
    onChange={(ids) => setFormData(prev => ({ ...prev, target_church_ids: ids }))}
  />
)}

{formData.target_type === 'single' && (
  <SingleSelectChurch
    churches={churches}
    selected={formData.church_id}
    onChange={(id) => setFormData(prev => ({ ...prev, church_id: id }))}
  />
)}
```

### 3.3 기간 설정 UI

```typescript
// 게시 기간 설정
<DatePicker
  label="게시 시작일"
  value={formData.start_date}
  onChange={(date) => setFormData(prev => ({ ...prev, start_date: date }))}
  required
/>

<DatePicker
  label="게시 종료일"
  value={formData.end_date}
  onChange={(date) => setFormData(prev => ({ ...prev, end_date: date }))}
  placeholder="종료일 미설정시 무제한"
  clearable
/>
```

### 3.4 우선순위 설정

```typescript
const priorityOptions = [
  { value: 'urgent', label: '긴급', color: 'red' },
  { value: 'important', label: '중요', color: 'orange' },
  { value: 'normal', label: '일반', color: 'blue' }
];

<Select
  options={priorityOptions}
  value={formData.priority}
  onChange={(priority) => setFormData(prev => ({ ...prev, priority }))}
/>
```

## 4. 권한 체크

### 4.1 시스템 관리자 확인
```typescript
const isSystemAdmin = user?.church_id === 0 && user?.role === 'system_admin';

// 메뉴 표시 여부
{isSystemAdmin && (
  <MenuItem>시스템 공지사항 관리</MenuItem>
)}
```

### 4.2 API 호출 시 권한 처리
```typescript
const createAnnouncement = async (data: AnnouncementForm) => {
  try {
    const response = await api.post('/api/announcements/admin', data);
    return response.data;
  } catch (error) {
    if (error.response?.status === 403) {
      alert('시스템 관리자만 접근 가능합니다.');
    }
    throw error;
  }
};
```

## 5. 사용자 경험 고려사항

### 5.1 대상 선택 가이드
- **전체 공지**: "모든 교회에 공지됩니다"
- **특정 교회**: "선택된 N개 교회에 공지됩니다"  
- **단일 교회**: "선택된 교회에만 공지됩니다"

### 5.2 기간 설정 가이드
- 시작일은 필수, 종료일은 선택
- 종료일 미설정시 "무제한" 표시
- 과거 날짜 선택 시 경고

### 5.3 미리보기 기능
```typescript
const previewTargets = () => {
  if (target_type === 'all') return '모든 교회';
  if (target_type === 'specific') return `${target_church_ids?.length}개 선택된 교회`;
  if (target_type === 'single') return selectedChurchName;
};
```

## 6. 에러 처리

### 6.1 유효성 검사
```typescript
const validateForm = (data: AnnouncementForm) => {
  if (data.target_type === 'specific' && (!data.target_church_ids || data.target_church_ids.length === 0)) {
    throw new Error('특정 교회 선택 시 최소 1개 교회를 선택해주세요.');
  }
  
  if (data.target_type === 'single' && !data.church_id) {
    throw new Error('단일 교회 선택 시 교회를 선택해주세요.');
  }
  
  if (!data.start_date) {
    throw new Error('게시 시작일은 필수입니다.');
  }
};
```

### 6.2 API 에러 메시지
- `400`: 잘못된 요청 (유효성 검사 실패)
- `403`: 권한 없음 (시스템 관리자가 아님)
- `404`: 공지사항을 찾을 수 없음

## 7. 테스트 시나리오

1. **전체 공지 생성**: target_type = 'all'로 공지 작성
2. **특정 교회 공지**: 2-3개 교회 선택하여 공지 작성  
3. **단일 교회 공지**: 1개 교회만 선택하여 공지 작성
4. **기간 설정**: 시작일/종료일 설정하여 활성화 확인
5. **우선순위 정렬**: urgent > important > normal 순서 확인
6. **권한 테스트**: 일반 사용자로 접근 시 403 에러 확인

이 가이드를 참고하여 시스템 공지사항 관리 기능을 구현하시면 됩니다!