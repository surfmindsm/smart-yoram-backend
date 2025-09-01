-- 시스템 관리자 계정 생성 (church_id = 0)

-- 1. 시스템 교회 생성 (church_id = 0)
INSERT INTO churches (
    id, name, address, phone, email, 
    pastor_name, business_no,
    subscription_status, subscription_plan, member_limit,
    gpt_model, max_tokens, temperature,
    max_agents, monthly_token_limit,
    is_active, created_at, updated_at
) VALUES (
    0, 'Smart Yoram System', 'System Admin Office', '000-0000-0000', 
    'superadmin@smartyoram.com',
    'System Administrator', '000-00-00000',
    'active', 'enterprise', 999999,
    'gpt-4o-mini', 4000, 0.7,
    999999, 999999999,
    true, NOW(), NOW()
) ON CONFLICT (id) DO NOTHING;

-- 2. 시스템 관리자 사용자 계정 생성
INSERT INTO users (
    username, email, full_name, hashed_password, 
    church_id, role, is_active, is_superuser,
    created_at, updated_at, is_first
) VALUES (
    'system_superadmin', 'system@smartyoram.com', '시스템 최고관리자',
    -- 비밀번호: admin123! (bcrypt 해시)
    '$2b$12$LQv3c1yqBwW0L/kDt.oeJ.vf9YH/Xd8.I7WxvUvxgj8xBxG8xR7G.',
    0, 'system_admin', true, true,
    NOW(), NOW(), true
) ON CONFLICT (username) DO NOTHING;

-- 3. 기존 SYS001 멤버가 있는지 확인 후 업데이트 또는 생성
DO $$
BEGIN
    -- 기존 SYS001 멤버가 있으면 업데이트
    IF EXISTS (SELECT 1 FROM members WHERE code = 'SYS001') THEN
        UPDATE members 
        SET user_id = (SELECT id FROM users WHERE username = 'system_superadmin'),
            name = '시스템 최고관리자',
            email = 'system@smartyoram.com',
            position = 'system_admin',
            church_id = 0,
            updated_at = NOW()
        WHERE code = 'SYS001';
    ELSE
        -- 없으면 새로 생성
        INSERT INTO members (
            church_id, user_id, code, name, 
            phone, email, position, 
            member_status, status, 
            created_at, updated_at
        ) VALUES (
            0, 
            (SELECT id FROM users WHERE username = 'system_superadmin'),
            'SYS001', '시스템 최고관리자',
            '000-0000-0000', 'system@smartyoram.com', 'system_admin',
            'active', 'active',
            NOW(), NOW()
        );
    END IF;
END $$;

-- 계정 정보 확인
SELECT 
    u.id, u.username, u.email, u.full_name, u.church_id, u.role,
    c.name as church_name
FROM users u 
LEFT JOIN churches c ON u.church_id = c.id
WHERE u.church_id = 0;