# 👩‍💼 비서 AI 에이전트 프론트엔드 개발 가이드

## 📋 개요

기존 AI 에이전트 시스템에 **교회 업무 전용 비서 에이전트**가 추가되었습니다. 프론트엔드에서는 기존 Chat API를 그대로 사용하되, 비서 에이전트를 통해 실시간 교회 데이터 조회 기능을 제공할 수 있습니다.

## 🏗️ 시스템 구조

### 기존 vs 새로운 구조

**이전 (기존)**
```
교회당 AI 에이전트:
- 🤖 기본 에이전트 1개 (일반 대화)
```

**현재 (새로운)**
```
교회당 AI 에이전트:
- 🤖 기본 에이전트 1개 (일반 대화)
- 👩‍💼 비서 에이전트 1개 (업무 지원) ← 새로 추가!
```

## 🚀 프론트엔드 구현 가이드

### 1. AI 에이전트 목록 조회

**기존 API 그대로 사용:**
```http
GET /api/v1/agents/
```

**응답 변화:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "기본 AI",
      "category": "default",
      "description": "일반적인 대화를 위한 AI",
      "icon": "🤖",
      "is_default": true,
      "enable_church_data": false
    },
    {
      "id": 2,
      "name": "데모 교회 비서",
      "category": "secretary",
      "description": "교회 업무를 도와주는 스마트 비서",
      "icon": "👩‍💼",
      "is_default": false,
      "enable_church_data": true,
      "created_by_system": true
    }
  ]
}
```

### 2. UI 표시 방법

**React 컴포넌트 예시:**
```jsx
const AgentSelector = ({ agents, selectedAgent, onSelectAgent }) => {
  return (
    <div className="agent-list">
      {agents.map(agent => (
        <div 
          key={agent.id}
          className={`agent-card ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
          onClick={() => onSelectAgent(agent)}
        >
          <div className="agent-icon">{agent.icon}</div>
          <div className="agent-info">
            <h3>{agent.name}</h3>
            <p>{agent.description}</p>
            {agent.category === 'secretary' && (
              <span className="badge badge-special">실시간 데이터 조회</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
```

### 3. 채팅 메시지 전송

**기존 Chat API 그대로 사용:**
```http
POST /api/v1/chat/messages
```

**요청 예시:**
```json
{
  "agent_id": 2,  // 비서 에이전트 선택
  "content": "오늘 심방 일정 알려줘",
  "chat_history_id": null,
  "create_history_if_needed": true
}
```

**비서 에이전트 응답:**
```json
{
  "success": true,
  "message": "오늘 심방 일정을 알려드립니다.\n\n1. **14:00 - 박은미 성도댁**\n   - 위치: 서울시 강남구...\n   - 유형: 병원 심방 (높은 우선순위)\n...",
  "tokens_used": 245,
  "model": "gpt-4o-mini",
  "is_secretary_agent": true,
  "query_type": "pastoral_visit_schedule",
  "data_sources": ["pastoral_visits"],
  "message_id": 123
}
```

### 4. 비서 에이전트 응답 처리

**응답 구분 방법:**
```jsx
const ChatMessage = ({ message, isSecretary }) => {
  // 비서 에이전트 응답인지 확인
  const isSecretaryResponse = message.is_secretary_agent;
  
  return (
    <div className={`message ${isSecretaryResponse ? 'secretary-message' : 'default-message'}`}>
      {isSecretaryResponse && (
        <div className="message-header">
          <span className="secretary-badge">👩‍💼 비서 AI</span>
          <span className="query-type">{getQueryTypeLabel(message.query_type)}</span>
        </div>
      )}
      
      <div className="message-content">
        {formatMessageContent(message.message)}
      </div>
      
      {isSecretaryResponse && message.data_sources?.length > 0 && (
        <div className="data-sources">
          <small>📊 조회된 데이터: {message.data_sources.join(', ')}</small>
        </div>
      )}
    </div>
  );
};

const getQueryTypeLabel = (queryType) => {
  const labels = {
    'pastoral_visit_schedule': '심방 일정',
    'prayer_requests': '중보기도',
    'announcements': '공지사항',
    'visit_reports': '심방 보고서',
    'member_info': '성도 정보'
  };
  return labels[queryType] || '일반 업무';
};
```

## 💬 지원하는 질문 유형

### 심방 관련
```
✅ "오늘 심방 일정 알려줘"
✅ "내일 방문해야 할 곳 어디야?"
✅ "이번주 심방 예정은?"
✅ "긴급한 심방 요청 있나?"
```

### 기도 요청 관련
```
✅ "최근 기도제목 뭐가 있어?"
✅ "긴급 기도 요청 있나?"
✅ "이번주 중보기도 내용"
✅ "응답받은 기도제목 있어?"
```

### 공지사항 관련
```
✅ "새로운 공지사항 있어?"
✅ "이번주 중요한 안내사항"
✅ "최근 교회 소식 정리해줘"
✅ "고정된 공지 뭐가 있지?"
```

### 심방 보고서 관련
```
✅ "최근 심방 결과 어때?"
✅ "이번달 심방 보고서 요약"
✅ "심방 현황 알려줘"
✅ "어떤 곳들 방문했어?"
```

## 🎨 UI/UX 가이드

### 1. 에이전트 선택 화면
```
┌─────────────────────────────────────────┐
│  AI 에이전트 선택                       │
├─────────────────────────────────────────┤
│ 🤖 기본 AI                             │
│ 자유로운 대화와 일반적인 질문 답변       │
│                                         │
│ 👩‍💼 교회 비서 AI   [실시간 데이터 조회] │
│ 심방·기도·공지사항 등 교회 업무 지원    │
└─────────────────────────────────────────┘
```

### 2. 채팅 화면에서 구분
```
일반 에이전트 메시지:
┌─────────────────────────┐
│ 🤖 안녕하세요!          │
│ 무엇을 도와드릴까요?     │
└─────────────────────────┘

비서 에이전트 메시지:
┌─────────────────────────┐
│ 👩‍💼 비서 AI · 심방 일정  │
│ ─────────────────────   │
│ 오늘 심방 일정을...     │
│                         │
│ 📊 조회: pastoral_visits │
└─────────────────────────┘
```

### 3. 추천 질문 버튼

**비서 에이전트 선택 시 표시:**
```jsx
const SuggestedQuestions = ({ onQuestionClick }) => {
  const questions = [
    "오늘 심방 일정 알려줘",
    "새로운 기도 요청 있나?",
    "최근 공지사항 정리해줘",
    "이번주 심방 현황은?"
  ];
  
  return (
    <div className="suggested-questions">
      <p>💡 이런 질문을 해보세요:</p>
      {questions.map((question, index) => (
        <button 
          key={index}
          className="suggestion-btn"
          onClick={() => onQuestionClick(question)}
        >
          {question}
        </button>
      ))}
    </div>
  );
};
```

## 🔍 디버깅 및 개발 팁

### 1. 에이전트 타입 확인
```jsx
// 에이전트가 비서 에이전트인지 확인
const isSecretaryAgent = agent.category === 'secretary' && agent.enable_church_data;

// 응답이 데이터 기반인지 확인  
const isDataEnhanced = response.is_secretary_agent && response.data_sources?.length > 0;
```

### 2. 에러 처리
```jsx
const handleChatResponse = (response) => {
  if (!response.success) {
    // 에러 응답 처리
    showError(response.error || '응답을 생성할 수 없습니다.');
    return;
  }
  
  if (response.is_secretary_agent) {
    // 비서 에이전트 응답
    if (response.data_sources?.length === 0) {
      showWarning('관련 데이터를 찾을 수 없었습니다.');
    }
  }
  
  // 정상 메시지 표시
  addMessageToChat(response);
};
```

### 3. 로딩 상태 관리
```jsx
const [chatState, setChatState] = useState({
  isLoading: false,
  isSecretaryProcessing: false  // 비서 에이전트 데이터 조회 중
});

const sendMessage = async (content, agentId) => {
  const isSecretary = selectedAgent?.category === 'secretary';
  
  setChatState({
    isLoading: true,
    isSecretaryProcessing: isSecretary
  });
  
  // 비서 에이전트는 데이터 조회로 인해 더 오래 걸릴 수 있음
  const timeout = isSecretary ? 30000 : 10000;
  
  try {
    const response = await chatAPI.sendMessage(content, agentId, timeout);
    handleChatResponse(response);
  } catch (error) {
    handleError(error);
  } finally {
    setChatState({ isLoading: false, isSecretaryProcessing: false });
  }
};
```

## 📱 모바일 최적화

### 1. 에이전트 선택 (모바일)
```jsx
const MobileAgentSelector = () => (
  <div className="mobile-agent-tabs">
    <button className={`tab ${isDefault ? 'active' : ''}`}>
      🤖 일반 대화
    </button>
    <button className={`tab ${isSecretary ? 'active' : ''}`}>
      👩‍💼 업무 지원
    </button>
  </div>
);
```

### 2. 응답 메시지 (모바일)
```jsx
const MobileChatBubble = ({ message }) => (
  <div className="mobile-message">
    {message.is_secretary_agent && (
      <div className="message-tag">👩‍💼 비서</div>
    )}
    <div className="message-text">{message.content}</div>
    {message.data_sources?.length > 0 && (
      <div className="data-badge">📊 실시간 데이터</div>
    )}
  </div>
);
```

## 🛠️ 개발 체크리스트

### 필수 구현 사항
- [ ] AI 에이전트 목록에서 비서 에이전트 표시
- [ ] 비서 에이전트 선택 시 특별한 UI 표시
- [ ] 비서 응답 메시지에 메타데이터 표시
- [ ] 추천 질문 버튼 구현
- [ ] 에러 및 로딩 상태 처리

### 선택 구현 사항
- [ ] 비서 응답에 대한 특별한 스타일링
- [ ] 데이터 소스별 아이콘 표시
- [ ] 질문 유형별 색상 구분
- [ ] 비서 사용 통계 표시

### 테스트 시나리오
1. **에이전트 목록 로드 테스트**
   - 기본 + 비서 에이전트 2개가 표시되는지 확인
   
2. **비서 에이전트 대화 테스트**
   - "오늘 심방 일정 알려줘" 질문 시 구체적 답변 확인
   - `is_secretary_agent: true` 응답 확인
   - 데이터 소스 메타데이터 표시 확인

3. **일반 에이전트 대화 테스트**
   - 기존 대화 방식이 그대로 동작하는지 확인
   - `is_secretary_agent` 필드가 없거나 false인지 확인

## 💡 문제 해결

### Q: 비서 에이전트가 목록에 나타나지 않아요
A: `/api/v1/agents/` 호출 시 자동으로 생성됩니다. 한 번 호출해보세요.

### Q: 비서 에이전트 응답이 일반 응답과 같아요  
A: `agent.category === 'secretary'`이고 `enable_church_data === true`인지 확인하세요.

### Q: 데이터 조회가 너무 느려요
A: 비서 에이전트는 실시간 DB 조회를 하므로 일반 에이전트보다 2-3초 더 걸릴 수 있습니다.

### Q: 특정 질문에 대한 답변이 "관련 데이터 없음"이 나와요
A: 데모 데이터가 생성되었는지 확인하거나, 다른 시간 범위로 질문해보세요.

---

## 📞 연락처

**백엔드 개발팀**: backend@smartyoram.com  
**문서 버전**: 1.0.0  
**최종 업데이트**: 2024년 8월

---

이 가이드를 참고하여 비서 AI 에이전트를 프론트엔드에 성공적으로 통합해 보세요! 🚀