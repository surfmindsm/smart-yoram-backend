-- Create system_announcements table
CREATE TABLE system_announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    priority VARCHAR(50) NOT NULL DEFAULT 'normal',
    start_date DATE NOT NULL,
    end_date DATE,
    target_churches TEXT,
    is_active BOOLEAN DEFAULT 1,
    is_pinned BOOLEAN DEFAULT 0,
    created_by INTEGER NOT NULL,
    author_name VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users (id),
    CHECK (priority IN ('urgent', 'important', 'normal'))
);

-- Create system_announcement_reads table
CREATE TABLE system_announcement_reads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_announcement_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    church_id INTEGER NOT NULL,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (system_announcement_id) REFERENCES system_announcements (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (church_id) REFERENCES churches (id) ON DELETE CASCADE,
    UNIQUE (system_announcement_id, user_id, church_id)
);

-- Create indexes
CREATE INDEX ix_system_announcements_start_date ON system_announcements (start_date);
CREATE INDEX ix_system_announcements_priority ON system_announcements (priority);
CREATE INDEX ix_system_announcements_is_active ON system_announcements (is_active);
CREATE INDEX ix_system_announcement_reads_user ON system_announcement_reads (user_id);
CREATE INDEX ix_system_announcement_reads_church ON system_announcement_reads (church_id);