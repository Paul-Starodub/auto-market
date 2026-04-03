from src.core.config import settings
from src.security.token_manager import JWTAuthManager


def get_jwt_auth_manager() -> JWTAuthManager:
    """
    Create and return a JWT authentication manager instance.
    """
    return JWTAuthManager(
        secret_key_access=settings.SECRET_KEY_ACCESS.get_secret_value(),
        secret_key_refresh=settings.SECRET_KEY_REFRESH.get_secret_value(),
        algorithm=settings.JWT_SIGNING_ALGORITHM,
    )
