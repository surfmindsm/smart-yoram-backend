"""
교번 자동생성 서비스
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.models.member import Member


class MemberNumberService:
    @staticmethod
    def generate_next_member_number(db: Session, church_id: int) -> str:
        """
        다음 교번 자동생성
        형식: 교회별로 7자리 숫자 (0000001, 0000002, ...)
        """
        try:
            # 해당 교회의 가장 큰 교번 찾기
            result = db.execute(
                text("""
                    SELECT MAX(CAST(code AS INTEGER)) as max_code 
                    FROM members 
                    WHERE church_id = :church_id 
                    AND code IS NOT NULL 
                    AND code REGEXP '^[0-9]+$'
                """),
                {"church_id": church_id}
            ).fetchone()
            
            if result and result[0]:
                next_number = int(result[0]) + 1
            else:
                next_number = 1
                
            # 7자리 포맷으로 변환 (0000001)
            return f"{next_number:07d}"
            
        except Exception as e:
            # SQLite에서는 REGEXP가 작동하지 않을 수 있음
            try:
                # 대안: 모든 숫자형 교번 조회 후 Python에서 처리
                result = db.query(Member.code).filter(
                    Member.church_id == church_id,
                    Member.code.isnot(None)
                ).all()
                
                numeric_codes = []
                for row in result:
                    try:
                        numeric_codes.append(int(row[0]))
                    except (ValueError, TypeError):
                        continue
                
                if numeric_codes:
                    next_number = max(numeric_codes) + 1
                else:
                    next_number = 1
                    
                return f"{next_number:07d}"
                
            except Exception as e2:
                print(f"Error generating member number: {e2}")
                # 최후 수단: 현재 시간 기반
                import time
                timestamp = int(time.time()) % 10000000
                return f"{timestamp:07d}"
    
    @staticmethod
    def is_member_number_exists(db: Session, church_id: int, member_number: str) -> bool:
        """
        교번 중복 확인
        """
        existing = db.query(Member).filter(
            Member.church_id == church_id,
            Member.code == member_number
        ).first()
        
        return existing is not None
    
    @staticmethod
    def assign_member_number(db: Session, church_id: int) -> str:
        """
        사용 가능한 교번 생성 및 할당
        중복 검사 포함
        """
        max_attempts = 10
        
        for _ in range(max_attempts):
            member_number = MemberNumberService.generate_next_member_number(db, church_id)
            
            if not MemberNumberService.is_member_number_exists(db, church_id, member_number):
                return member_number
        
        # 최후 수단: 랜덤 생성
        import random
        random_number = random.randint(1000000, 9999999)
        return str(random_number)
    
    @staticmethod
    def update_existing_members_with_numbers(db: Session, church_id: int) -> int:
        """
        기존 교번이 없는 교인들에게 교번 일괄 할당
        """
        members_without_code = db.query(Member).filter(
            Member.church_id == church_id,
            Member.code.is_(None)
        ).all()
        
        updated_count = 0
        
        for member in members_without_code:
            member_number = MemberNumberService.assign_member_number(db, church_id)
            member.code = member_number
            updated_count += 1
            
        db.commit()
        return updated_count