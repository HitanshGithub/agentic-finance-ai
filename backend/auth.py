"""
Authentication utilities for user signup, login, and JWT tokens.
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
import bcrypt
from jose import JWTError, jwt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

load_dotenv()

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Email verification token
EMAIL_VERIFICATION_SECRET = os.getenv("EMAIL_VERIFICATION_SECRET", secrets.token_hex(32))
email_serializer = URLSafeTimedSerializer(EMAIL_VERIFICATION_SECRET)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user_id: str, email: str) -> str:
    """Create a JWT access token."""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def create_email_verification_token(email: str) -> str:
    """Create a token for email verification."""
    return email_serializer.dumps(email, salt="email-verify")


def verify_email_token(token: str, max_age: int = 86400) -> Optional[str]:
    """
    Verify an email verification token.
    Returns the email if valid, None otherwise.
    max_age is in seconds (default 24 hours).
    """
    try:
        email = email_serializer.loads(token, salt="email-verify", max_age=max_age)
        return email
    except (SignatureExpired, BadSignature):
        return None


def verify_google_token(token: str, client_id: str) -> Optional[dict]:
    """
    Verify a Google OAuth token.
    Returns user info if valid, None otherwise.
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            client_id
        )
        
        # Verify the issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return None
            
        return {
            "google_id": idinfo['sub'],
            "email": idinfo['email'],
            "name": idinfo.get('name', ''),
            "picture": idinfo.get('picture', '')
        }
    except Exception:
        return None
