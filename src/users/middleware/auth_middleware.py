# =====================================
# File: src/core/middleware/auth_middleware.py
# =====================================

"""
Authentication middleware for CampaignForge.

Handles JWT token validation and user authentication
for protected routes.
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import logging

from src.core.config.settings import settings
from src.core.shared.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """JWT authentication middleware."""
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode and validate JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            dict: Token payload
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise AuthenticationError("Invalid or expired token")
    
    @staticmethod
    def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials]) -> Optional[str]:
        """
        Extract user ID from authentication credentials.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            Optional[str]: User ID if authenticated, None otherwise
        """
        if not credentials:
            return None
        
        try:
            payload = AuthMiddleware.decode_token(credentials.credentials)
            return payload.get("sub")  # Subject claim contains user ID
        except AuthenticationError:
            return None
    
    @staticmethod
    def require_authentication(credentials: Optional[HTTPAuthorizationCredentials]) -> str:
        """
        Require valid authentication and return user ID.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            str: User ID
            
        Raises:
            HTTPException: If authentication fails
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            payload = AuthMiddleware.decode_token(credentials.credentials)
            user_id = payload.get("sub")
            if not user_id:
                raise AuthenticationError("Invalid token payload")
            return user_id
        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )