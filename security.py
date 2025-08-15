from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import hashlib
import hmac
from typing import Dict, Any
import re
import html

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

class SecurityMiddleware:
    """Enhanced security middleware for input validation and rate limiting"""
    
    @staticmethod
    def sanitize_input(data: Any) -> Any:
        """Sanitize user input to prevent XSS and injection attacks"""
        if isinstance(data, str):
            # Remove HTML tags and escape special characters
            data = html.escape(data.strip())
            # Remove potentially dangerous characters
            data = re.sub(r'[<>"\']', '', data)
            return data
        elif isinstance(data, dict):
            return {key: SecurityMiddleware.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [SecurityMiddleware.sanitize_input(item) for item in data]
        return data
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        return True, "Password is valid"
    
    @staticmethod
    def validate_location(location: str) -> bool:
        """Validate location input"""
        # Allow letters, spaces, commas, and basic punctuation
        location_pattern = r'^[a-zA-Z0-9\s,.-]+$'
        return re.match(location_pattern, location) is not None and len(location) <= 100
    
    @staticmethod
    def validate_trade(trade: str) -> bool:
        """Validate trade category"""
        allowed_trades = [
            'roofing', 'solar', 'pool', 'painting', 'plumbing',
            'electrical', 'hvac', 'landscaping', 'construction', 'remodeling'
        ]
        return trade.lower() in allowed_trades

class CSRFProtection:
    """CSRF protection for forms"""
    
    @staticmethod
    def generate_csrf_token(secret_key: str, user_id: str) -> str:
        """Generate CSRF token"""
        timestamp = str(int(time.time()))
        message = f"{user_id}:{timestamp}"
        signature = hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{message}:{signature}"
    
    @staticmethod
    def validate_csrf_token(token: str, secret_key: str, user_id: str, max_age: int = 3600) -> bool:
        """Validate CSRF token"""
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return False
            
            token_user_id, timestamp, signature = parts
            
            # Check if token is for the right user
            if token_user_id != user_id:
                return False
            
            # Check if token is not expired
            if int(time.time()) - int(timestamp) > max_age:
                return False
            
            # Verify signature
            message = f"{token_user_id}:{timestamp}"
            expected_signature = hmac.new(
                secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except (ValueError, TypeError):
            return False

class SecureHTTPBearer(HTTPBearer):
    """Enhanced HTTP Bearer authentication with additional security checks"""
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        credentials = await super().__call__(request)
        
        if credentials:
            # Additional token validation
            if not self._is_valid_token_format(credentials.credentials):
                raise HTTPException(
                    status_code=403,
                    detail="Invalid token format"
                )
        
        return credentials
    
    def _is_valid_token_format(self, token: str) -> bool:
        """Validate JWT token format"""
        parts = token.split('.')
        return len(parts) == 3 and all(part for part in parts)

# Rate limiting decorators
def rate_limit_auth():
    """Rate limit for authentication endpoints"""
    return limiter.limit("5/minute")

def rate_limit_search():
    """Rate limit for search endpoints"""
    return limiter.limit("10/minute")

def rate_limit_export():
    """Rate limit for export endpoints"""
    return limiter.limit("3/minute")

def rate_limit_general():
    """General rate limit for other endpoints"""
    return limiter.limit("60/minute")
