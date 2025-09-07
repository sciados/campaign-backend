# src/users/auth/__init__.py

"""Authentication Components"""

# Import authentication dependencies and utilities
try:
    from src.users.middleware.auth_middleware import get_current_user, verify_token
    __all__ = ["get_current_user", "verify_token"]
except ImportError:
    __all__ = []