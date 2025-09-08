# src/users/__init__.py
"""
Users Module - Authentication and User Management

Handles:
- User authentication and authorization
- User profile management  
- Admin and user dashboards
- User preferences and settings
"""
# from src.users.auth.auth_middleware import AuthMiddleware
from src.users.models.user import User
from src.users.services.user_service import UserService
from .users_module import UsersModule

__all__ = ["UsersModule"]