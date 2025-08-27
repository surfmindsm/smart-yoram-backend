"""Add constraints to prevent secretary agent deletion

Revision ID: secretary_constraints_001
Revises: secretary_agent_001
Create Date: 2024-08-27 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'secretary_constraints_001'
down_revision = 'secretary_agent_001'
depends_on = None


def upgrade() -> None:
    """Add database constraints to prevent secretary agent deletion."""
    
    # PostgreSQL/Supabase용 트리거 함수 생성
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_secretary_agent_deletion()
        RETURNS TRIGGER AS $$
        BEGIN
            -- 비서 에이전트이고 시스템에서 생성한 경우 삭제 방지
            IF OLD.category = 'secretary' AND OLD.created_by_system = true THEN
                RAISE EXCEPTION '시스템이 생성한 비서 에이전트는 삭제할 수 없습니다. (Agent ID: %)', OLD.id;
            END IF;
            RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # 삭제 방지 트리거 생성
    op.execute("""
        CREATE TRIGGER prevent_secretary_deletion
            BEFORE DELETE ON ai_agents
            FOR EACH ROW
            EXECUTE FUNCTION prevent_secretary_agent_deletion();
    """)
    
    # 업데이트 시에도 중요 필드 변경 방지
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_secretary_agent_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            -- 비서 에이전트의 중요 필드 변경 방지
            IF OLD.category = 'secretary' AND OLD.created_by_system = true THEN
                -- category 변경 방지
                IF NEW.category != OLD.category THEN
                    RAISE EXCEPTION '비서 에이전트의 카테고리는 변경할 수 없습니다. (Agent ID: %)', OLD.id;
                END IF;
                
                -- created_by_system 변경 방지
                IF NEW.created_by_system != OLD.created_by_system THEN
                    RAISE EXCEPTION '비서 에이전트의 시스템 생성 플래그는 변경할 수 없습니다. (Agent ID: %)', OLD.id;
                END IF;
                
                -- is_active를 false로 변경 방지 (비활성화 방지)
                IF NEW.is_active = false AND OLD.is_active = true THEN
                    RAISE EXCEPTION '시스템 비서 에이전트는 비활성화할 수 없습니다. (Agent ID: %)', OLD.id;
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # 수정 방지 트리거 생성
    op.execute("""
        CREATE TRIGGER prevent_secretary_modification
            BEFORE UPDATE ON ai_agents
            FOR EACH ROW
            EXECUTE FUNCTION prevent_secretary_agent_modification();
    """)
    
    # 인덱스 추가 (성능 최적화)
    op.create_index(
        'idx_ai_agents_category', 
        'ai_agents', 
        ['category'], 
        if_not_exists=True
    )
    
    op.create_index(
        'idx_ai_agents_church_created_by_system', 
        'ai_agents', 
        ['church_id', 'created_by_system'], 
        if_not_exists=True
    )


def downgrade() -> None:
    """Remove secretary agent protection constraints."""
    
    # 트리거 삭제
    op.execute("DROP TRIGGER IF EXISTS prevent_secretary_modification ON ai_agents;")
    op.execute("DROP TRIGGER IF EXISTS prevent_secretary_deletion ON ai_agents;")
    
    # 함수 삭제
    op.execute("DROP FUNCTION IF EXISTS prevent_secretary_agent_modification();")
    op.execute("DROP FUNCTION IF EXISTS prevent_secretary_agent_deletion();")
    
    # 인덱스 삭제
    op.drop_index('idx_ai_agents_church_created_by_system', 'ai_agents', if_exists=True)
    op.drop_index('idx_ai_agents_category', 'ai_agents', if_exists=True)