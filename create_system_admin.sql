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
    church_id, role, is_active, 
    created_at, updated_at
) VALUES (
    'superadmin', 'superadmin@smartyoram.com', '시스템 관리자',
    -- 비밀번호: admin123! (bcrypt 해시)
    '$2b$12$LQv3c1yqBwW0L/kDt.oeJ.vf9YH/Xd8.I7WxvUvxgj8xBxG8xR7G.',
    0, 'admin', true,
    NOW(), NOW()
) ON CONFLICT (username) DO NOTHING;

-- 계정 정보 확인
SELECT 
    u.id, u.username, u.email, u.full_name, u.church_id, u.role,
    c.name as church_name
FROM users u 
LEFT JOIN churches c ON u.church_id = c.id
WHERE u.church_id = 0;