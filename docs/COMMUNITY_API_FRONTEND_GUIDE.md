# 커뮤니티 회원 신청 API - 프론트엔드 가이드

## 📋 개요
외부 사용자(업체, 연주자, 사역자 등)의 커뮤니티 회원 신청 및 관리를 위한 API 가이드입니다.

## 🚀 베이스 URL
```
https://api.surfmind-team.com/api/v1
```

## 📝 API 엔드포인트

### 1. 커뮤니티 회원 신청서 제출 (공개 API)

**`POST /community/applications`**

#### 📤 요청 형식
- **Content-Type**: `multipart/form-data`
- **인증**: 불필요 (공개 API)

#### 📋 요청 필드

```typescript
interface CommunityApplicationRequest {
  // 필수 필드
  applicant_type: 'company' | 'individual' | 'musician' | 'minister' | 'organization' | 'other';
  organization_name: string;     // 단체/회사명
  contact_person: string;        // 담당자명
  email: string;                // 이메일 (중복 체크됨)
  phone: string;                // 연락처
  description: string;          // 상세 소개 및 신청 사유
  
  // 선택 필드
  business_number?: string;     // 사업자등록번호
  address?: string;            // 주소
  service_area?: string;       // 서비스 지역
  website?: string;           // 웹사이트/SNS
  attachments?: File[];       // 첨부파일 (최대 5개, 각 10MB)
}
```

#### 📎 파일 업로드 제한사항
- **허용 확장자**: pdf, jpg, jpeg, png, doc, docx
- **최대 파일 크기**: 10MB per file
- **최대 파일 개수**: 5개

#### 📥 성공 응답 (200 OK)
```json
{
  "success": true,
  "message": "신청서가 성공적으로 제출되었습니다.",
  "data": {
    "application_id": 123,
    "status": "pending",
    "submitted_at": "2024-09-08T10:30:00Z"
  }
}
```

#### ❌ 에러 응답 (400 Bad Request)
```json
{
  "success": false,
  "message": "이미 등록된 이메일입니다.",
  "data": {
    "error_code": "EMAIL_ALREADY_EXISTS"
  }
}
```

#### 🔗 프론트엔드 구현 예시

```javascript
const submitApplication = async (formData) => {
  const data = new FormData();
  
  // 기본 필드 추가
  data.append('applicant_type', formData.applicant_type);
  data.append('organization_name', formData.organization_name);
  data.append('contact_person', formData.contact_person);
  data.append('email', formData.email);
  data.append('phone', formData.phone);
  data.append('description', formData.description);
  
  // 선택 필드 추가 (값이 있을 때만)
  if (formData.business_number) {
    data.append('business_number', formData.business_number);
  }
  if (formData.address) {
    data.append('address', formData.address);
  }
  if (formData.service_area) {
    data.append('service_area', formData.service_area);
  }
  if (formData.website) {
    data.append('website', formData.website);
  }
  
  // 파일 첨부 (multiple files)
  if (formData.attachments && formData.attachments.length > 0) {
    formData.attachments.forEach(file => {
      data.append('attachments', file);
    });
  }
  
  try {
    const response = await fetch('https://api.surfmind-team.com/api/v1/community/applications', {
      method: 'POST',
      body: data
    });
    
    const result = await response.json();
    
    if (result.success) {
      alert('신청서가 성공적으로 제출되었습니다!');
      return result.data;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('신청서 제출 실패:', error);
    alert('신청서 제출 중 오류가 발생했습니다.');
    throw error;
  }
};
```

---

## 🛡️ 관리자 전용 API (슈퍼어드민만 접근 가능)

> **⚠️ 중요**: 모든 관리자 API는 `Authorization: Bearer {JWT_TOKEN}` 헤더가 필요하며, 슈퍼어드민 권한이 있어야 합니다.

### 2. 신청서 목록 조회

**`GET /admin/community/applications`**

#### 🔍 쿼리 파라미터

```typescript
interface ApplicationsQueryParams {
  page?: number;              // 페이지 번호 (default: 1)
  limit?: number;             // 페이지당 개수 (default: 20)
  status?: 'pending' | 'approved' | 'rejected' | 'all';  // 상태 필터
  applicant_type?: 'company' | 'individual' | 'musician' | 'minister' | 'organization' | 'other' | 'all';
  search?: string;            // 검색어 (조직명, 담당자명, 이메일)
  sort_by?: 'submitted_at' | 'reviewed_at' | 'organization_name';
  sort_order?: 'asc' | 'desc';
}
```

#### 📥 응답
```json
{
  "applications": [
    {
      "id": 1,
      "applicant_type": "company",
      "organization_name": "(주)교회음향시스템",
      "contact_person": "김○○",
      "email": "contact@churchsound.co.kr",
      "phone": "010-1234-5678",
      "status": "pending",
      "submitted_at": "2024-09-07T10:30:00Z",
      "reviewed_at": null
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 87,
    "per_page": 20
  },
  "statistics": {
    "pending": 12,
    "approved": 65,
    "rejected": 10,
    "total": 87
  }
}
```

#### 🔗 프론트엔드 구현 예시

```javascript
const getApplications = async (params = {}) => {
  const query = new URLSearchParams({
    page: params.page || 1,
    limit: params.limit || 20,
    ...params
  });
  
  try {
    const response = await fetch(`https://api.surfmind-team.com/api/v1/admin/community/applications?${query}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) throw new Error('Failed to fetch applications');
    
    return await response.json();
  } catch (error) {
    console.error('신청서 목록 조회 실패:', error);
    throw error;
  }
};
```

### 3. 신청서 상세 조회

**`GET /admin/community/applications/{application_id}`**

#### 📥 응답
```json
{
  "id": 1,
  "applicant_type": "company",
  "organization_name": "(주)교회음향시스템",
  "contact_person": "김○○",
  "email": "contact@churchsound.co.kr",
  "phone": "010-1234-5678",
  "business_number": "123-45-67890",
  "address": "서울시 강남구 테헤란로 123",
  "description": "교회 전문 음향장비 설치 및 유지보수 업체입니다...",
  "service_area": "전국",
  "website": "https://churchsound.co.kr",
  "attachments": [
    {
      "filename": "사업자등록증.pdf",
      "path": "/uploads/applications/1/business_license.pdf",
      "size": 245760
    }
  ],
  "status": "pending",
  "submitted_at": "2024-09-07T10:30:00Z",
  "reviewed_at": null,
  "reviewed_by": null,
  "rejection_reason": null,
  "notes": null,
  "created_at": "2024-09-07T10:30:00Z",
  "updated_at": "2024-09-07T10:30:00Z"
}
```

### 4. 신청서 승인

**`PUT /admin/community/applications/{application_id}/approve`**

#### 📤 요청
```json
{
  "notes": "우수한 경력 확인. 승인 처리함."
}
```

#### 📥 응답
```json
{
  "success": true,
  "message": "신청서가 승인되었습니다.",
  "data": {
    "application_id": 1,
    "status": "approved",
    "reviewed_at": "2024-09-08T14:20:00Z",
    "user_account": {
      "username": "churchsound_company",
      "temporary_password": "TempPass123!",
      "login_url": "https://admin.smartyoram.com/login"
    }
  }
}
```

### 5. 신청서 반려

**`PUT /admin/community/applications/{application_id}/reject`**

#### 📤 요청
```json
{
  "rejection_reason": "제출 서류가 불충분합니다. 사업자등록증과 보험가입증명서를 추가 제출해주세요.",
  "notes": "서류 보완 후 재신청 안내함."
}
```

#### 📥 응답
```json
{
  "success": true,
  "message": "신청서가 반려되었습니다.",
  "data": {
    "application_id": 1,
    "status": "rejected",
    "reviewed_at": "2024-09-08T14:20:00Z"
  }
}
```

### 6. 첨부파일 다운로드

**`GET /admin/community/applications/{application_id}/attachments/{filename}`**

#### 📥 응답
- 파일 바이너리 데이터
- Content-Disposition 헤더로 파일명 전달

#### 🔗 프론트엔드 구현 예시

```javascript
const downloadAttachment = async (applicationId, filename) => {
  try {
    const response = await fetch(
      `https://api.surfmind-team.com/api/v1/admin/community/applications/${applicationId}/attachments/${filename}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    );
    
    if (!response.ok) throw new Error('파일 다운로드 실패');
    
    // 파일 다운로드 처리
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (error) {
    console.error('파일 다운로드 실패:', error);
    alert('파일 다운로드 중 오류가 발생했습니다.');
  }
};
```

---

## 🎨 UI/UX 권장사항

### 신청서 제출 폼
1. **필수 필드 표시**: 필수 필드에 asterisk(*) 표시
2. **이메일 중복 체크**: 실시간 또는 제출 시 체크
3. **파일 업로드**: 드래그 앤 드롭 지원, 진행률 표시
4. **유효성 검사**: 클라이언트 사이드 검증 + 서버 에러 처리

### 관리자 대시보드
1. **상태별 통계**: 대기/승인/반려 건수 표시
2. **검색 및 필터**: 실시간 검색, 상태/유형별 필터
3. **페이지네이션**: 무한스크롤 또는 페이지 번호
4. **일괄 처리**: 체크박스로 다중 선택 후 일괄 승인/반려

---

## ⚠️ 에러 처리 가이드

### 공통 HTTP 상태 코드
- `200 OK`: 성공
- `400 Bad Request`: 잘못된 요청 (필수 필드 누락, 유효하지 않은 데이터)
- `401 Unauthorized`: 인증 실패 (토큰 없음/만료)
- `403 Forbidden`: 권한 부족 (슈퍼어드민 아님)
- `404 Not Found`: 리소스 없음 (신청서 ID 없음)
- `413 Payload Too Large`: 파일 크기 초과
- `422 Unprocessable Entity`: 이메일 중복 등 비즈니스 로직 오류
- `500 Internal Server Error`: 서버 오류

### 에러 응답 형식
```json
{
  "success": false,
  "message": "사용자 친화적인 에러 메시지",
  "data": {
    "error_code": "ERROR_CODE_IF_APPLICABLE",
    "details": "상세 에러 정보"
  }
}
```

---

## 🧪 테스트 가이드

### 신청서 제출 테스트 데이터
```json
{
  "applicant_type": "company",
  "organization_name": "테스트 회사",
  "contact_person": "김테스트",
  "email": "test@example.com",
  "phone": "010-1234-5678",
  "description": "테스트용 신청서입니다."
}
```

### 관리자 권한 확인
- 슈퍼어드민 계정으로 로그인 후 JWT 토큰 사용
- `church_id = 0`인 계정만 관리자 API 접근 가능

---

## 📞 문의 및 지원

구현 중 문제가 발생하거나 추가 기능이 필요한 경우 백엔드 개발팀에 문의해주세요.

**API 상태 확인**: `/api/v1/health` 엔드포인트로 서버 상태 확인 가능