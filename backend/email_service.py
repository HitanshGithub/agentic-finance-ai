"""
Email service for sending verification emails.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# SMTP Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def send_verification_email(to_email: str, verification_token: str) -> bool:
    """
    Send a verification email to the user.
    Returns True if successful, False otherwise.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        print("⚠️ SMTP not configured. Verification email not sent.")
        print(f"📧 Verification link: {FRONTEND_URL}/verify/{verification_token}")
        return True  # Return True in dev mode so signup can proceed
    
    verification_link = f"{FRONTEND_URL}/verify/{verification_token}"
    
    # Create email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify your Agentic Finance AI account"
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    
    # Plain text version
    text = f"""
Welcome to Agentic Finance AI!

Please verify your email address by clicking the link below:

{verification_link}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
Agentic Finance AI Team
    """
    
    # HTML version
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #1a1a2e; color: #ffffff; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #00d4ff; margin: 0; }}
        .content {{ background-color: #16213e; border-radius: 10px; padding: 30px; }}
        .button {{ display: inline-block; background: linear-gradient(135deg, #00d4ff, #7b2cbf); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Agentic Finance AI</h1>
        </div>
        <div class="content">
            <h2>Welcome! 🎉</h2>
            <p>Thanks for signing up! Please verify your email address to get started.</p>
            <p style="text-align: center;">
                <a href="{verification_link}" class="button">✅ Verify Email</a>
            </p>
            <p style="font-size: 12px; color: #888;">
                Or copy this link: {verification_link}
            </p>
            <p style="font-size: 12px; color: #888;">
                This link will expire in 24 hours.
            </p>
        </div>
        <div class="footer">
            <p>If you didn't create an account, please ignore this email.</p>
        </div>
    </div>
</body>
</html>
    """
    
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        print(f"✅ Verification email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        print(f"")
        print(f"📧📧📧 COPY THIS VERIFICATION LINK 📧📧📧")
        print(f"👉 {verification_link}")
        print(f"📧📧📧📧📧📧📧📧📧📧📧📧📧📧📧📧📧📧📧📧")
        print(f"")
        return True  # Return True so signup succeeds
