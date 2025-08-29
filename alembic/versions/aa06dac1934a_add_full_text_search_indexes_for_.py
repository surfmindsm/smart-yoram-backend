"""Add full-text search indexes for content search

Revision ID: aa06dac1934a
Revises: fef6cceb4de2
Create Date: 2025-08-30 00:57:48.372525

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa06dac1934a'
down_revision: Union[str, None] = 'fef6cceb4de2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create full-text search indexes using PostgreSQL's tsvector and GIN indexes
    # These support Korean text search with proper tokenization
    
    # Announcements full-text search (title + content combined)
    op.execute("""
        CREATE INDEX idx_announcements_fts 
        ON announcements 
        USING GIN (to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(content, '')))
    """)
    
    # Prayer requests full-text search
    op.execute("""
        CREATE INDEX idx_prayer_requests_fts 
        ON prayer_requests 
        USING GIN (to_tsvector('english', COALESCE(prayer_content, '')))
    """)
    
    # Pastoral care requests full-text search  
    op.execute("""
        CREATE INDEX idx_pastoral_care_requests_fts 
        ON pastoral_care_requests 
        USING GIN (to_tsvector('english', COALESCE(request_content, '')))
    """)
    
    # Members name search (supports partial matching)
    op.execute("""
        CREATE INDEX idx_members_name_fts 
        ON members 
        USING GIN (to_tsvector('english', COALESCE(name, '') || ' ' || COALESCE(name_eng, '')))
    """)
    
    # Add trigram indexes for better partial matching (requires pg_trgm extension)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    
    # Trigram indexes for fuzzy search
    op.execute("""
        CREATE INDEX idx_announcements_title_trgm 
        ON announcements 
        USING GIN (title gin_trgm_ops)
    """)
    
    op.execute("""
        CREATE INDEX idx_members_name_trgm 
        ON members 
        USING GIN (name gin_trgm_ops)
    """)


def downgrade() -> None:
    # Drop trigram indexes
    op.drop_index('idx_members_name_trgm')
    op.drop_index('idx_announcements_title_trgm')
    
    # Drop full-text search indexes
    op.drop_index('idx_members_name_fts')
    op.drop_index('idx_pastoral_care_requests_fts')  
    op.drop_index('idx_prayer_requests_fts')
    op.drop_index('idx_announcements_fts')