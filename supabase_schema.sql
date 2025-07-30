-- Supabase database schema for Smart Yoram
-- Run this in the Supabase SQL editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create churches table
CREATE TABLE IF NOT EXISTS churches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(200),
    phone VARCHAR(20),
    email VARCHAR(100),
    pastor_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create members table
CREATE TABLE IF NOT EXISTS members (
    id SERIAL PRIMARY KEY,
    church_id INTEGER NOT NULL REFERENCES churches(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    birth_date DATE,
    gender VARCHAR(10),
    member_type VARCHAR(50) DEFAULT 'member',
    status VARCHAR(20) DEFAULT 'active',
    baptism_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for church_id
CREATE INDEX idx_members_church_id ON members(church_id);

-- Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    church_id INTEGER REFERENCES churches(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create attendances table
CREATE TABLE IF NOT EXISTS attendances (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    service_type VARCHAR(50) DEFAULT 'sunday',
    status VARCHAR(20) DEFAULT 'present',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(member_id, date, service_type)
);

-- Create index for attendance queries
CREATE INDEX idx_attendances_date ON attendances(date);
CREATE INDEX idx_attendances_member_id ON attendances(member_id);

-- Create bulletins table
CREATE TABLE IF NOT EXISTS bulletins (
    id SERIAL PRIMARY KEY,
    church_id INTEGER NOT NULL REFERENCES churches(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    date DATE NOT NULL,
    content TEXT,
    file_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for church_id
CREATE INDEX idx_bulletins_church_id ON bulletins(church_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply the trigger to all tables with updated_at
CREATE TRIGGER update_churches_updated_at BEFORE UPDATE ON churches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_members_updated_at BEFORE UPDATE ON members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bulletins_updated_at BEFORE UPDATE ON bulletins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default data
-- Create default church
INSERT INTO churches (name, address, phone, email, pastor_name)
VALUES ('Smart Yoram Church', '123 Main St, Seoul', '02-1234-5678', 'info@smartyoram.church', 'Pastor Kim')
ON CONFLICT DO NOTHING;

-- Create admin user (password: admin123)
INSERT INTO users (username, email, hashed_password, church_id, role)
VALUES (
    'admin',
    'admin@smartyoram.church',
    '$2b$12$LQQvLqYzTqCqUqLxQZGcOuEPvheOcJxPYwPyVUb5nTLzWgcIhxY/O',
    1,
    'admin'
)
ON CONFLICT (username) DO NOTHING;

-- Create sample members
INSERT INTO members (church_id, name, phone, email, gender, member_type, status)
VALUES 
    (1, '김철수', '010-1234-5678', 'chulsoo@example.com', 'male', 'member', 'active'),
    (1, '이영희', '010-2345-6789', 'younghee@example.com', 'female', 'member', 'active'),
    (1, '박민수', '010-3456-7890', 'minsoo@example.com', 'male', 'member', 'active'),
    (1, '정수진', '010-4567-8901', 'soojin@example.com', 'female', 'member', 'active')
ON CONFLICT DO NOTHING;

-- Grant permissions for the application
-- Note: In production, use Row Level Security (RLS) for better security
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Enable Row Level Security (optional but recommended)
-- ALTER TABLE churches ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE members ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE attendances ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE bulletins ENABLE ROW LEVEL SECURITY;