-- Church ID 9999의 실제 교인 데이터 기반 헌금 목업 데이터 생성

-- 기존 헌금 데이터 삭제 (church_id 9999)
DELETE FROM offerings WHERE church_id = 9999;

-- 실제 교인 데이터를 기반으로 헌금 데이터 생성
-- 각 교인마다 3-6건의 헌금 기록 생성 (최근 6개월)
INSERT INTO offerings (
    church_id, member_id, offered_on, fund_type, amount, 
    note, input_user_id, created_at, updated_at
)
SELECT 
    9999 as church_id,
    m.id as member_id,
    -- 헌금일 (최근 6개월 사이 랜덤)
    CURRENT_DATE - (random() * 180)::integer as offered_on,
    -- 헌금 유형
    CASE (random() * 6)::integer
        WHEN 0 THEN '십일조'
        WHEN 1 THEN '감사헌금'
        WHEN 2 THEN '특별헌금' 
        WHEN 3 THEN '선교헌금'
        WHEN 4 THEN '건축헌금'
        ELSE '주일헌금'
    END as fund_type,
    -- 헌금액 (fund_type별 차등)
    CASE 
        WHEN (random() * 6)::integer = 0 THEN -- 십일조 (20-80만원)
            (200000 + random() * 600000)::numeric(15,2)
        WHEN (random() * 6)::integer = 1 THEN -- 감사헌금 (5-30만원)
            (50000 + random() * 250000)::numeric(15,2)
        WHEN (random() * 6)::integer = 2 THEN -- 특별헌금 (10-50만원)
            (100000 + random() * 400000)::numeric(15,2)
        WHEN (random() * 6)::integer = 3 THEN -- 선교헌금 (5-20만원)
            (50000 + random() * 150000)::numeric(15,2)
        WHEN (random() * 6)::integer = 4 THEN -- 건축헌금 (10-100만원)
            (100000 + random() * 900000)::numeric(15,2)
        ELSE -- 주일헌금 (1-10만원)
            (10000 + random() * 90000)::numeric(15,2)
    END as amount,
    -- 비고
    CASE (random() * 6)::integer
        WHEN 0 THEN '정기 십일조 헌금입니다.'
        WHEN 1 THEN '하나님의 은혜에 감사드리며 드립니다.'
        WHEN 2 THEN '교회 발전을 위해 기쁜 마음으로 드립니다.'
        WHEN 3 THEN '해외 선교 사역을 위해 드립니다.'
        WHEN 4 THEN '새 성전 건축을 위해 드립니다.'
        ELSE '주일 예배 헌금입니다.'
    END as note,
    -- input_user_id (첫 번째 활성 교인의 user_id 사용)
    (SELECT user_id FROM members WHERE church_id = 9999 AND status = 'active' AND user_id IS NOT NULL LIMIT 1) as input_user_id,
    -- 생성일 (헌금일과 비슷한 시기)
    CURRENT_DATE - (random() * 180)::integer + (random() * interval '7 days') as created_at,
    CURRENT_DATE - (random() * 90)::integer + (random() * interval '3 days') as updated_at
FROM members m
CROSS JOIN generate_series(1, 4) as series -- 각 교인마다 평균 4건 생성
WHERE m.church_id = 9999 
    AND m.status = 'active'
    AND random() < 0.8  -- 80% 확률로 헌금 기록 생성
ORDER BY random();

-- 정기 십일조 추가 생성 (일부 교인들의 월별 십일조)
INSERT INTO offerings (
    church_id, member_id, offered_on, fund_type, amount, 
    note, input_user_id, created_at, updated_at
)
SELECT 
    9999 as church_id,
    m.id as member_id,
    -- 매월 첫 주 일요일에 십일조
    DATE_TRUNC('month', CURRENT_DATE - (month_offset * interval '1 month')) + 
    (EXTRACT(dow FROM DATE_TRUNC('month', CURRENT_DATE - (month_offset * interval '1 month'))) * interval '-1 day') +
    interval '7 days' as offered_on,
    '십일조' as fund_type,
    -- 정기 십일조는 비교적 일정한 금액 (교인별로 고정)
    (200000 + (m.id % 10) * 50000 + random() * 100000)::numeric(15,2) as amount,
    '정기 월 십일조' as note,
    (SELECT user_id FROM members WHERE church_id = 9999 AND status = 'active' AND user_id IS NOT NULL LIMIT 1) as input_user_id,
    DATE_TRUNC('month', CURRENT_DATE - (month_offset * interval '1 month')) + 
    interval '1 week' + (random() * interval '2 days') as created_at,
    CURRENT_DATE - (random() * 30)::integer as updated_at
FROM members m
CROSS JOIN generate_series(0, 5) as month_offset -- 최근 6개월
WHERE m.church_id = 9999 
    AND m.status = 'active'
    AND m.id % 3 = 0  -- 3명 중 1명만 정기 십일조 참여
    AND random() < 0.9  -- 90% 확률로 매월 십일조
ORDER BY offered_on DESC;

-- 특별 절기 헌금 추가 (추수감사절, 성탄절, 부활절 등)
INSERT INTO offerings (
    church_id, member_id, offered_on, fund_type, amount, 
    note, input_user_id, created_at, updated_at
)
SELECT 
    9999 as church_id,
    m.id as member_id,
    -- 특별 절기 날짜들
    CASE holiday_type
        WHEN 1 THEN '2024-11-24'::date  -- 추수감사절
        WHEN 2 THEN '2024-12-25'::date  -- 성탄절
        WHEN 3 THEN '2024-03-31'::date  -- 부활절 (2024년)
        ELSE '2024-01-01'::date         -- 신년
    END as offered_on,
    CASE holiday_type
        WHEN 1 THEN '추수감사절헌금'
        WHEN 2 THEN '성탄절헌금'  
        WHEN 3 THEN '부활절헌금'
        ELSE '신년헌금'
    END as fund_type,
    -- 절기 헌금은 평소보다 많이 (10-100만원)
    (100000 + random() * 900000)::numeric(15,2) as amount,
    CASE holiday_type
        WHEN 1 THEN '한 해 동안 베풀어주신 은혜에 감사드립니다.'
        WHEN 2 THEN '구세주 탄생을 기념하며 감사한 마음으로 드립니다.'
        WHEN 3 THEN '부활의 은혜를 기억하며 감사함으로 드립니다.'
        ELSE '새해를 맞아 새로운 결단으로 드립니다.'
    END as note,
    (SELECT user_id FROM members WHERE church_id = 9999 AND status = 'active' AND user_id IS NOT NULL LIMIT 1) as input_user_id,
    CASE holiday_type
        WHEN 1 THEN '2024-11-24'::timestamp + (random() * interval '3 days')
        WHEN 2 THEN '2024-12-25'::timestamp + (random() * interval '3 days')
        WHEN 3 THEN '2024-03-31'::timestamp + (random() * interval '3 days')
        ELSE '2024-01-01'::timestamp + (random() * interval '3 days')
    END as created_at,
    CURRENT_DATE - (random() * 30)::integer as updated_at
FROM members m
CROSS JOIN generate_series(1, 4) as holiday_type
WHERE m.church_id = 9999 
    AND m.status = 'active'
    AND random() < 0.4  -- 40% 확률로 절기 헌금 참여
ORDER BY offered_on;

-- 결과 확인 쿼리
SELECT 
    COUNT(*) as total_offerings,
    COUNT(DISTINCT member_id) as unique_members,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount
FROM offerings 
WHERE church_id = 9999;

SELECT 
    fund_type, 
    COUNT(*) as count,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount
FROM offerings 
WHERE church_id = 9999 
GROUP BY fund_type 
ORDER BY total_amount DESC;

SELECT 
    DATE_TRUNC('month', offered_on) as month,
    COUNT(*) as offerings_count,
    SUM(amount) as total_amount
FROM offerings 
WHERE church_id = 9999 
GROUP BY DATE_TRUNC('month', offered_on)
ORDER BY month DESC
LIMIT 12;