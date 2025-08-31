-- Church ID 9999의 실제 교인 데이터 기반 심방요청 목업 데이터 생성

-- 기존 심방요청 데이터 삭제 (church_id 9999)
DELETE FROM pastoral_care_requests WHERE church_id = 9999;

-- 실제 교인 데이터를 기반으로 심방요청 데이터 생성
INSERT INTO pastoral_care_requests (
    church_id, member_id, requester_name, requester_phone, request_type, 
    request_content, preferred_date, preferred_time_start, preferred_time_end,
    status, priority, scheduled_date, scheduled_time, completion_notes,
    admin_notes, address, is_urgent, created_at, updated_at
)
SELECT 
    9999 as church_id,
    m.user_id as member_id,  -- users 테이블의 id를 참조해야 함
    m.name as requester_name,
    m.phone as requester_phone,
    CASE (random() * 5)::integer
        WHEN 0 THEN '병문안'
        WHEN 1 THEN '새신자 심방'
        WHEN 2 THEN '정기 심방'
        WHEN 3 THEN '상담 심방'
        ELSE '일반 심방'
    END as request_type,
    CASE (random() * 8)::integer
        WHEN 0 THEN '몸이 아파서 목사님의 기도와 위로가 필요합니다.'
        WHEN 1 THEN '새롭게 교회에 나오게 되어 인사드리고 싶습니다.'
        WHEN 2 THEN '가정에 어려움이 있어 상담을 받고 싶습니다.'
        WHEN 3 THEN '신앙생활에 대해 궁금한 것이 있어 질문드리고 싶습니다.'
        WHEN 4 THEN '직장 문제로 인해 기도 부탁드립니다.'
        WHEN 5 THEN '자녀 교육 문제로 조언을 구하고 싶습니다.'
        WHEN 6 THEN '경제적 어려움이 있어 기도와 상담이 필요합니다.'
        ELSE '정기적인 심방을 통해 은혜를 나누고 싶습니다.'
    END as request_content,
    -- 선호 날짜 (앞으로 1-30일 사이)
    CURRENT_DATE + (random() * 30)::integer as preferred_date,
    -- 선호 시간 (오전 9시~오후 6시 사이)
    ('09:00:00'::time + (random() * interval '9 hours'))::time as preferred_time_start,
    ('10:00:00'::time + (random() * interval '9 hours'))::time as preferred_time_end,
    CASE (random() * 5)::integer
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'approved'
        WHEN 2 THEN 'scheduled'
        WHEN 3 THEN 'completed'
        ELSE 'pending'
    END as status,
    CASE (random() * 3)::integer
        WHEN 0 THEN 'normal'
        WHEN 1 THEN 'high'
        ELSE 'normal'
    END as priority,
    -- 예약 날짜 (상태가 scheduled나 completed인 경우)
    CASE 
        WHEN (random() * 5)::integer >= 2 THEN CURRENT_DATE + (random() * 20)::integer
        ELSE NULL
    END as scheduled_date,
    -- 예약 시간
    CASE 
        WHEN (random() * 5)::integer >= 2 THEN ('10:00:00'::time + (random() * interval '8 hours'))::time
        ELSE NULL
    END as scheduled_time,
    -- 완료 노트 (completed 상태인 경우)
    CASE 
        WHEN (random() * 5)::integer = 3 THEN '심방을 통해 많은 은혜를 나누었습니다. 지속적인 기도가 필요합니다.'
        ELSE NULL
    END as completion_notes,
    -- 관리자 노트
    CASE (random() * 3)::integer
        WHEN 0 THEN '목사님께서 직접 방문 예정'
        WHEN 1 THEN '구역장과 함께 심방 진행'
        ELSE NULL
    END as admin_notes,
    m.address as address,
    -- 긴급 여부 (10% 확률)
    CASE WHEN random() < 0.1 THEN true ELSE false END as is_urgent,
    -- 생성일 (최근 2개월 사이)
    NOW() - (random() * interval '60 days') as created_at,
    NOW() - (random() * interval '30 days') as updated_at
FROM members m
WHERE m.church_id = 9999 
    AND m.status = 'active'
    AND m.user_id IS NOT NULL  -- user_id가 있는 교인만
    AND random() < 0.6  -- 60% 확률로 심방요청 생성
ORDER BY random();

-- 결과 확인
SELECT 
    COUNT(*) as total_requests,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved,
    COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
    COUNT(CASE WHEN is_urgent = true THEN 1 END) as urgent_requests
FROM pastoral_care_requests 
WHERE church_id = 9999;

SELECT 
    request_type, 
    COUNT(*) as count 
FROM pastoral_care_requests 
WHERE church_id = 9999 
GROUP BY request_type 
ORDER BY count DESC;