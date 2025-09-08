# src/users/services/__init__.py

"""User Services"""

from src.users.services.user_service import UserService
from src.users.services.auth_service import AuthService

# Temporarily remove UserStorageCRUD to fix circular import
try:
    from src.users.services.user_storage_crud import UserStorageCRUD
    print("UserStorageCRUD imported successfully")
except ImportError as e:
    print(f"UserStorageCRUD not available: {e}")
    UserStorageCRUD = None

__all__ = [
    "UserService",
    "AuthService",
]

# Only include UserStorageCRUD if it imported successfully
if 'UserStorageCRUD' in locals() and UserStorageCRUD is not None:
    __all__.append("UserStorageCRUD")