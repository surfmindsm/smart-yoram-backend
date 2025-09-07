-- 프로덕션 PostgreSQL용 login_history 테이블 생성 스크립트
-- 프로덕션 데이터베이스에서 직접 실행하세요

-- 1. 테이블 존재 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'login_history';

-- 2. 테이블이 없다면 생성
CREATE TABLE IF NOT EXISTS login_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    device_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 3. 인덱스 생성 (성능 향상용)
CREATE INDEX IF NOT EXISTS ix_login_history_user_id ON login_history(user_id);
CREATE INDEX IF NOT EXISTS ix_login_history_timestamp ON login_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS ix_login_history_user_timestamp ON login_history(user_id, timestamp DESC);

-- 4. 테이블 생성 확인
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'login_history'
ORDER BY ordinal_position;

-- 완료 메시지
SELECT '✅ login_history 테이블 생성 완료!' as result;