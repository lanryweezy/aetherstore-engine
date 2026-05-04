# security_middleware.py
# Security middleware for rate limiting, validation, and headers

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable, Optional, Any
import logging
import re
from config import settings

logger = logging.getLogger(__name__)

# Optional slowapi dependency
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False

# Initialize rate limiter
if SLOWAPI_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
else:
    class MockLimiter:
        def limit(self, *args, **kwargs):
            return lambda func: func
    limiter = MockLimiter()

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' cdn.aframe.io cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://api.stripe.com https://api.paystack.co;"
    ),
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}

class SecurityMiddleware:
    """Security middleware for adding headers and validation"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    for header, value in SECURITY_HEADERS.items():
                        headers[header.lower().encode()] = value.encode()
                    message["headers"] = list(headers.items())
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)

def validate_input(input_str: str, max_length: int = 1000) -> bool:
    """Validate input string for common injection patterns"""
    if not isinstance(input_str, str):
        return False
    if len(input_str) > max_length:
        return False
    
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|/\*|\*/|xp_|sp_)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            logger.warning(f"Potential SQL injection detected: {input_str[:50]}")
            return False
    
    xss_patterns = [
        r"<script[^>]*>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            logger.warning(f"Potential XSS detected: {input_str[:50]}")
            return False
    
    return True

def sanitize_string(input_str: str) -> str:
    """Sanitize input string"""
    if not isinstance(input_str, str):
        return ""
    input_str = input_str.replace("\x00", "")
    input_str = "".join(char for char in input_str if ord(char) >= 32 or char in "\n\t")
    return input_str.strip()

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, email))

def validate_uuid(uuid_str: str) -> bool:
    """Validate UUID format"""
    if not uuid_str:
        return False
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return bool(re.match(uuid_pattern, uuid_str, re.IGNORECASE))

async def rate_limit_handler(request: Request, exc: Any):
    """Handle rate limit exceeded"""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": 60
        },
        headers={"Retry-After": "60"}
    )

def rate_limit(requests_per_minute: int = 60):
    """Rate limit decorator"""
    return limiter.limit(f"{requests_per_minute}/minute")
