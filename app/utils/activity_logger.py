import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import Request
from sqlalchemy.orm import Session
from app import models
from app.schemas.activity_log import ActivityLogCreate
from app.utils.device_parser import get_client_ip


class ActivityLogger:
    """
    Central activity logging system for GDPR/Privacy law compliance
    Handles batch processing, IP extraction, and security validation
    """
    
    def __init__(self):
        self.log_queue = []
        self.batch_size = 100
        self.batch_timeout = 5  # seconds
        self.processing = False
    
    def extract_request_info(self, request: Request) -> Dict[str, str]:
        """
        Extract client information from request headers
        Handles proxy scenarios for accurate IP detection
        """
        return {
            "ip_address": get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "session_id": self.get_or_create_session_id(request)
        }
    
    def get_or_create_session_id(self, request: Request) -> str:
        """
        Get session ID from request or create a new one
        """
        # Try to get from authorization header or generate new one
        auth_header = request.headers.get("authorization", "")
        if auth_header:
            # Use part of the token as session ID for consistency
            return f"session_{hash(auth_header) % 1000000000}"
        return f"session_{uuid.uuid4().hex[:16]}"
    
    async def log_activity(self, db: Session, log_data: ActivityLogCreate, 
                          request: Request, immediate: bool = False) -> bool:
        """
        Log user activity with automatic IP and session detection
        
        Args:
            db: Database session
            log_data: Activity log data
            request: FastAPI request object
            immediate: If True, save immediately instead of batching
        
        Returns:
            bool: Success status
        """
        try:
            # Extract request information
            request_info = self.extract_request_info(request)
            
            # Create complete log entry
            complete_log = models.ActivityLog(
                user_id=log_data.user_id,
                session_id=request_info["session_id"],
                timestamp=log_data.timestamp or datetime.utcnow(),
                action=log_data.action,
                resource=log_data.resource,
                target_id=log_data.target_id,
                target_name=log_data.target_name,
                page_path=log_data.page_path,
                page_name=log_data.page_name,
                details=log_data.details,
                sensitive_data=log_data.sensitive_data,
                ip_address=request_info["ip_address"],
                user_agent=request_info["user_agent"]
            )
            
            if immediate:
                # Save immediately for critical logs (login, security events)
                db.add(complete_log)
                db.commit()
                print(f"🔒 IMMEDIATE LOG SAVED: {log_data.action.value} on {log_data.resource.value} by user {log_data.user_id}")
                return True
            else:
                # Add to batch queue for performance
                self.log_queue.append(complete_log)
                
                # Process batch if queue is full
                if len(self.log_queue) >= self.batch_size:
                    await self.process_batch(db)
                
                return True
                
        except Exception as e:
            print(f"❌ Activity logging failed: {e}")
            return False
    
    async def log_batch_activities(self, db: Session, log_batch: List[ActivityLogCreate], 
                                  request: Request) -> Dict[str, Any]:
        """
        Log multiple activities in batch for better performance
        
        Args:
            db: Database session
            log_batch: List of activity log data
            request: FastAPI request object
        
        Returns:
            Dict with success status and details
        """
        try:
            request_info = self.extract_request_info(request)
            saved_logs = []
            
            for log_data in log_batch:
                complete_log = models.ActivityLog(
                    user_id=log_data.user_id,
                    session_id=request_info["session_id"],
                    timestamp=log_data.timestamp or datetime.utcnow(),
                    action=log_data.action,
                    resource=log_data.resource,
                    target_id=log_data.target_id,
                    target_name=log_data.target_name,
                    page_path=log_data.page_path,
                    page_name=log_data.page_name,
                    details=log_data.details,
                    sensitive_data=log_data.sensitive_data,
                    ip_address=request_info["ip_address"],
                    user_agent=request_info["user_agent"]
                )
                saved_logs.append(complete_log)
            
            # Batch insert for performance
            db.add_all(saved_logs)
            db.commit()
            
            print(f"📊 BATCH LOG SAVED: {len(saved_logs)} activities logged")
            
            return {
                "success": True,
                "inserted_count": len(saved_logs),
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"❌ Batch activity logging failed: {e}")
            db.rollback()
            return {
                "success": False,
                "error": str(e),
                "inserted_count": 0
            }
    
    async def process_batch(self, db: Session) -> None:
        """
        Process queued logs in batch for performance optimization
        """
        if self.processing or not self.log_queue:
            return
            
        self.processing = True
        
        try:
            # Take current queue and create new one
            batch = self.log_queue[:self.batch_size]
            self.log_queue = self.log_queue[self.batch_size:]
            
            # Batch insert
            db.add_all(batch)
            db.commit()
            
            print(f"📦 BATCH PROCESSED: {len(batch)} activity logs saved")
            
        except Exception as e:
            print(f"❌ Batch processing failed: {e}")
            # Put failed logs back in queue for retry
            self.log_queue.extend(batch)
            db.rollback()
        finally:
            self.processing = False
    
    def log_login_success(self, db: Session, user_id: str, request: Request) -> None:
        """
        Log successful login with enhanced security tracking
        """
        try:
            request_info = self.extract_request_info(request)
            
            login_log = models.ActivityLog(
                user_id=user_id,
                session_id=request_info["session_id"],
                action=models.ActionType.LOGIN,
                resource=models.ResourceType.SYSTEM,
                target_name=f"User {user_id}",
                page_path="/login",
                page_name="로그인 성공",
                details={
                    "login_method": "password",
                    "browser": self.parse_browser_info(request_info["user_agent"]),
                    "success": True,
                    "login_time": datetime.utcnow().isoformat(),
                    "security_level": "standard"
                },
                ip_address=request_info["ip_address"],
                user_agent=request_info["user_agent"]
            )
            
            # Login events are saved immediately for security
            db.add(login_log)
            db.commit()
            
            print(f"🔐 LOGIN SUCCESS LOGGED: User {user_id} from {request_info['ip_address']}")
            
        except Exception as e:
            print(f"❌ Login success logging failed: {e}")
    
    def log_login_failure(self, db: Session, attempted_email: str, request: Request, 
                         failure_reason: str = "invalid_credentials") -> None:
        """
        Log failed login attempt for security monitoring
        """
        try:
            request_info = self.extract_request_info(request)
            
            failure_log = models.ActivityLog(
                user_id="anonymous",  # No valid user ID for failed login
                session_id=request_info["session_id"],
                action=models.ActionType.LOGIN,
                resource=models.ResourceType.SYSTEM,
                target_name=f"Failed login: {attempted_email}",
                page_path="/login",
                page_name="로그인 실패",
                details={
                    "attempted_email": attempted_email,
                    "failure_reason": failure_reason,
                    "success": False,
                    "attempt_time": datetime.utcnow().isoformat(),
                    "security_alert": failure_reason in ["too_many_attempts", "account_locked"]
                },
                sensitive_data=["attempted_email"],
                ip_address=request_info["ip_address"],
                user_agent=request_info["user_agent"]
            )
            
            # Failed login attempts are saved immediately for security
            db.add(failure_log)
            db.commit()
            
            print(f"🚨 LOGIN FAILURE LOGGED: {attempted_email} from {request_info['ip_address']} - {failure_reason}")
            
        except Exception as e:
            print(f"❌ Login failure logging failed: {e}")
    
    def parse_browser_info(self, user_agent: str) -> str:
        """
        Extract browser information from User-Agent string
        """
        if not user_agent:
            return "Unknown Browser"
        
        # Simple browser detection
        if "Chrome" in user_agent:
            return "Chrome"
        elif "Firefox" in user_agent:
            return "Firefox"
        elif "Safari" in user_agent and "Chrome" not in user_agent:
            return "Safari"
        elif "Edge" in user_agent:
            return "Edge"
        else:
            return "Other Browser"
    
    async def cleanup_old_logs(self, db: Session, days: int = 2555) -> int:
        """
        Clean up old activity logs (default: 7 years = 2555 days)
        For GDPR/Privacy law compliance
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            deleted_count = db.query(models.ActivityLog).filter(
                models.ActivityLog.timestamp < cutoff_date
            ).delete()
            
            db.commit()
            
            print(f"🗑️ CLEANUP COMPLETED: {deleted_count} old activity logs deleted")
            return deleted_count
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            db.rollback()
            return 0


# Global activity logger instance
activity_logger = ActivityLogger()


# Utility functions for easy logging
def log_member_view(db: Session, request: Request, user_id: str, member_id: str, 
                   member_name: str, accessed_fields: List[str]) -> None:
    """Quick utility to log member view activity"""
    log_data = ActivityLogCreate(
        user_id=user_id,
        session_id="",  # Will be set by logger
        action=models.ActionType.VIEW,
        resource=models.ResourceType.MEMBER,
        target_id=member_id,
        target_name=member_name,
        page_path="/member-management",
        page_name="교인 상세조회",
        details={
            "accessed_fields": accessed_fields,
            "view_type": "detail_modal"
        },
        sensitive_data=accessed_fields
    )
    asyncio.create_task(activity_logger.log_activity(db, log_data, request))


def log_member_update(db: Session, request: Request, user_id: str, member_id: str, 
                     member_name: str, updated_fields: List[str], 
                     old_values: Dict[str, Any] = None) -> None:
    """Quick utility to log member update activity"""
    details = {
        "updated_fields": updated_fields,
        "update_type": "form_edit"
    }
    if old_values:
        details["old_values"] = old_values
    
    log_data = ActivityLogCreate(
        user_id=user_id,
        session_id="",  # Will be set by logger
        action=models.ActionType.UPDATE,
        resource=models.ResourceType.MEMBER,
        target_id=member_id,
        target_name=member_name,
        page_path="/member-management/edit",
        page_name="교인 정보 수정",
        details=details,
        sensitive_data=updated_fields
    )
    asyncio.create_task(activity_logger.log_activity(db, log_data, request))