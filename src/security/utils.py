import hashlib
import secrets


def generate_secure_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
