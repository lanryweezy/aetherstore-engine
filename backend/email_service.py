# email_service.py
# Email service for transactional emails using SendGrid/Mailgun

import os
import requests
from typing import Dict, List, Optional, Any
from fastapi import HTTPException
import logging
from config import settings
from jinja2 import Template
from pathlib import Path

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending transactional emails"""
    
    def __init__(self):
        self.provider = os.getenv("EMAIL_PROVIDER", "sendgrid").lower()
        self.sendgrid_api_key = settings.EMAIL_SENDGRID_API_KEY if hasattr(settings, 'EMAIL_SENDGRID_API_KEY') else os.getenv("SENDGRID_API_KEY", "")
        self.mailgun_api_key = settings.EMAIL_MAILGUN_API_KEY if hasattr(settings, 'EMAIL_MAILGUN_API_KEY') else os.getenv("MAILGUN_API_KEY", "")
        self.mailgun_domain = os.getenv("MAILGUN_DOMAIN", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@aetherstore.engine")
        self.from_name = os.getenv("FROM_NAME", "Aetherstore Engine")
        
        # Email templates directory
        self.templates_dir = Path("backend/email_templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize default templates
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize default email templates"""
        templates = {
            "welcome.html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .button { display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Aetherstore Engine!</h1>
        </div>
        <div class="content">
            <p>Hi {{name}},</p>
            <p>Welcome to Aetherstore Engine - the ultimate 3D fashion platform!</p>
            <p>Get started by creating your first 3D store.</p>
            <a href="{{dashboard_url}}" class="button">Go to Dashboard</a>
            <p>Best regards,<br>The Aetherstore Team</p>
        </div>
    </div>
</body>
</html>
            """,
            "order_confirmation.html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #667eea; color: white; padding: 30px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .order-details { background: white; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .total { font-size: 18px; font-weight: bold; color: #667eea; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Order Confirmation</h1>
        </div>
        <div class="content">
            <p>Hi {{customer_name}},</p>
            <p>Thank you for your order!</p>
            <div class="order-details">
                <p><strong>Order ID:</strong> {{order_id}}</p>
                <p><strong>Total:</strong> <span class="total">${{total_amount}}</span></p>
                <p><strong>Status:</strong> {{order_status}}</p>
            </div>
            <p>We'll send you tracking information once your order ships.</p>
            <p>Best regards,<br>{{brand_name}}</p>
        </div>
    </div>
</body>
</html>
            """,
            "subscription_confirmation.html": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #667eea; color: white; padding: 30px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .plan-details { background: white; padding: 15px; margin: 15px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Subscription Confirmed</h1>
        </div>
        <div class="content">
            <p>Hi {{brand_name}},</p>
            <p>Your subscription to Aetherstore Engine has been confirmed!</p>
            <div class="plan-details">
                <p><strong>Plan:</strong> {{plan_name}}</p>
                <p><strong>Amount:</strong> ${{amount}}/{{billing_cycle}}</p>
                <p><strong>Next billing:</strong> {{next_billing_date}}</p>
            </div>
            <p>You can now start creating your 3D stores!</p>
            <p>Best regards,<br>The Aetherstore Team</p>
        </div>
    </div>
</body>
</html>
            """
        }
        
        for filename, content in templates.items():
            template_path = self.templates_dir / filename
            if not template_path.exists():
                template_path.write_text(content)
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """Send an email"""
        try:
            if self.provider == "sendgrid":
                return await self._send_via_sendgrid(
                    to_email, subject, html_content, text_content,
                    from_email or self.from_email, from_name or self.from_name, attachments
                )
            elif self.provider == "mailgun":
                return await self._send_via_mailgun(
                    to_email, subject, html_content, text_content,
                    from_email or self.from_email, from_name or self.from_name, attachments
                )
            else:
                logger.warning(f"Unknown email provider: {self.provider}, using SMTP fallback")
                return await self._send_via_smtp(
                    to_email, subject, html_content, text_content,
                    from_email or self.from_email, from_name or self.from_name
                )
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    async def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        from_email: str,
        from_name: str,
        attachments: Optional[List[Dict]]
    ) -> bool:
        """Send email via SendGrid"""
        if not self.sendgrid_api_key:
            logger.error("SendGrid API key not configured")
            return False
        
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {self.sendgrid_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "personalizations": [{
                "to": [{"email": to_email}]
            }],
            "from": {
                "email": from_email,
                "name": from_name
            },
            "subject": subject,
            "content": [
                {
                    "type": "text/html",
                    "value": html_content
                }
            ]
        }
        
        if text_content:
            payload["content"].append({
                "type": "text/plain",
                "value": text_content
            })
        
        if attachments:
            payload["attachments"] = attachments
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 202:
            logger.info(f"Email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"SendGrid error: {response.status_code} - {response.text}")
            return False
    
    async def _send_via_mailgun(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        from_email: str,
        from_name: str,
        attachments: Optional[List[Dict]]
    ) -> bool:
        """Send email via Mailgun"""
        if not self.mailgun_api_key or not self.mailgun_domain:
            logger.error("Mailgun API key or domain not configured")
            return False
        
        url = f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages"
        auth = ("api", self.mailgun_api_key)
        
        data = {
            "from": f"{from_name} <{from_email}>",
            "to": to_email,
            "subject": subject,
            "html": html_content
        }
        
        if text_content:
            data["text"] = text_content
        
        files = []
        if attachments:
            for att in attachments:
                files.append(("attachment", (att.get("filename", "file"), att.get("content", ""))))
        
        response = requests.post(url, auth=auth, data=data, files=files if files else None)
        
        if response.status_code == 200:
            logger.info(f"Email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"Mailgun error: {response.status_code} - {response.text}")
            return False
    
    async def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        from_email: str,
        from_name: str
    ) -> bool:
        """Send email via SMTP (fallback)"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{from_name} <{from_email}>"
            msg['To'] = to_email
            
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            smtp_server = settings.SMTP_SERVER
            smtp_port = settings.SMTP_PORT
            smtp_user = settings.EMAIL_USERNAME
            smtp_password = settings.EMAIL_PASSWORD
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent via SMTP to {to_email}")
            return True
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
    
    async def send_welcome_email(self, user_email: str, user_name: str, dashboard_url: str = "https://app.aetherstore.engine/dashboard"):
        """Send welcome email to new user"""
        template_path = self.templates_dir / "welcome.html"
        template = Template(template_path.read_text())
        
        html_content = template.render(
            name=user_name,
            dashboard_url=dashboard_url
        )
        
        return await self.send_email(
            to_email=user_email,
            subject="Welcome to Aetherstore Engine!",
            html_content=html_content
        )
    
    async def send_order_confirmation(self, customer_email: str, customer_name: str, order_id: str, 
                                     total_amount: float, order_status: str, brand_name: str):
        """Send order confirmation email"""
        template_path = self.templates_dir / "order_confirmation.html"
        template = Template(template_path.read_text())
        
        html_content = template.render(
            customer_name=customer_name,
            order_id=order_id,
            total_amount=f"{total_amount:.2f}",
            order_status=order_status,
            brand_name=brand_name
        )
        
        return await self.send_email(
            to_email=customer_email,
            subject=f"Order Confirmation - {order_id}",
            html_content=html_content
        )
    
    async def send_subscription_confirmation(self, brand_email: str, brand_name: str, plan_name: str,
                                            amount: float, billing_cycle: str, next_billing_date: str):
        """Send subscription confirmation email"""
        template_path = self.templates_dir / "subscription_confirmation.html"
        template = Template(template_path.read_text())
        
        html_content = template.render(
            brand_name=brand_name,
            plan_name=plan_name,
            amount=f"{amount:.2f}",
            billing_cycle=billing_cycle,
            next_billing_date=next_billing_date
        )
        
        return await self.send_email(
            to_email=brand_email,
            subject="Subscription Confirmed - Aetherstore Engine",
            html_content=html_content
        )

# Global email service instance
email_service = EmailService()

