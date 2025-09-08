"""
커뮤니티 신청 관련 이메일 발송 유틸리티
승인/반려 알림 이메일 템플릿 및 발송 기능
"""

import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.config import settings


class CommunityEmailService:
    """커뮤니티 신청 이메일 서비스"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_user = getattr(settings, 'SMTP_USER', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@smartyoram.com')
        self.from_name = getattr(settings, 'FROM_NAME', '스마트요람')
    
    def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """실제 이메일 발송"""
        try:
            if not all([self.smtp_user, self.smtp_password]):
                print("⚠️ SMTP 설정이 없어서 이메일을 발송할 수 없습니다")
                return False
            
            # 이메일 메시지 구성
            msg = MimeMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # HTML 본문 추가
            html_part = MimeText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ 이메일 발송 성공: {to_email} - {subject}")
            return True
            
        except Exception as e:
            print(f"❌ 이메일 발송 실패: {to_email} - {str(e)}")
            return False
    
    def send_approval_email(
        self, 
        email: str, 
        organization_name: str, 
        contact_person: str,
        username: str, 
        temporary_password: str,
        application_id: int
    ) -> bool:
        """승인 완료 이메일 발송"""
        
        subject = "[스마트요람] 커뮤니티 회원 신청이 승인되었습니다"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Malgun Gothic', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .info-box {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
                .login-info {{ background: #e3f2fd; padding: 20px; margin: 15px 0; border-radius: 8px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
                .warning {{ color: #f44336; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 회원 신청이 승인되었습니다!</h1>
                </div>
                <div class="content">
                    <p><strong>{contact_person}</strong>님, 안녕하세요.</p>
                    
                    <p><strong>{organization_name}</strong>의 스마트요람 커뮤니티 회원 신청이 <span style="color: #4caf50; font-weight: bold;">승인</span>되었습니다.</p>
                    
                    <div class="info-box">
                        <h3>📋 신청 정보</h3>
                        <ul>
                            <li><strong>신청번호:</strong> #{application_id}</li>
                            <li><strong>단체명:</strong> {organization_name}</li>
                            <li><strong>담당자:</strong> {contact_person}</li>
                            <li><strong>이메일:</strong> {email}</li>
                            <li><strong>승인일:</strong> {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</li>
                        </ul>
                    </div>
                    
                    <div class="login-info">
                        <h3>🔑 로그인 정보</h3>
                        <ul>
                            <li><strong>로그인 URL:</strong> <a href="https://admin.smartyoram.com/login">https://admin.smartyoram.com/login</a></li>
                            <li><strong>아이디:</strong> <code style="background: #fff; padding: 2px 6px; border-radius: 3px;">{username}</code></li>
                            <li><strong>임시 비밀번호:</strong> <code style="background: #fff; padding: 2px 6px; border-radius: 3px;">{temporary_password}</code></li>
                        </ul>
                        
                        <p class="warning">⚠️ 보안을 위해 최초 로그인 후 반드시 비밀번호를 변경해주세요.</p>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="https://admin.smartyoram.com/login" class="button">지금 로그인하기</a>
                    </div>
                    
                    <div class="info-box">
                        <h3>📞 고객지원</h3>
                        <p>시스템 이용 중 문의사항이 있으시면 언제든 연락주세요.</p>
                        <ul>
                            <li><strong>이메일:</strong> support@smartyoram.com</li>
                            <li><strong>전화:</strong> 1588-0000</li>
                            <li><strong>운영시간:</strong> 평일 09:00~18:00</li>
                        </ul>
                    </div>
                    
                    <p>스마트요람 커뮤니티에 함께해주셔서 감사합니다!</p>
                </div>
                <div class="footer">
                    <p>본 메일은 발신전용입니다. 문의사항은 고객센터를 이용해주세요.</p>
                    <p>&copy; 2024 SmartYoram. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(email, subject, html_body)
    
    def send_rejection_email(
        self, 
        email: str, 
        organization_name: str, 
        contact_person: str,
        rejection_reason: str,
        application_id: int
    ) -> bool:
        """반려 알림 이메일 발송"""
        
        subject = "[스마트요람] 커뮤니티 회원 신청 검토 결과"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Malgun Gothic', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #ff7043 0%, #f4511e 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .info-box {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #ff7043; }}
                .reason-box {{ background: #ffebee; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #f44336; }}
                .reapply-box {{ background: #e8f5e8; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #4caf50; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .button {{ display: inline-block; background: #4caf50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 회원 신청 검토 결과</h1>
                </div>
                <div class="content">
                    <p><strong>{contact_person}</strong>님, 안녕하세요.</p>
                    
                    <p>아쉽게도 <strong>{organization_name}</strong>의 스마트요람 커뮤니티 회원 신청이 <span style="color: #f44336; font-weight: bold;">반려</span>되었습니다.</p>
                    
                    <div class="info-box">
                        <h3>📋 신청 정보</h3>
                        <ul>
                            <li><strong>신청번호:</strong> #{application_id}</li>
                            <li><strong>단체명:</strong> {organization_name}</li>
                            <li><strong>담당자:</strong> {contact_person}</li>
                            <li><strong>검토일:</strong> {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</li>
                        </ul>
                    </div>
                    
                    <div class="reason-box">
                        <h3>🔍 반려 사유</h3>
                        <p style="white-space: pre-line;">{rejection_reason}</p>
                    </div>
                    
                    <div class="reapply-box">
                        <h3>🔄 재신청 방법</h3>
                        <p>반려 사유를 참고하여 필요한 서류나 정보를 보완하신 후 다시 신청해주시기 바랍니다.</p>
                        
                        <div style="text-align: center;">
                            <a href="https://admin.smartyoram.com/community-signup" class="button">다시 신청하기</a>
                        </div>
                        
                        <p><strong>재신청 시 참고사항:</strong></p>
                        <ul>
                            <li>모든 필수 항목을 정확히 입력해주세요</li>
                            <li>첨부서류는 선명하고 읽기 쉽게 업로드해주세요</li>
                            <li>사업자등록증, 보험가입증명서 등이 필요할 수 있습니다</li>
                        </ul>
                    </div>
                    
                    <div class="info-box">
                        <h3>📞 문의하기</h3>
                        <p>반려 사유에 대한 상세한 문의나 재신청 관련 질문이 있으시면 언제든 연락주세요.</p>
                        <ul>
                            <li><strong>이메일:</strong> support@smartyoram.com</li>
                            <li><strong>전화:</strong> 1588-0000</li>
                            <li><strong>운영시간:</strong> 평일 09:00~18:00</li>
                        </ul>
                    </div>
                    
                    <p>앞으로도 스마트요람에 많은 관심 부탁드립니다.</p>
                </div>
                <div class="footer">
                    <p>본 메일은 발신전용입니다. 문의사항은 고객센터를 이용해주세요.</p>
                    <p>&copy; 2024 SmartYoram. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(email, subject, html_body)
    
    def send_admin_notification(self, application_data: Dict[str, Any]) -> bool:
        """관리자에게 새 신청서 알림 발송"""
        
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@smartyoram.com')
        subject = f"[스마트요람] 새로운 커뮤니티 회원 신청 (#{application_data['id']})"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2196f3; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f5f5f5; padding: 20px; }}
                .info-box {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .button {{ display: inline-block; background: #2196f3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🆕 새로운 커뮤니티 회원 신청</h2>
                </div>
                <div class="content">
                    <div class="info-box">
                        <h3>신청 정보</h3>
                        <ul>
                            <li><strong>신청번호:</strong> #{application_data['id']}</li>
                            <li><strong>신청자 유형:</strong> {application_data.get('applicant_type_display', application_data.get('applicant_type'))}</li>
                            <li><strong>단체명:</strong> {application_data['organization_name']}</li>
                            <li><strong>담당자:</strong> {application_data['contact_person']}</li>
                            <li><strong>이메일:</strong> {application_data['email']}</li>
                            <li><strong>연락처:</strong> {application_data['phone']}</li>
                            <li><strong>신청일시:</strong> {application_data['submitted_at']}</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="https://admin.smartyoram.com/admin/community/applications" class="button">관리 페이지에서 검토하기</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(admin_email, subject, html_body)


# 전역 인스턴스
community_email_service = CommunityEmailService()


def send_approval_email(application_data: Dict[str, Any], username: str, temporary_password: str) -> bool:
    """승인 완료 이메일 발송 (편의 함수)"""
    return community_email_service.send_approval_email(
        email=application_data['email'],
        organization_name=application_data['organization_name'],
        contact_person=application_data['contact_person'],
        username=username,
        temporary_password=temporary_password,
        application_id=application_data['id']
    )


def send_rejection_email(application_data: Dict[str, Any], rejection_reason: str) -> bool:
    """반려 알림 이메일 발송 (편의 함수)"""
    return community_email_service.send_rejection_email(
        email=application_data['email'],
        organization_name=application_data['organization_name'],
        contact_person=application_data['contact_person'],
        rejection_reason=rejection_reason,
        application_id=application_data['id']
    )


def send_admin_notification(application_data: Dict[str, Any]) -> bool:
    """관리자 알림 이메일 발송 (편의 함수)"""
    return community_email_service.send_admin_notification(application_data)