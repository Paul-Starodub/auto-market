from src.config import settings
from src.security.token_manager import JWTAuthManager


def get_jwt_auth_manager() -> JWTAuthManager:
    """
    Create and return a JWT authentication manager instance.
    """
    return JWTAuthManager(
        secret_key_access=settings.SECRET_KEY_ACCESS,
        secret_key_refresh=settings.SECRET_KEY_REFRESH,
        algorithm=settings.JWT_SIGNING_ALGORITHM,
    )
