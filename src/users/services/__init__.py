# src/users/services/__init__.py

"""User Services"""

from src.users.services.user_service import UserService
from src.users.services.auth_service import AuthService

try:
    from src.users.services.user_storage_crud import UserStorageCRUD
    USER_STORAGE_AVAILABLE = True
except ImportError as e:
    print(f"UserStorageCRUD not available: {e}")
    UserStorageCRUD = None
    USER_STORAGE_AVAILABLE = False

__all__ = [
    "UserService",
    "AuthService",
]

if USER_STORAGE_AVAILABLE:
    __all__.append("UserStorageCRUD")