# ============================================================================
# ENHANCED AUTH SERVICE (Session 5 Re-enablement) - FIXED
# ============================================================================

# src/users/services/auth_service.py (Fixed .value issues)

from typing import Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import jwt
from passlib.context import CryptContext

from src.users.models.user import User
from src.users.services.user_service import UserService
from src.core.config.settings import get_settings
from src.core.shared.exceptions import ValidationError, NotFoundError

logger = logging.getLogger(__name__)
settings = get_settings()

class AuthService:
    """Enhanced Authentication Service with full implementation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = await self.user_service.authenticate_user(email, password)
            if user:
                logger.info(f"User authenticated successfully: {user.id}")
            else:
                logger.warning(f"Authentication failed for email: {email}")
            return user
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise
    
    async def create_access_token(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token for user"""
        try:
            if expires_delta:
                expire = datetime.now(timezone.utc) + expires_delta
            else:
                expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
            
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "exp": expire,
                "iat": datetime.now(timezone.utc),
                "type": "access"
            }
            
            encoded_jwt = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Access token created for user: {user.id}")
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Token creation error: {e}")
            raise
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != "access":
                return None
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                return None
            
            return payload
            
        except jwt.PyJWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token"""
        try:
            payload = await self.verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            user = await self.user_service.get_user_by_id(user_id, include_company=True)
            return user
            
        except Exception as e:
            logger.error(f"Get current user error: {e}")
            return None
    
    async def login(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """Complete login process - FIXED: Removed .value calls"""
        try:
            # Authenticate user
            user = await self.authenticate_user(email, password)
            if not user:
                raise ValidationError("Invalid email or password", field="credentials")
            
            # Create access token
            access_token = await self.create_access_token(user)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role if user.role else "USER",  # FIXED: Removed .value
                    "user_type": user.user_type if user.user_type else None,  # FIXED: Removed .value
                    "company": {
                        "id": str(user.company.id),
                        "name": user.company.company_name,
                        "slug": user.company.company_slug,
                        "subscription_tier": user.company.subscription_tier  # FIXED: Removed .value
                    } if user.company else None
                }
            }
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise
    
    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
        company_name: str = "Default Company"
    ) -> Dict[str, Any]:
        """Complete registration process"""
        try:
            # Create user
            user = await self.user_service.create_user(
                email=email,
                password=password,
                full_name=full_name,
                company_name=company_name
            )
            
            return {
                "message": "User registered successfully",
                "user_id": str(user.id),
                "company_id": str(user.company_id) if user.company_id else None,
                "email": user.email
            }
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Auth service health check"""
        try:
            # Test database connection
            test_query = select(User).limit(1)
            await self.db.execute(test_query)
            
            return {
                "status": "healthy",
                "service": "auth_service",
                "database": "connected",
                "token_expiry_minutes": self.access_token_expire_minutes
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "auth_service",
                "error": str(e)
            }