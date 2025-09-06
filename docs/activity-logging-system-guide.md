# 📋 활동 로깅 시스템 API 가이드

**개인정보보호법 및 GDPR 준수를 위한 포괄적인 사용자 활동 추적 시스템**

---

## 🎯 개요

Smart Yoram 백엔드에 개인정보보호법 및 GDPR 준수를 위한 활동 로깅 시스템이 구축되었습니다. 모든 개인정보 접근, 수정, 삭제 작업을 자동으로 추적하여 완전한 감사 추적(Audit Trail)을 제공합니다.

## 🔗 API 엔드포인트 목록

### 1. 활동 로그 저장 (필수 구현)
```
POST /api/v1/auth/activity-logs
Content-Type: application/json
Authorization: Bearer {access_token}
```

### 2. 로그 조회 (관리자용)
```
GET /api/v1/auth/activity-logs
Authorization: Bearer {admin_access_token}
```

### 3. 통계 조회 (대시보드용)
```
GET /api/v1/auth/activity-logs/stats/summary
Authorization: Bearer {access_token}
```

---

## 📤 1. 활동 로그 저장 API

### Request Format
```javascript
POST /api/v1/auth/activity-logs
{
  "logs": [
    {
      "user_id": "123",                    // 현재 로그인한 사용자 ID (필수)
      "action": "view",                    // 액션 타입 (필수)
      "resource": "member",                // 리소스 타입 (필수)
      "target_id": "456",                  // 대상 ID (선택)
      "target_name": "홍길동",             // 대상 이름 (선택)
      "page_path": "/member-management",   // 현재 페이지 경로 (필수)
      "page_name": "교인 상세조회",        // 화면명 (필수)
      "details": {                         // 상세 정보 (선택)
        "accessed_fields": ["name", "email", "phone"],
        "view_type": "detail_modal",
        "browser": "Chrome",
        "screen_resolution": "1920x1080"
      },
      "sensitive_data": ["name", "email", "phone", "address"] // 민감 정보 필드 (필수)
    }
  ]
}
```

### Response (성공)
```javascript
{
  "success": true,
  "message": "활동 로그가 성공적으로 저장되었습니다",
  "inserted_count": 1,
  "timestamp": "2025-09-06T15:30:45.456Z"
}
```

### Response (오류)
```javascript
{
  "success": false,
  "error": "INVALID_ACTION",
  "message": "유효하지 않은 액션 타입입니다",
  "details": {
    "invalid_actions": ["invalid_action"],
    "valid_actions": ["view", "create", "update", "delete", "search", "login", "logout"]
  }
}
```

---

## 📊 2. 로그 조회 API (관리자용)

### Request Format
```javascript
GET /api/v1/auth/activity-logs?page=1&limit=50&user_id=123&action=view&resource=member&start_date=2025-09-01&end_date=2025-09-06&search=홍길동
```

### Query Parameters
| 파라미터 | 타입 | 필수 | 설명 | 기본값 |
|---------|------|------|------|--------|
| page | number | X | 페이지 번호 | 1 |
| limit | number | X | 페이지당 항목 수 (최대 200) | 50 |
| user_id | string | X | 특정 사용자 필터링 | - |
| action | string | X | 액션 타입 필터링 | - |
| resource | string | X | 리소스 타입 필터링 | - |
| start_date | string | X | 시작 날짜 (YYYY-MM-DD) | - |
| end_date | string | X | 종료 날짜 (YYYY-MM-DD) | - |
| search | string | X | 대상 이름 검색 | - |
| ip_address | string | X | IP 주소 필터링 | - |

### Response
```javascript
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": 84,
        "user_id": "123",
        "timestamp": "2025-09-06T15:30:45.123Z",
        "action": "view",
        "resource": "member",
        "target_id": "456",
        "target_name": "홍길동",
        "page_name": "교인 상세조회",
        "ip_address": "192.168.1.100",
        "sensitive_data_count": 5
      }
    ],
    "pagination": {
      "total_count": 1247,
      "page": 1,
      "limit": 50,
      "total_pages": 25
    }
  }
}
```

---

## 📈 3. 통계 조회 API

### Request Format
```javascript
GET /api/v1/auth/activity-logs/stats/summary
```

### Response
```javascript
{
  "total_logs": 1247,
  "today_logs": 45,
  "week_logs": 312,
  "month_logs": 1156,
  "action_breakdown": {
    "view": 856,
    "update": 234,
    "create": 89,
    "delete": 23,
    "search": 45
  },
  "resource_breakdown": {
    "member": 1023,
    "attendance": 134,
    "financial": 56,
    "bulletin": 34
  },
  "top_users": [
    {"user_id": "123", "log_count": 456},
    {"user_id": "456", "log_count": 234}
  ],
  "sensitive_data_access_count": 892
}
```

---

## 🔧 프론트엔드 구현 가이드

### 1. 필수 구현 사항

#### A. 교인 상세조회 시 로깅
```javascript
// 교인 정보 조회 후 자동으로 활동 로그 저장
const viewMemberDetail = async (memberId) => {
  try {
    // 1. 교인 정보 조회
    const response = await api.get(`/members/${memberId}`);
    const member = response.data;
    
    // 2. 활동 로그 저장 (비동기, 에러 무시)
    logActivity({
      action: 'view',
      resource: 'member',
      target_id: memberId.toString(),
      target_name: member.name,
      page_path: '/member-management',
      page_name: '교인 상세조회',
      details: {
        accessed_fields: ['name', 'email', 'phone', 'address', 'birthdate'],
        view_type: 'detail_modal',
        browser: getBrowserInfo(),
        screen_resolution: `${screen.width}x${screen.height}`,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: navigator.language
      },
      sensitive_data: ['name', 'email', 'phone', 'address', 'birthdate']
    });
    
    return member;
  } catch (error) {
    console.error('교인 조회 실패:', error);
    throw error;
  }
};
```

#### B. 교인 정보 수정 시 로깅
```javascript
const updateMember = async (memberId, updateData) => {
  try {
    // 1. 기존 정보 백업 (변경 추적용)
    const oldMember = await api.get(`/members/${memberId}`);
    
    // 2. 정보 수정
    const response = await api.put(`/members/${memberId}`, updateData);
    
    // 3. 변경된 필드 추출
    const changedFields = Object.keys(updateData);
    const oldValues = {};
    changedFields.forEach(field => {
      oldValues[field] = oldMember.data[field];
    });
    
    // 4. 활동 로그 저장
    logActivity({
      action: 'update',
      resource: 'member',
      target_id: memberId.toString(),
      target_name: updateData.name || oldMember.data.name,
      page_path: '/member-management/edit',
      page_name: '교인 정보 수정',
      details: {
        updated_fields: changedFields,
        old_values: oldValues,
        update_type: 'form_edit',
        form_section: getCurrentFormSection()
      },
      sensitive_data: changedFields
    });
    
    return response.data;
  } catch (error) {
    console.error('교인 정보 수정 실패:', error);
    throw error;
  }
};
```

#### C. 교인 검색 시 로깅
```javascript
const searchMembers = async (searchTerm) => {
  try {
    const response = await api.get(`/members/?search=${encodeURIComponent(searchTerm)}`);
    
    // 검색 활동 로깅
    logActivity({
      action: 'search',
      resource: 'member',
      target_name: `검색: ${searchTerm}`,
      page_path: '/member-management',
      page_name: '교인 검색',
      details: {
        search_term: searchTerm,
        result_count: response.data.length,
        search_type: 'name_search',
        filters_applied: getCurrentFilters()
      },
      sensitive_data: response.data.length > 0 ? ['search_results'] : []
    });
    
    return response.data;
  } catch (error) {
    console.error('교인 검색 실패:', error);
    throw error;
  }
};
```

#### D. 교인 삭제 시 로깅
```javascript
const deleteMember = async (memberId, memberName) => {
  try {
    await api.delete(`/members/${memberId}`);
    
    // 삭제 활동 로깅
    logActivity({
      action: 'delete',
      resource: 'member',
      target_id: memberId.toString(),
      target_name: memberName,
      page_path: '/member-management',
      page_name: '교인 삭제',
      details: {
        deletion_reason: '관리자 요청',
        confirmation_time: new Date().toISOString(),
        deleted_by: getCurrentUser().name
      },
      sensitive_data: ['all_member_data']
    });
    
  } catch (error) {
    console.error('교인 삭제 실패:', error);
    throw error;
  }
};
```

### 2. 공통 유틸리티 함수

#### A. 활동 로깅 헬퍼 함수
```javascript
// utils/activityLogger.js
class ActivityLogger {
  constructor() {
    this.queue = [];
    this.batchSize = 10;
    this.flushInterval = 5000; // 5초마다 자동 플러시
    
    // 자동 플러시 설정
    setInterval(() => this.flush(), this.flushInterval);
  }
  
  log(activityData) {
    // 현재 사용자 정보 자동 추가
    const currentUser = getCurrentUser();
    if (!currentUser) {
      console.warn('로그인하지 않은 사용자의 활동 로그 시도');
      return;
    }
    
    const completeLog = {
      user_id: currentUser.id.toString(),
      timestamp: new Date().toISOString(),
      ...activityData
    };
    
    this.queue.push(completeLog);
    
    // 큐가 가득 차면 즉시 플러시
    if (this.queue.length >= this.batchSize) {
      this.flush();
    }
  }
  
  async flush() {
    if (this.queue.length === 0) return;
    
    const logsToSend = [...this.queue];
    this.queue = [];
    
    try {
      await api.post('/auth/activity-logs', {
        logs: logsToSend
      });
      
      console.log(`✅ ${logsToSend.length}개 활동 로그 저장 완료`);
    } catch (error) {
      console.error('❌ 활동 로그 저장 실패:', error);
      // 실패한 로그는 다시 큐에 추가 (최대 3회 재시도)
      logsToSend.forEach(log => {
        log._retryCount = (log._retryCount || 0) + 1;
        if (log._retryCount <= 3) {
          this.queue.unshift(log);
        }
      });
    }
  }
  
  // 페이지 언로드 시 강제 플러시
  forceFlush() {
    if (this.queue.length > 0) {
      // 동기식으로 전송 (페이지 종료 전)
      navigator.sendBeacon('/api/v1/auth/activity-logs', 
        JSON.stringify({logs: this.queue}));
    }
  }
}

// 전역 인스턴스
const activityLogger = new ActivityLogger();

// 페이지 언로드 시 자동 플러시
window.addEventListener('beforeunload', () => {
  activityLogger.forceFlush();
});

// 공개 API
export const logActivity = (data) => activityLogger.log(data);
```

#### B. 브라우저 정보 추출
```javascript
// utils/browserInfo.js
export const getBrowserInfo = () => {
  const ua = navigator.userAgent;
  
  if (ua.includes('Chrome')) return 'Chrome';
  if (ua.includes('Firefox')) return 'Firefox';
  if (ua.includes('Safari') && !ua.includes('Chrome')) return 'Safari';
  if (ua.includes('Edge')) return 'Edge';
  return 'Other';
};

export const getCurrentUser = () => {
  // 현재 로그인한 사용자 정보 반환
  const token = localStorage.getItem('access_token');
  if (!token) return null;
  
  // JWT 토큰에서 사용자 정보 추출
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return {
      id: payload.sub,
      name: payload.name,
      email: payload.email
    };
  } catch {
    return null;
  }
};

export const getCurrentFilters = () => {
  // 현재 적용된 필터 정보 반환
  const urlParams = new URLSearchParams(window.location.search);
  return Object.fromEntries(urlParams);
};

export const getCurrentFormSection = () => {
  // 현재 수정 중인 폼 섹션 반환
  const activeTab = document.querySelector('.tab-content.active');
  return activeTab?.id || 'unknown_section';
};
```

### 3. React Hook 구현

#### 활동 로깅 Hook
```javascript
// hooks/useActivityLogger.js
import { useCallback } from 'react';
import { logActivity } from '../utils/activityLogger';

export const useActivityLogger = () => {
  const logMemberView = useCallback((memberId, memberName, accessedFields) => {
    logActivity({
      action: 'view',
      resource: 'member',
      target_id: memberId.toString(),
      target_name: memberName,
      page_path: window.location.pathname,
      page_name: '교인 상세조회',
      details: {
        accessed_fields: accessedFields,
        view_type: 'detail_modal',
        component: 'MemberDetailModal'
      },
      sensitive_data: accessedFields
    });
  }, []);
  
  const logMemberUpdate = useCallback((memberId, memberName, updatedFields, oldValues) => {
    logActivity({
      action: 'update',
      resource: 'member',
      target_id: memberId.toString(),
      target_name: memberName,
      page_path: window.location.pathname,
      page_name: '교인 정보 수정',
      details: {
        updated_fields: updatedFields,
        old_values: oldValues,
        component: 'MemberEditForm'
      },
      sensitive_data: updatedFields
    });
  }, []);
  
  const logMemberSearch = useCallback((searchTerm, resultCount) => {
    logActivity({
      action: 'search',
      resource: 'member',
      target_name: `검색: ${searchTerm}`,
      page_path: window.location.pathname,
      page_name: '교인 검색',
      details: {
        search_term: searchTerm,
        result_count: resultCount,
        component: 'MemberSearchForm'
      },
      sensitive_data: resultCount > 0 ? ['search_results'] : []
    });
  }, []);
  
  return {
    logMemberView,
    logMemberUpdate,
    logMemberSearch
  };
};
```

### 4. 컴포넌트 사용 예시

#### 교인 상세조회 컴포넌트
```javascript
// components/MemberDetailModal.jsx
import React, { useEffect } from 'react';
import { useActivityLogger } from '../hooks/useActivityLogger';

const MemberDetailModal = ({ memberId, member }) => {
  const { logMemberView } = useActivityLogger();
  
  useEffect(() => {
    if (member) {
      // 모달이 열릴 때 자동으로 활동 로깅
      const accessedFields = [
        'name', 'email', 'phone', 'address', 'birthdate',
        'position', 'department', 'baptism_date'
      ];
      
      logMemberView(memberId, member.name, accessedFields);
    }
  }, [member, memberId, logMemberView]);
  
  return (
    <div className="member-detail-modal">
      <h2>교인 상세 정보</h2>
      <div>이름: {member.name}</div>
      <div>이메일: {member.email}</div>
      <div>전화번호: {member.phone}</div>
      {/* ... 기타 정보 표시 */}
    </div>
  );
};
```

---

## 🏷️ 액션 및 리소스 타입 정의

### Action Types (필수)
| 액션 | 설명 | 사용 시점 |
|------|------|----------|
| `view` | 조회 | 교인 상세보기, 리스트 조회 |
| `create` | 생성 | 신규 교인 등록 |
| `update` | 수정 | 교인 정보 변경 |
| `delete` | 삭제 | 교인 삭제 |
| `search` | 검색 | 이름/전화번호 검색 |
| `login` | 로그인 | 사용자 로그인 |
| `logout` | 로그아웃 | 사용자 로그아웃 |

### Resource Types (필수)
| 리소스 | 설명 | 민감 정보 예시 |
|--------|------|---------------|
| `member` | 교인 정보 | name, email, phone, address, birthdate |
| `attendance` | 출석 정보 | member_id, attendance_date |
| `financial` | 재정 정보 | amount, donor_name |
| `bulletin` | 주보 정보 | - |
| `announcement` | 공지사항 | - |
| `system` | 시스템 | 로그인/로그아웃 |

---

## 🚨 주의사항 및 베스트 프랙티스

### 1. 필수 구현 사항
✅ **모든 개인정보 조회 시 로깅 필수**  
✅ **개인정보 수정 시 변경 전 값 보관**  
✅ **검색 시 검색어와 결과 수 기록**  
✅ **삭제 시 삭제 사유 기록**

### 2. 성능 최적화
✅ **배치 처리 사용** (10개씩 모아서 전송)  
✅ **비동기 처리** (UI 블로킹 방지)  
✅ **에러 무시** (로깅 실패가 메인 기능 방해 금지)  
✅ **재시도 로직** (최대 3회)

### 3. 보안 고려사항
⚠️ **IP 주소와 User-Agent는 서버에서 자동 설정**  
⚠️ **클라이언트에서 IP 정보 전송 금지**  
⚠️ **민감한 정보는 details가 아닌 sensitive_data 필드에 기록**  
⚠️ **사용자 ID는 문자열로 전송**

### 4. 에러 처리
```javascript
// 올바른 에러 처리 예시
const logActivity = async (data) => {
  try {
    await api.post('/auth/activity-logs', { logs: [data] });
  } catch (error) {
    // 로깅 실패는 콘솔에만 기록하고 사용자에게 표시하지 않음
    console.warn('활동 로그 저장 실패:', error);
    // 메인 기능은 계속 진행
  }
};
```

### 5. 테스트 가이드
```javascript
// 개발 환경에서 로깅 테스트
if (process.env.NODE_ENV === 'development') {
  // 로깅 활성화 상태 확인
  console.log('Activity Logging:', window.activityLogger ? 'Enabled' : 'Disabled');
  
  // 수동 로그 전송 테스트
  window.testActivityLog = () => {
    logActivity({
      action: 'view',
      resource: 'member',
      target_id: '999',
      target_name: '테스트 사용자',
      page_path: '/test',
      page_name: '테스트 페이지',
      sensitive_data: ['test_field']
    });
  };
}
```

---

## 📞 지원 및 문의

구현 중 문제가 발생하거나 추가 기능이 필요한 경우 백엔드팀에 문의해 주세요.

**백엔드 API 상태 확인:**
```bash
# 로깅 API 동작 확인
curl -X POST http://localhost:8000/api/v1/auth/activity-logs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"logs":[{"user_id":"123","action":"view","resource":"member","page_path":"/test","page_name":"테스트","sensitive_data":["test"]}]}'
```

**예상 응답:**
```json
{
  "success": true,
  "message": "활동 로그가 성공적으로 저장되었습니다",
  "inserted_count": 1,
  "timestamp": "2025-09-06T15:30:45.456Z"
}
```

---

## 🎯 구현 우선순위

### Phase 1 (1주일 내 필수)
1. ✅ 교인 상세조회 로깅
2. ✅ 교인 정보 수정 로깅  
3. ✅ 교인 검색 로깅
4. ✅ 공통 유틸리티 함수 구현

### Phase 2 (2주일 내 권장)
5. 📊 관리자 대시보드 연동
6. 📈 통계 화면 구현
7. 🔍 로그 조회 기능

### Phase 3 (향후 확장)
8. 📁 CSV 내보내기
9. 🔄 실시간 모니터링
10. 📧 보안 알림 기능

---

**🚀 이제 완전한 개인정보보호법/GDPR 준수 시스템을 프론트엔드에서 활용할 수 있습니다!**