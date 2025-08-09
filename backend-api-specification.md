# Smart Yoram 백엔드 API 명세서

## 개요

Smart Yoram은 교회 관리를 위한 AI 에이전트 시스템입니다. 이 문서는 프론트엔드에서 필요로 하는 백엔드 API의 상세 명세를 제공합니다.

## 시스템 아키텍처

### 핵심 구성요소
1. **AI 에이전트 관리 시스템** - 교회별 맞춤 AI 에이전트 생성/관리
2. **채팅 시스템** - 실시간 AI 대화 및 히스토리 관리
3. **교회 데이터베이스 연동** - 각 교회의 내부 데이터 조회/분석
4. **GPT API 관리** - OpenAI API 키 관리 및 사용량 모니터링
5. **멀티 테넌트 지원** - 여러 교회를 위한 공식 에이전트 템플릿

## 데이터베이스 스키마

### 1. 교회 (Churches)
```sql
CREATE TABLE churches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    admin_user_id UUID REFERENCES users(id),
    gpt_api_key TEXT ENCRYPTED,
    subscription_plan VARCHAR(50) DEFAULT 'basic',
    max_agents INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2. AI 에이전트 (AI_Agents)
```sql
CREATE TABLE ai_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    church_id UUID REFERENCES churches(id),
    template_id UUID REFERENCES official_agent_templates(id) NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    detailed_description TEXT,
    icon VARCHAR(10) DEFAULT '🤖',
    system_prompt TEXT,
    is_active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3. 공식 에이전트 템플릿 (Official_Agent_Templates)
```sql
CREATE TABLE official_agent_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    detailed_description TEXT,
    icon VARCHAR(10) DEFAULT '🤖',
    system_prompt TEXT NOT NULL,
    is_public BOOLEAN DEFAULT true,
    version VARCHAR(20) DEFAULT '1.0.0',
    created_by VARCHAR(255) DEFAULT 'Smart Yoram Team',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 4. 채팅 히스토리 (Chat_Histories)
```sql
CREATE TABLE chat_histories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    church_id UUID REFERENCES churches(id),
    user_id UUID REFERENCES users(id),
    agent_id UUID REFERENCES ai_agents(id),
    title VARCHAR(255) NOT NULL,
    is_bookmarked BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 5. 채팅 메시지 (Chat_Messages)
```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_history_id UUID REFERENCES chat_histories(id),
    content TEXT NOT NULL,
    role VARCHAR(20) CHECK (role IN ('user', 'assistant')) NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6. 교회 데이터베이스 연동 설정 (Church_Database_Configs)
```sql
CREATE TABLE church_database_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    church_id UUID REFERENCES churches(id) UNIQUE,
    db_type VARCHAR(50), -- 'mysql', 'postgresql', 'mssql' 등
    host VARCHAR(255),
    port INTEGER,
    database_name VARCHAR(255),
    username VARCHAR(255),
    password TEXT ENCRYPTED,
    connection_string TEXT ENCRYPTED,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## API 엔드포인트

### 인증 & 교회 관리

#### POST /api/auth/login
관리자 로그인
```json
{
  "email": "admin@church.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "token": "jwt_token_here",
    "user": {
      "id": "uuid",
      "email": "admin@church.com",
      "church_id": "uuid",
      "church_name": "예시교회"
    }
  }
}
```

#### GET /api/church/profile
교회 정보 조회
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "예시교회",
    "subscriptionPlan": "premium",
    "maxAgents": 50,
    "currentAgentsCount": 12,
    "gptApiConfigured": true,
    "databaseConnected": true,
    "lastSync": "2025-08-08T10:30:00Z",
    "monthlyUsage": {
      "totalTokens": 28100,
      "totalRequests": 152,
      "totalCost": 14.05,
      "remainingQuota": 71900
    }
  }
}
```

#### PUT /api/church/gpt-config
GPT API 키 설정
```json
{
  "apiKey": "sk-...",
  "model": "gpt-4",
  "maxTokens": 4000,
  "temperature": 0.7
}
```

#### GET /api/church/system-status
시스템 상태 확인
```json
{
  "success": true,
  "data": {
    "gptApi": {
      "configured": true,
      "model": "gpt-4",
      "lastTest": "2025-08-08T10:30:00Z",
      "status": "active"
    },
    "database": {
      "connected": true,
      "lastSync": "2025-08-08T10:30:00Z",
      "tablesCount": 8,
      "status": "healthy"
    },
    "agents": {
      "total": 12,
      "active": 10,
      "totalTokensThisMonth": 28100,
      "totalCostThisMonth": 14.05
    }
  }
}
```

### AI 에이전트 관리

#### GET /api/agents
에이전트 목록 조회
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "id": "uuid",
        "name": "설교 도우미",
        "category": "설교 지원",
        "description": "설교 준비와 설교 연구를 도와드리는 전문 에이전트",
        "detailedDescription": "상세 설명...",
        "icon": "📖",
        "usage": 45,
        "isActive": true,
        "templates": ["uuid1", "uuid2"],
        "createdAt": "2025-08-08T10:30:00Z",
        "updatedAt": "2025-08-08T15:22:00Z",
        "totalTokensUsed": 12500,
        "totalCost": 6.25,
        "systemPrompt": "당신은 설교 준비를 전문적으로 도와주는 AI입니다...",
        "templateId": "official-template-1",
        "version": "1.0.0"
      }
    ],
    "stats": {
      "total_agents": 12,
      "active_agents": 10,
      "inactive_agents": 2,
      "total_usage": 156
    }
  }
}
```

#### POST /api/agents
새 에이전트 생성
```json
{
  "name": "새 에이전트",
  "category": "목양 관리",
  "description": "간단 설명",
  "detailedDescription": "상세 설명",
  "icon": "❤️",
  "systemPrompt": "당신은 목양을 위한 전문 상담사입니다...",
  "isActive": true,
  "templateId": "uuid" // 공식 템플릿 기반 생성 시
}
```

#### PUT /api/agents/{agentId}
에이전트 수정
```json
{
  "name": "수정된 이름",
  "description": "수정된 설명",
  "isActive": false
}
```

#### DELETE /api/agents/{agentId}
에이전트 삭제

#### GET /api/agents/templates/official
공식 에이전트 템플릿 목록
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "설교 준비 도우미",
      "category": "설교 지원",
      "description": "성경 해석, 설교문 작성, 적용점 개발을 도와주는 전문 AI",
      "detailedDescription": "설교 준비의 전 과정을 체계적으로 지원하는 전문 AI 에이전트입니다...",
      "icon": "📖",
      "systemPrompt": "당신은 설교 준비를 전문적으로 도와주는 AI입니다...",
      "isOfficial": true,
      "version": "2.1.0",
      "createdBy": "Smart Yoram Team",
      "createdAt": "2025-07-01T10:00:00Z"
    },
    {
      "id": "uuid2",
      "name": "목양 및 심방 도우미",
      "category": "목양 관리",
      "description": "성도 상담, 심방 계획, 목양 지도를 도와주는 전문 AI",
      "detailedDescription": "목양과 심방의 모든 단계를 전문적으로 지원하는 AI 에이전트입니다...",
      "icon": "❤️",
      "systemPrompt": "당신은 목양과 심방을 전문적으로 도와주는 AI입니다...",
      "isOfficial": true,
      "version": "1.8.0",
      "createdBy": "Smart Yoram Team",
      "createdAt": "2025-06-15T10:00:00Z"
    }
  ]
}
```

### 채팅 시스템

#### GET /api/chat/histories
채팅 히스토리 목록
**Query Parameters:**
- `include_messages` (optional): true인 경우 각 히스토리의 최근 메시지들도 포함

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "최근 4주 연속 주일예배...",
      "agentName": "설교 도우미",
      "isBookmarked": true,
      "messageCount": 8,
      "timestamp": "2025-08-08T10:30:00Z",
      "messages": [  // include_messages=true일 때만
        {
          "id": "uuid",
          "content": "마지막 메시지 내용",
          "role": "assistant",
          "tokensUsed": 25,
          "timestamp": "2025-08-08T10:30:00Z"
        }
      ]
    }
  ]
}
```

#### POST /api/chat/histories
새 채팅 시작
```json
{
  "agent_id": "uuid",
  "title": "새 대화"
}
```

#### GET /api/chat/histories/{historyId}/messages
특정 채팅의 메시지 목록
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "content": "안녕하세요",
      "role": "user",
      "tokensUsed": 0,
      "timestamp": "2025-08-08T10:30:00Z"
    },
    {
      "id": "uuid",
      "content": "안녕하세요! 어떻게 도와드릴까요?",
      "role": "assistant", 
      "tokensUsed": 25,
      "timestamp": "2025-08-08T10:30:05Z"
    }
  ]
}
```

#### POST /api/chat/messages
메시지 전송 및 AI 응답 생성
```json
{
  "chat_history_id": "uuid",
  "agent_id": "uuid",
  "content": "이번 주 결석자 현황을 알려주세요"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_message": {
      "id": "uuid",
      "content": "이번 주 결석자 현황을 알려주세요",
      "role": "user",
      "timestamp": "2025-08-08T10:30:00Z"
    },
    "ai_response": {
      "id": "uuid", 
      "content": "이번 주 결석자는 총 5명입니다...",
      "role": "assistant",
      "tokensUsed": 150,
      "dataSources": ["church_members", "attendance_records"],
      "timestamp": "2025-08-08T10:30:05Z"
    }
  }
}
```

#### PUT /api/chat/histories/{historyId}
채팅 제목 수정 또는 북마크 토글
```json
{
  "title": "새로운 제목",
  "isBookmarked": true
}
```

#### DELETE /api/chat/histories/{historyId}
채팅 히스토리 삭제

### 교회 데이터베이스 연동

#### POST /api/church/database/config
교회 데이터베이스 연결 설정
```json
{
  "db_type": "mysql",
  "host": "localhost",
  "port": 3306,
  "database_name": "church_db",
  "username": "admin",
  "password": "password123"
}
```

#### GET /api/church/database/test-connection
데이터베이스 연결 테스트
```json
{
  "success": true,
  "data": {
    "connected": true,
    "tables_found": ["members", "attendance", "donations", "events"],
    "last_sync": "2025-08-08T10:30:00Z"
  }
}
```

#### POST /api/church/database/query
AI가 교회 데이터를 조회할 때 사용 (내부 API)
```json
{
  "query_type": "members_absent",
  "parameters": {
    "weeks": 4,
    "service_type": "sunday"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "query_result": [
      {
        "member_id": "12345",
        "name": "김철수",
        "phone": "010-1234-5678",
        "last_attendance": "2025-07-15",
        "weeks_absent": 4
      }
    ],
    "summary": "4주 연속 결석자 5명 발견"
  }
}
```

### 사용량 및 통계

#### GET /api/analytics/usage
GPT API 사용량 통계
```json
{
  "success": true,
  "data": {
    "current_month": {
      "total_tokens": 50000,
      "total_requests": 200,
      "cost_usd": 25.50
    },
    "daily_usage": [
      {
        "date": "2025-08-08",
        "tokens": 2500,
        "requests": 15,
        "cost": 1.25
      }
    ],
    "agent_usage": [
      {
        "agent_id": "uuid",
        "agent_name": "설교 도우미",
        "tokens": 15000,
        "requests": 75
      }
    ]
  }
}
```

## AI 응답 생성 로직

### 1. 컨텍스트 구성
```python
def build_context(agent_id, user_message, church_id):
    agent = get_agent(agent_id)
    church_data = get_relevant_church_data(user_message, church_id)
    
    context = {
        "system_prompt": agent.system_prompt,
        "church_context": church_data,
        "conversation_history": get_recent_messages(chat_history_id, limit=10)
    }
    return context
```

### 2. 교회 데이터 조회
AI가 필요시 교회 데이터베이스에서 관련 정보를 자동으로 조회:

- **출석 현황**: "결석자", "출석률" 키워드 감지
- **성도 정보**: "성도", "회원", "연락처" 키워드 감지  
- **헌금 현황**: "헌금", "십일조", "재정" 키워드 감지
- **행사 일정**: "행사", "예배", "모임" 키워드 감지

### 3. 응답 생성 플로우
```python
async def generate_ai_response(user_message, agent_id, church_id):
    # 1. 메시지 분석 및 필요한 데이터 확인
    required_data = analyze_message_intent(user_message)
    
    # 2. 교회 데이터베이스에서 관련 정보 조회
    church_data = {}
    if required_data:
        church_data = query_church_database(required_data, church_id)
    
    # 3. 컨텍스트 구성
    context = build_context(agent_id, user_message, church_id, church_data)
    
    # 4. GPT API 호출
    response = await call_gpt_api(context)
    
    # 5. 사용량 기록
    record_usage(church_id, agent_id, response.tokens_used)
    
    return response
```

## 보안 고려사항

### 1. 데이터 암호화
- GPT API 키: AES-256 암호화 저장
- 데이터베이스 연결 정보: 암호화 저장
- 민감한 교회 데이터: 전송 시 TLS 1.3 사용

### 2. 접근 제어
- JWT 토큰 기반 인증
- 교회별 데이터 격리 (Row Level Security)
- API 레이트 리미팅

### 3. 데이터 프라이버시
- 교회 데이터는 해당 교회에서만 접근 가능
- GPT API 전송 데이터 로깅 최소화
- 개인정보 마스킹 처리

## 배포 및 환경 설정

### 환경 변수
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/smart_yoram
JWT_SECRET=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key
OPENAI_API_KEY=fallback_api_key
REDIS_URL=redis://localhost:6379
LOG_LEVEL=info
```

### Docker 컨테이너 구성
- **Backend API**: Node.js/Express 또는 Python/FastAPI
- **Database**: PostgreSQL 14+
- **Cache**: Redis 7+
- **File Storage**: AWS S3 또는 호환 스토리지

## 에러 처리

### 표준 에러 응답 형식
```json
{
  "success": false,
  "error": {
    "code": "INVALID_API_KEY",
    "message": "GPT API 키가 유효하지 않습니다.",
    "details": "OpenAI API returned 401 Unauthorized"
  }
}
```

### 주요 에러 코드
- `INVALID_API_KEY`: GPT API 키 오류
- `DATABASE_CONNECTION_FAILED`: 교회 DB 연결 실패
- `QUOTA_EXCEEDED`: API 사용량 한도 초과
- `AGENT_NOT_FOUND`: 존재하지 않는 에이전트
- `UNAUTHORIZED`: 인증 실패
- `FORBIDDEN`: 권한 없음

## 확장성 고려사항

### 1. 멀티 테넌시
- 교회별 독립적인 데이터 격리
- 교회별 커스텀 도메인 지원 가능

### 2. 스케일링
- 수평적 확장을 위한 스테이트리스 API 설계
- 데이터베이스 읽기 복제본 활용
- CDN을 통한 정적 리소스 제공

### 3. 모니터링
- API 응답 시간 모니터링
- GPT API 사용량 알림
- 에러율 추적 및 알림

이 명세서를 바탕으로 백엔드 개발을 진행하시면, 프론트엔드와 완벽하게 연동되는 시스템을 구축할 수 있습니다.
