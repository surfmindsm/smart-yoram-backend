#!/usr/bin/env python3
"""
기존 교회들에 비서 에이전트를 추가하는 마이그레이션 스크립트

모든 기존 교회에 비서 에이전트가 없다면 자동으로 생성합니다.
"""
import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.church import Church
from app.models.ai_agent import AIAgent, OfficialAgentTemplate
from app.services.secretary_agent_service import secretary_agent_service

logger = logging.getLogger(__name__)


def migrate_existing_churches():
    """기존 교회들에 비서 에이전트 추가"""
    db = SessionLocal()
    
    try:
        print("🚀 기존 교회 비서 에이전트 마이그레이션 시작...")
        
        # 1. 비서 에이전트 템플릿 확인/생성
        template = secretary_agent_service.ensure_secretary_agent_template(db)
        print(f"✅ 비서 에이전트 템플릿 준비: {template.name} (ID: {template.id})")
        
        # 2. 모든 활성 교회 조회
        churches = db.query(Church).filter(
            Church.is_active == True
        ).all()
        
        print(f"📊 총 {len(churches)}개 교회 확인 중...")
        
        created_count = 0
        skipped_count = 0
        
        for church in churches:
            # 이미 비서 에이전트가 있는지 확인
            existing_secretary = db.query(AIAgent).filter(
                AIAgent.church_id == church.id,
                AIAgent.category == "secretary"
            ).first()
            
            if existing_secretary:
                print(f"⏭️  교회 {church.id} ({church.name}): 비서 에이전트 이미 존재 (ID: {existing_secretary.id})")
                skipped_count += 1
                continue
            
            # 비서 에이전트 생성
            try:
                secretary = secretary_agent_service.ensure_church_secretary_agent(
                    church.id, db
                )
                print(f"✅ 교회 {church.id} ({church.name}): 비서 에이전트 생성 완료 (ID: {secretary.id})")
                created_count += 1
                
            except Exception as e:
                print(f"❌ 교회 {church.id} ({church.name}): 비서 에이전트 생성 실패 - {e}")
                continue
        
        print(f"\n🎉 마이그레이션 완료!")
        print(f"📈 통계:")
        print(f"   - 총 교회 수: {len(churches)}")
        print(f"   - 새로 생성: {created_count}개")
        print(f"   - 이미 존재: {skipped_count}개")
        
        if created_count > 0:
            print(f"\n💡 {created_count}개 교회에 비서 에이전트가 새로 추가되었습니다!")
            
    except Exception as e:
        print(f"❌ 마이그레이션 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def verify_migration():
    """마이그레이션 결과 검증"""
    db = SessionLocal()
    
    try:
        print("\n🔍 마이그레이션 결과 검증 중...")
        
        # 전체 교회 수
        total_churches = db.query(Church).filter(Church.is_active == True).count()
        
        # 비서 에이전트가 있는 교회 수
        churches_with_secretary = db.query(Church).join(AIAgent).filter(
            Church.is_active == True,
            AIAgent.category == "secretary"
        ).count()
        
        print(f"📊 검증 결과:")
        print(f"   - 활성 교회 수: {total_churches}")
        print(f"   - 비서 에이전트 보유 교회: {churches_with_secretary}")
        print(f"   - 커버리지: {(churches_with_secretary/total_churches*100):.1f}%" if total_churches > 0 else "   - 커버리지: 0%")
        
        if churches_with_secretary == total_churches:
            print("✅ 모든 교회가 비서 에이전트를 보유하고 있습니다!")
        else:
            missing_count = total_churches - churches_with_secretary
            print(f"⚠️  {missing_count}개 교회가 비서 에이전트가 없습니다.")
            
            # 누락된 교회 목록 표시
            missing_churches = db.query(Church).filter(
                Church.is_active == True,
                ~Church.id.in_(
                    db.query(AIAgent.church_id).filter(AIAgent.category == "secretary")
                )
            ).all()
            
            print("📋 비서 에이전트가 없는 교회:")
            for church in missing_churches:
                print(f"   - 교회 {church.id}: {church.name}")
                
    except Exception as e:
        print(f"❌ 검증 중 오류 발생: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    # 마이그레이션 실행
    migrate_existing_churches()
    
    # 결과 검증
    verify_migration()
    
    print("\n🚀 마이그레이션 스크립트 완료!")