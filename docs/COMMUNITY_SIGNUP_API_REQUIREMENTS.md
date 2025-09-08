# 커뮤니티 회원 신청 시스템 API 요구사항

## 개요
교회 커뮤니티 외부 사용자(업체, 연주자, 사역자 등)의 회원가입 신청 및 관리를 위한 API입니다.

## 데이터베이스 테이블 설계

### community_applications 테이블
```sql
CREATE TABLE community_applications (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    applicant_type ENUM('company', 'individual', 'musician', 'minister', 'organization', 'other') NOT NULL COMMENT '신청자 유형',
    organization_name VARCHAR(200) NOT NULL COMMENT '단체/회사명',
    contact_person VARCHAR(100) NOT NULL COMMENT '담당자명',
    email VARCHAR(255) NOT NULL COMMENT '이메일',
    phone VARCHAR(50) NOT NULL COMMENT '연락처',
    business_number VARCHAR(50) NULL COMMENT '사업자등록번호',
    address TEXT NULL COMMENT '주소',
    description TEXT NOT NULL COMMENT '상세 소개 및 신청 사유',
    service_area VARCHAR(200) NULL COMMENT '서비스 지역',
    website VARCHAR(500) NULL COMMENT '웹사이트/SNS',
    attachments JSON NULL COMMENT '첨부파일 정보 [{"filename": "파일명", "path": "저장경로", "size": 크기}]',
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending' COMMENT '신청 상태',
    submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '신청일시',
    reviewed_at DATETIME NULL COMMENT '검토일시',
    reviewed_by BIGINT NULL COMMENT '검토자 ID',
    rejection_reason TEXT NULL COMMENT '반려 사유',
    notes TEXT NULL COMMENT '검토 메모',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_status (status),
    INDEX idx_submitted_at (submitted_at),
    INDEX idx_applicant_type (applicant_type),
    FOREIGN KEY (reviewed_by) REFERENCES users(id)
);
```

## API 엔드포인트

### 1. 회원 신청서 제출
**POST** `/api/v1/community/applications`

#### 요청 (multipart/form-data)
```typescript
interface CommunityApplicationRequest {
  applicant_type: 'company' | 'individual' | 'musician' | 'minister' | 'organization' | 'other';
  organization_name: string;
  contact_person: string;
  email: string;
  phone: string;
  business_number?: string;
  address?: string;
  description: string;
  service_area?: string;
  website?: string;
  attachments?: File[]; // 첨부파일들
}
```

#### 응답
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

#### 에러 응답
```json
{
  "success": false,
  "message": "이미 등록된 이메일입니다.",
  "error_code": "EMAIL_ALREADY_EXISTS"
}
```

### 2. 신청서 목록 조회 (슈퍼어드민 전용)
**GET** `/api/v1/admin/community/applications`

#### 쿼리 파라미터
```typescript
interface ApplicationsQueryParams {
  page?: number;           // 페이지 번호 (default: 1)
  limit?: number;          // 페이지당 개수 (default: 20)
  status?: 'pending' | 'approved' | 'rejected' | 'all';
  applicant_type?: 'company' | 'individual' | 'musician' | 'minister' | 'organization' | 'other' | 'all';
  search?: string;         // 검색어 (조직명, 담당자명, 이메일)
  sort_by?: 'submitted_at' | 'reviewed_at' | 'organization_name';
  sort_order?: 'asc' | 'desc';
}
```

#### 응답
```json
{
  "success": true,
  "data": {
    "applications": [
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
        "notes": null
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
}
```

### 3. 신청서 상세 조회 (슈퍼어드민 전용)
**GET** `/api/v1/admin/community/applications/{application_id}`

#### 응답
```json
{
  "success": true,
  "data": {
    "id": 1,
    "applicant_type": "company",
    "organization_name": "(주)교회음향시스템",
    // ... 모든 필드 포함
    "reviewer_info": {
      "id": 5,
      "name": "시스템관리자",
      "email": "admin@church.com"
    }
  }
}
```

### 4. 신청서 승인 (슈퍼어드민 전용)
**PUT** `/api/v1/admin/community/applications/{application_id}/approve`

#### 요청
```json
{
  "notes": "우수한 경력 확인. 승인 처리함."
}
```

#### 응답
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

#### 승인 후 처리사항
1. **사용자 계정 생성**
   - `users` 테이블에 새 계정 생성
   - `church_id = NULL` (커뮤니티 전용 사용자)
   - `role = 'community_user'`
   - 임시 비밀번호 생성

2. **이메일 발송**
   - 승인 완료 알림
   - 로그인 정보 (아이디, 임시 비밀번호)
   - 최초 로그인 시 비밀번호 변경 안내

### 5. 신청서 반려 (슈퍼어드민 전용)
**PUT** `/api/v1/admin/community/applications/{application_id}/reject`

#### 요청
```json
{
  "rejection_reason": "제출 서류가 불충분합니다. 사업자등록증과 보험가입증명서를 추가 제출해주세요.",
  "notes": "서류 보완 후 재신청 안내함."
}
```

#### 응답
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

#### 반려 후 처리사항
1. **이메일 발송**
   - 반려 알림
   - 상세 반려 사유
   - 재신청 방법 안내

### 6. 첨부파일 다운로드 (슈퍼어드민 전용)
**GET** `/api/v1/admin/community/applications/{application_id}/attachments/{filename}`

#### 응답
- 파일 바이너리 데이터
- Content-Disposition 헤더로 파일명 전달

## 권한 및 보안

### 접근 권한
- **신청서 제출**: 인증 불필요 (공개)
- **신청서 관리**: `church_id = 0` (슈퍼어드민) 전용

### 보안 고려사항
1. **파일 업로드 검증**
   - 허용 확장자: pdf, jpg, jpeg, png, doc, docx
   - 최대 파일 크기: 10MB per file
   - 최대 파일 개수: 5개

2. **데이터 검증**
   - 이메일 중복 체크
   - 필수 필드 검증
   - XSS, SQL Injection 방지

3. **API 레이트 리미팅**
   - 신청서 제출: IP당 하루 3회
   - 관리 API: 인증된 사용자만 접근

## 이메일 템플릿

### 승인 완료 이메일
```
제목: [스마트요람] 커뮤니티 회원 신청이 승인되었습니다

{신청자명}님, 안녕하세요.

스마트요람 커뮤니티 회원 신청이 승인되었습니다.

■ 로그인 정보
- 로그인 URL: https://admin.smartyoram.com/login  
- 아이디: {username}
- 임시 비밀번호: {temporary_password}

※ 최초 로그인 후 비밀번호를 변경해주세요.

감사합니다.
```

### 반려 알림 이메일
```
제목: [스마트요람] 커뮤니티 회원 신청 검토 결과

{신청자명}님, 안녕하세요.

아쉽게도 커뮤니티 회원 신청이 반려되었습니다.

■ 반려 사유
{rejection_reason}

■ 재신청 방법
필요한 서류를 보완하신 후 다시 신청해주시기 바랍니다.
신청 URL: https://admin.smartyoram.com/community-signup

문의사항이 있으시면 언제든 연락주세요.

감사합니다.
```

## 구현 참고사항

1. **파일 저장 구조**
   ```
   /uploads/community_applications/
   ├── {application_id}/
   │   ├── business_license.pdf
   │   ├── portfolio.pdf
   │   └── certificate.jpg
   ```

2. **로그 기록**
   - 신청서 제출/승인/반려 모든 액션 로깅
   - 슈퍼어드민의 모든 검토 활동 추적

3. **알림 시스템**
   - 새 신청서 제출 시 슈퍼어드민에게 알림
   - 승인/반려 처리 후 신청자에게 이메일 발송

4. **데이터 보관**
   - 반려된 신청서도 삭제하지 않고 보관
   - 승인된 사용자의 원본 신청서 정보 유지