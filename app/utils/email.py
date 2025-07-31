import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os


def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> bool:
    """
    Send an email using SMTP.
    Returns True if successful, False otherwise.
    """
    # Email configuration from environment variables
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    from_email = os.getenv("FROM_EMAIL", smtp_user)
    
    if not smtp_user or not smtp_password:
        print("SMTP credentials not configured. Skipping email send.")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Add text part
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # Add HTML part if provided
        if html_body:
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_temporary_password_email(
    to_email: str,
    member_name: str,
    church_name: str,
    temp_password: str
) -> bool:
    """
    Send temporary password email to new member.
    """
    subject = f"[{church_name}] 스마트요람 임시 비밀번호 안내"
    
    body = f"""
안녕하세요 {member_name}님,

{church_name} 스마트요람에 가입되셨습니다.
아래 정보로 로그인하실 수 있습니다.

이메일: {to_email}
임시 비밀번호: {temp_password}

보안을 위해 로그인 후 비밀번호를 변경해주세요.

감사합니다.
{church_name} 드림
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .info-box {{ background-color: #f9f9f9; padding: 15px; margin: 20px 0; border-left: 4px solid #007bff; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{church_name} 스마트요람</h2>
        </div>
        <div class="content">
            <p>안녕하세요 <strong>{member_name}</strong>님,</p>
            <p>{church_name} 스마트요람에 가입되셨습니다.</p>
            <p>아래 정보로 로그인하실 수 있습니다.</p>
            
            <div class="info-box">
                <p><strong>이메일:</strong> {to_email}</p>
                <p><strong>임시 비밀번호:</strong> {temp_password}</p>
            </div>
            
            <p style="color: #dc3545;">보안을 위해 로그인 후 비밀번호를 변경해주세요.</p>
        </div>
        <div class="footer">
            <p>{church_name} 드림</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(to_email, subject, body, html_body)