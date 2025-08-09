import asyncio
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.models.church import Church
from app.models.ai_agent import ChurchDatabaseConfig
from app.core.security import decrypt_data
import json

logger = logging.getLogger(__name__)


class ChurchDataService:
    """Service for connecting to church databases and retrieving data"""
    
    def __init__(self):
        self.connections = {}
    
    def get_connection_string(self, config: ChurchDatabaseConfig) -> str:
        """Build connection string from config"""
        password = decrypt_data(config.password) if config.password else ""
        
        if config.db_type == "mysql":
            return f"mysql+pymysql://{config.username}:{password}@{config.host}:{config.port}/{config.database_name}"
        elif config.db_type == "postgresql":
            return f"postgresql://{config.username}:{password}@{config.host}:{config.port}/{config.database_name}"
        elif config.db_type == "mssql":
            return f"mssql+pyodbc://{config.username}:{password}@{config.host}:{config.port}/{config.database_name}?driver=ODBC+Driver+17+for+SQL+Server"
        else:
            raise ValueError(f"Unsupported database type: {config.db_type}")
    
    async def test_connection(self, config: ChurchDatabaseConfig) -> Dict:
        """Test database connection and get available tables"""
        try:
            conn_string = self.get_connection_string(config)
            engine = create_engine(conn_string)
            
            with engine.connect() as conn:
                # Get list of tables
                if config.db_type == "mysql":
                    result = conn.execute(text("SHOW TABLES"))
                    tables = [row[0] for row in result]
                elif config.db_type == "postgresql":
                    result = conn.execute(text("""
                        SELECT tablename FROM pg_tables 
                        WHERE schemaname = 'public'
                    """))
                    tables = [row[0] for row in result]
                elif config.db_type == "mssql":
                    result = conn.execute(text("""
                        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
                        WHERE TABLE_TYPE = 'BASE TABLE'
                    """))
                    tables = [row[0] for row in result]
                else:
                    tables = []
                
                return {
                    "connected": True,
                    "tables_found": tables,
                    "error": None
                }
                
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return {
                "connected": False,
                "tables_found": [],
                "error": str(e)
            }
    
    async def query_members_absent(
        self, 
        church_id: int, 
        weeks: int = 4, 
        service_type: str = "sunday",
        db: Session = None
    ) -> Dict:
        """Query members who have been absent for specified weeks"""
        try:
            # Get church database config
            config = db.query(ChurchDatabaseConfig).filter(
                ChurchDatabaseConfig.church_id == church_id,
                ChurchDatabaseConfig.is_active == True
            ).first()
            
            if not config:
                return {"error": "No database configured for this church"}
            
            conn_string = self.get_connection_string(config)
            engine = create_engine(conn_string)
            
            with engine.connect() as conn:
                # Example query - adjust based on actual church database schema
                query = text("""
                    SELECT 
                        m.member_id,
                        m.name,
                        m.phone,
                        MAX(a.attendance_date) as last_attendance,
                        DATEDIFF(WEEK, MAX(a.attendance_date), GETDATE()) as weeks_absent
                    FROM members m
                    LEFT JOIN attendance a ON m.member_id = a.member_id
                    WHERE a.service_type = :service_type
                    GROUP BY m.member_id, m.name, m.phone
                    HAVING DATEDIFF(WEEK, MAX(a.attendance_date), GETDATE()) >= :weeks
                    ORDER BY weeks_absent DESC
                """)
                
                result = conn.execute(query, {
                    "weeks": weeks,
                    "service_type": service_type
                })
                
                absent_members = []
                for row in result:
                    absent_members.append({
                        "member_id": row[0],
                        "name": row[1],
                        "phone": row[2],
                        "last_attendance": row[3].isoformat() if row[3] else None,
                        "weeks_absent": row[4]
                    })
                
                return {
                    "query_result": absent_members,
                    "summary": f"{len(absent_members)}명이 {weeks}주 이상 결석했습니다."
                }
                
        except Exception as e:
            logger.error(f"Query members absent failed: {e}")
            return {"error": str(e)}
    
    async def query_attendance_stats(
        self,
        church_id: int,
        period: str = "month",
        db: Session = None
    ) -> Dict:
        """Get attendance statistics for specified period"""
        try:
            config = db.query(ChurchDatabaseConfig).filter(
                ChurchDatabaseConfig.church_id == church_id,
                ChurchDatabaseConfig.is_active == True
            ).first()
            
            if not config:
                return {"error": "No database configured for this church"}
            
            conn_string = self.get_connection_string(config)
            engine = create_engine(conn_string)
            
            with engine.connect() as conn:
                # Example query for attendance stats
                query = text("""
                    SELECT 
                        service_type,
                        COUNT(DISTINCT member_id) as attendees,
                        AVG(CAST(attended as FLOAT)) * 100 as attendance_rate,
                        attendance_date
                    FROM attendance
                    WHERE attendance_date >= DATEADD(:period, -1, GETDATE())
                    GROUP BY service_type, attendance_date
                    ORDER BY attendance_date DESC
                """)
                
                result = conn.execute(query, {"period": period})
                
                stats = []
                for row in result:
                    stats.append({
                        "service_type": row[0],
                        "attendees": row[1],
                        "attendance_rate": round(row[2], 2),
                        "date": row[3].isoformat() if row[3] else None
                    })
                
                return {
                    "query_result": stats,
                    "summary": f"최근 {period} 출석 통계"
                }
                
        except Exception as e:
            logger.error(f"Query attendance stats failed: {e}")
            return {"error": str(e)}
    
    async def query_member_info(
        self,
        church_id: int,
        search_term: str = None,
        db: Session = None
    ) -> Dict:
        """Search and retrieve member information"""
        try:
            config = db.query(ChurchDatabaseConfig).filter(
                ChurchDatabaseConfig.church_id == church_id,
                ChurchDatabaseConfig.is_active == True
            ).first()
            
            if not config:
                return {"error": "No database configured for this church"}
            
            conn_string = self.get_connection_string(config)
            engine = create_engine(conn_string)
            
            with engine.connect() as conn:
                query = text("""
                    SELECT 
                        member_id,
                        name,
                        phone,
                        email,
                        address,
                        birth_date,
                        join_date
                    FROM members
                    WHERE name LIKE :search_term
                       OR phone LIKE :search_term
                       OR email LIKE :search_term
                    LIMIT 50
                """)
                
                search_pattern = f"%{search_term}%" if search_term else "%"
                result = conn.execute(query, {"search_term": search_pattern})
                
                members = []
                for row in result:
                    members.append({
                        "member_id": row[0],
                        "name": row[1],
                        "phone": row[2],
                        "email": row[3],
                        "address": row[4],
                        "birth_date": row[5].isoformat() if row[5] else None,
                        "join_date": row[6].isoformat() if row[6] else None
                    })
                
                return {
                    "query_result": members,
                    "summary": f"{len(members)}명의 성도 정보를 찾았습니다."
                }
                
        except Exception as e:
            logger.error(f"Query member info failed: {e}")
            return {"error": str(e)}
    
    async def query_donation_stats(
        self,
        church_id: int,
        period: str = "month",
        db: Session = None
    ) -> Dict:
        """Get donation statistics for specified period"""
        try:
            config = db.query(ChurchDatabaseConfig).filter(
                ChurchDatabaseConfig.church_id == church_id,
                ChurchDatabaseConfig.is_active == True
            ).first()
            
            if not config:
                return {"error": "No database configured for this church"}
            
            conn_string = self.get_connection_string(config)
            engine = create_engine(conn_string)
            
            with engine.connect() as conn:
                query = text("""
                    SELECT 
                        donation_type,
                        SUM(amount) as total_amount,
                        COUNT(DISTINCT member_id) as donors,
                        AVG(amount) as avg_amount
                    FROM donations
                    WHERE donation_date >= DATEADD(:period, -1, GETDATE())
                    GROUP BY donation_type
                    ORDER BY total_amount DESC
                """)
                
                result = conn.execute(query, {"period": period})
                
                donations = []
                for row in result:
                    donations.append({
                        "donation_type": row[0],
                        "total_amount": float(row[1]),
                        "donors": row[2],
                        "avg_amount": float(row[3])
                    })
                
                total = sum(d["total_amount"] for d in donations)
                
                return {
                    "query_result": donations,
                    "summary": f"최근 {period} 총 헌금액: {total:,.0f}원"
                }
                
        except Exception as e:
            logger.error(f"Query donation stats failed: {e}")
            return {"error": str(e)}
    
    async def query_events(
        self,
        church_id: int,
        upcoming: bool = True,
        db: Session = None
    ) -> Dict:
        """Get church events"""
        try:
            config = db.query(ChurchDatabaseConfig).filter(
                ChurchDatabaseConfig.church_id == church_id,
                ChurchDatabaseConfig.is_active == True
            ).first()
            
            if not config:
                return {"error": "No database configured for this church"}
            
            conn_string = self.get_connection_string(config)
            engine = create_engine(conn_string)
            
            with engine.connect() as conn:
                if upcoming:
                    query = text("""
                        SELECT 
                            event_id,
                            event_name,
                            event_date,
                            location,
                            description
                        FROM events
                        WHERE event_date >= GETDATE()
                        ORDER BY event_date ASC
                        LIMIT 20
                    """)
                else:
                    query = text("""
                        SELECT 
                            event_id,
                            event_name,
                            event_date,
                            location,
                            description
                        FROM events
                        WHERE event_date < GETDATE()
                        ORDER BY event_date DESC
                        LIMIT 20
                    """)
                
                result = conn.execute(query)
                
                events = []
                for row in result:
                    events.append({
                        "event_id": row[0],
                        "event_name": row[1],
                        "event_date": row[2].isoformat() if row[2] else None,
                        "location": row[3],
                        "description": row[4]
                    })
                
                return {
                    "query_result": events,
                    "summary": f"{'예정된' if upcoming else '지난'} 행사 {len(events)}개"
                }
                
        except Exception as e:
            logger.error(f"Query events failed: {e}")
            return {"error": str(e)}


async def get_church_data(
    church_id: int,
    data_types: List[str],
    db: Session,
    **kwargs
) -> Dict:
    """Get church data based on requested types"""
    service = ChurchDataService()
    results = {}
    
    for data_type in data_types:
        if data_type == "attendance":
            results["attendance"] = await service.query_attendance_stats(
                church_id, db=db, **kwargs
            )
        elif data_type == "members":
            results["members"] = await service.query_member_info(
                church_id, db=db, **kwargs
            )
        elif data_type == "donations":
            results["donations"] = await service.query_donation_stats(
                church_id, db=db, **kwargs
            )
        elif data_type == "events":
            results["events"] = await service.query_events(
                church_id, db=db, **kwargs
            )
        elif data_type == "absent_members":
            results["absent_members"] = await service.query_members_absent(
                church_id, db=db, **kwargs
            )
    
    # Format results for GPT context
    context_text = ""
    for key, value in results.items():
        if "query_result" in value:
            context_text += f"\n[{key.upper()}]\n"
            context_text += f"Summary: {value.get('summary', '')}\n"
            context_text += f"Data: {json.dumps(value['query_result'], ensure_ascii=False, indent=2)}\n"
    
    return context_text


# Create service instance
church_data_service = ChurchDataService()