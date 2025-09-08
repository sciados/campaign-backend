# src/users/api/__init__.py

"""User API Routes"""

# Import router when routes.py is implemented
try:
    from src.users.api.routes import router
    __all__ = ["router"]
except ImportError:
    # Routes not implemented yet
    __all__ = []