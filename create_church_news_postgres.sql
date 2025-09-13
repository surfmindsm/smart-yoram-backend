-- church_news 테이블 생성 SQL (PostgreSQL/Supabase용)

-- Enum 타입 생성 (이미 존재할 수 있으므로 IF NOT EXISTS 사용)
DO $$ BEGIN
    CREATE TYPE newspriority AS ENUM ('urgent', 'important', 'normal');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE newsstatus AS ENUM ('active', 'completed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- church_news 테이블 생성
CREATE TABLE IF NOT EXISTS church_news (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    priority newspriority DEFAULT 'normal',
    
    -- 행사 정보
    event_date DATE,
    event_time TIME,
    location VARCHAR(255),
    organizer VARCHAR(100) NOT NULL,
    target_audience VARCHAR(100),
    participation_fee VARCHAR(50),
    
    -- 신청 관련
    registration_required BOOLEAN DEFAULT FALSE,
    registration_deadline DATE,
    
    -- 연락처 정보
    contact_person VARCHAR(100),
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),
    
    -- 상태 관리
    status newsstatus DEFAULT 'active',
    
    -- 메타데이터
    view_count INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    
    -- 태그 및 이미지 (JSON 배열)
    tags JSONB,
    images JSONB,
    
    -- 공통 필드
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 작성자 정보
    author_id INTEGER NOT NULL,
    church_id INTEGER
);

-- 외래키 제약조건 추가 (users 테이블이 있는 경우에만)
-- ALTER TABLE church_news ADD CONSTRAINT fk_church_news_author 
--   FOREIGN KEY (author_id) REFERENCES users(id);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS ix_church_news_id ON church_news(id);
CREATE INDEX IF NOT EXISTS ix_church_news_title ON church_news(title);
CREATE INDEX IF NOT EXISTS ix_church_news_category ON church_news(category);
CREATE INDEX IF NOT EXISTS ix_church_news_priority ON church_news(priority);
CREATE INDEX IF NOT EXISTS ix_church_news_status ON church_news(status);
CREATE INDEX IF NOT EXISTS ix_church_news_event_date ON church_news(event_date);
CREATE INDEX IF NOT EXISTS ix_church_news_created_at ON church_news(created_at);

-- updated_at 자동 업데이트 함수 및 트리거 생성
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성 (이미 존재할 수 있으므로 DROP 후 생성)
DROP TRIGGER IF EXISTS update_church_news_updated_at ON church_news;
CREATE TRIGGER update_church_news_updated_at 
    BEFORE UPDATE ON church_news 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- RLS (Row Level Security) 정책 설정 (Supabase용)
ALTER TABLE church_news ENABLE ROW LEVEL SECURITY;

-- 읽기 정책: 모든 인증된 사용자가 읽을 수 있음
CREATE POLICY "Anyone can view church news" ON church_news
  FOR SELECT USING (true);

-- 삽입 정책: 인증된 사용자만 생성 가능
CREATE POLICY "Authenticated users can insert church news" ON church_news
  FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- 업데이트 정책: 작성자만 수정 가능
CREATE POLICY "Users can update own church news" ON church_news
  FOR UPDATE USING (auth.uid()::text = author_id::text);

-- 삭제 정책: 작성자만 삭제 가능
CREATE POLICY "Users can delete own church news" ON church_news
  FOR DELETE USING (auth.uid()::text = author_id::text);