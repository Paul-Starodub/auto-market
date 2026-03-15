from datetime import datetime, timedelta, UTC
from typing import Optional

import jwt

from src.config import get_settings

settings = get_settings()


class JWTAuthManager:
    """
    A manager for creating, decoding, and verifying JWT access and refresh tokens.
    """

    def __init__(self, secret_key_access: str, secret_key_refresh: str, algorithm: str):
        """
        Initialize the manager with secret keys and algorithm for token operations.
        """
        self._secret_key_access = secret_key_access
        self._secret_key_refresh = secret_key_refresh
        self._algorithm = algorithm

    def _create_token(
        self, data: dict, secret_key: str, expires_delta: timedelta
    ) -> str:
        """
        Create a JWT token with provided data, secret key, and expiration time.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=settings.access_token_expire_minutes,
            )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, secret_key, algorithm=self._algorithm)

    def _decode_token(self, token: str, secret_key: str):
        try:
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[self._algorithm],
                options={"require": ["exp", "sub"]},
            )
        except jwt.InvalidTokenError:
            return None
        return payload.get("sub")

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a new access token with a default or specified expiration time.
        """
        return self._create_token(data, self._secret_key_access, expires_delta)

    def create_refresh_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a new refresh token with a default or specified expiration time.
        """
        return self._create_token(data, self._secret_key_refresh, expires_delta)

    def decode_access_token(self, token: str):
        """
        Decode and validate an access token, returning the token's data.
        """
        return self._decode_token(token, self._secret_key_access)

    def decode_refresh_token(self, token: str):
        """
        Decode and validate a refresh token, returning the token's data.
        """
        return self._decode_token(token, self._secret_key_refresh)
