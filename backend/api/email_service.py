import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from .core import config

# SendGrid Configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@yourdomain.com")  # Change this to your email
SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "DocFusion AI")

# Configure SendGrid
sendgrid_client = None
if SENDGRID_API_KEY:
    sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)

def get_welcome_email_html(user_name: str) -> str:
    """Generate a themed welcome email HTML"""
    # Logo URL from Cloudinary (hosted)
    logo_url = os.getenv("LOGO_URL", "https://res.cloudinary.com/dggwdladu/image/upload/v1759913904/docfusion/docfusion_logo.png")
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to DocFusion AI</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: linear-gradient(135deg, #f8fafc 0%, #d1fae5 50%, #99f6e4 100%);">
    <div style="max-width: 600px; margin: 40px auto; background: white; border-radius: 24px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.1);">
        
        <!-- Header with gradient background -->
        <div style="background: linear-gradient(135deg, #10b981 0%, #14b8a6 100%); padding: 48px 32px; text-align: center;">
            <img src="{logo_url}" alt="DocFusion AI Logo" style="width: 100px; height: 100px; display: block; margin: 0 auto 20px;" />
            <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 900; letter-spacing: -0.5px;">DocFusion AI</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0; font-size: 14px; font-weight: 600;">Intelligent Document Assistant</p>
        </div>
        
        <!-- Content -->
        <div style="padding: 40px 32px;">
            <h2 style="color: #0f172a; font-size: 28px; font-weight: 800; margin: 0 0 16px; letter-spacing: -0.5px;">
                Welcome, {user_name}! 🎉
            </h2>
            
            <p style="color: #475569; font-size: 16px; line-height: 1.6; margin: 0 0 24px;">
                Thank you for joining <strong style="color: #0f172a;">DocFusion AI</strong>! We're excited to have you on board.
            </p>
            
            <p style="color: #475569; font-size: 16px; line-height: 1.6; margin: 0 0 32px;">
                With DocFusion AI, you can upload your PDF documents and interact with them using natural language. Ask questions, extract information, and gain insights from your documents effortlessly.
            </p>
            
            <!-- Features -->
            <div style="background: linear-gradient(135deg, #ecfdf5 0%, #f0fdfa 100%); border-radius: 16px; padding: 24px; margin-bottom: 32px; border: 2px solid #a7f3d0;">
                <h3 style="color: #047857; font-size: 18px; font-weight: 700; margin: 0 0 16px;">🚀 Getting Started:</h3>
                <ul style="margin: 0; padding-left: 20px; color: #064e3b;">
                    <li style="margin-bottom: 12px; line-height: 1.5;">
                        <strong>Upload Documents:</strong> Start by uploading your PDF files
                    </li>
                    <li style="margin-bottom: 12px; line-height: 1.5;">
                        <strong>Ask Questions:</strong> Chat naturally with your documents
                    </li>
                    <li style="margin-bottom: 12px; line-height: 1.5;">
                        <strong>Manage Sessions:</strong> Organize documents into different sessions
                    </li>
                    <li style="margin-bottom: 0; line-height: 1.5;">
                        <strong>Get Instant Answers:</strong> AI-powered responses with source references
                    </li>
                </ul>
            </div>
            
            <!-- CTA Button -->
            <div style="text-align: center; margin-bottom: 32px;">
                <a href="{os.getenv('FRONTEND_URL', 'http://localhost:5173')}" style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #14b8a6 100%); color: white; text-decoration: none; padding: 16px 40px; border-radius: 12px; font-weight: 700; font-size: 16px; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4); transition: all 0.3s;">
                    Start Using DocFusion AI
                </a>
            </div>
            
            <!-- Footer Info -->
            <div style="border-top: 2px solid #e2e8f0; padding-top: 24px;">
                <p style="color: #64748b; font-size: 14px; line-height: 1.6; margin: 0 0 12px;">
                    Need help? Our support team is here for you. Just reply to this email or visit our help center.
                </p>
                <p style="color: #64748b; font-size: 14px; line-height: 1.6; margin: 0;">
                    Happy document exploring! 📚✨
                </p>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background: #f8fafc; padding: 24px 32px; text-align: center; border-top: 1px solid #e2e8f0;">
            <p style="color: #94a3b8; font-size: 12px; margin: 0 0 8px;">
                © 2025 DocFusion AI. All rights reserved.
            </p>
            <p style="color: #94a3b8; font-size: 12px; margin: 0 0 8px;">
                You're receiving this email because you created an account with DocFusion AI.
            </p>
            <p style="color: #94a3b8; font-size: 11px; margin: 0;">
                <a href="{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/settings" style="color: #64748b; text-decoration: underline;">Update email preferences</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

async def send_welcome_email(to_email: str, user_name: str) -> bool:
    """Send a welcome email to a new user using SendGrid"""
    if not sendgrid_client:
        print("SendGrid API key not configured, skipping email")
        return True  # Return True so it doesn't cause issues
    
    try:
        # Plain text version (fallback)
        text_content = f"""
Welcome to DocFusion AI, {user_name}!

Thank you for joining DocFusion AI! We're excited to have you on board.

With DocFusion AI, you can upload your PDF documents and interact with them using natural language. Ask questions, extract information, and gain insights from your documents effortlessly.

Getting Started:
- Upload Documents: Start by uploading your PDF files
- Ask Questions: Chat naturally with your documents
- Manage Sessions: Organize documents into different sessions
- Get Instant Answers: AI-powered responses with source references

Visit {os.getenv('FRONTEND_URL', 'http://localhost:5173')} to get started!

Need help? Our support team is here for you. Just reply to this email.

Happy document exploring!

© 2025 DocFusion AI. All rights reserved.
"""
        
        # HTML version
        html_content = get_welcome_email_html(user_name)
        
        # Create SendGrid message
        message = Mail(
            from_email=Email(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
            to_emails=To(to_email),
            subject=f"Welcome to DocFusion AI, {user_name}! 🎉",
            plain_text_content=Content("text/plain", text_content),
            html_content=Content("text/html", html_content)
        )
        
        # Add tracking settings to improve deliverability
        message.tracking_settings = {
            "click_tracking": {"enable": False, "enable_text": False},
            "open_tracking": {"enable": False},
            "subscription_tracking": {"enable": False}
        }
        
        # Send email using SendGrid
        response = sendgrid_client.send(message)
        print(f"Welcome email sent successfully to {to_email} (Status: {response.status_code})")
        return True
        
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
        # Don't raise the exception - just log it and continue
        # This prevents email failures from breaking registration
        return False

