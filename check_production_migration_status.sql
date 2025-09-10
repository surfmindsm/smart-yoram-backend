-- 운영 서버 마이그레이션 상태 확인 SQL
-- 현재 적용된 마이그레이션 버전 확인
SELECT version_num FROM alembic_version;

-- 커뮤니티 테이블들 존재 여부 확인
SELECT 
    table_name,
    CASE 
        WHEN table_name IN (
            'community_sharing', 
            'community_requests', 
            'job_posts', 
            'job_seekers', 
            'music_requests', 
            'event_announcements'
        ) THEN '✅ 커뮤니티 테이블'
        ELSE '❌ 일반 테이블'
    END as table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name IN (
        'community_sharing', 
        'community_requests', 
        'job_posts', 
        'job_seekers', 
        'music_requests', 
        'event_announcements',
        'ai_agents',
        'sermon_materials'
    )
ORDER BY table_name;

-- ai_agents 테이블의 컬럼 확인 (secretary_agent_001 마이그레이션 적용 여부)
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'ai_agents' 
    AND column_name IN ('is_default', 'enable_church_data', 'created_by_system', 'gpt_model', 'max_tokens', 'temperature')
ORDER BY column_name;