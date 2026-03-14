import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import (
    HTTPBasicCredentials,
    HTTPBasic,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from pydantic import BaseModel

from src.config import settings

router = APIRouter(prefix="/examples", tags=["examples"])


##### basic authentication ######

USERNAME = "admin"
PASSWORD = "vovk7777"

# security = HTTPBasic()


# def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
#
#     is_correct_username = secrets.compare_digest(credentials.username, USERNAME)
#     is_correct_password = secrets.compare_digest(credentials.password, PASSWORD)
#     if not (is_correct_username and is_correct_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Basic"},
#         )
#     return credentials.username
#
#
# @router.get("/protected/")
# async def protected_endpoint(username: str = Depends(get_current_user)):
#     """Protected endpoint that requires basic authentication."""
#     return {"message": "This is a protected endpoint", "username": username}


################################################


######## session authentication ################


# class ErrorMessage(BaseModel):
#     """Error message model."""
#
#     detail: str
#
#
# class LoginRequest(BaseModel):
#     """Login request model."""
#
#     username: str
#     password: str
#
#
# class LoginResponse(BaseModel):
#     """Login response model."""
#
#     username: str
#     message: str = "Login successful"
#
#
# # Simple in-memory session store
# # In production, use Redis or a database
# active_sessions: Dict[str, str] = {}


# def get_random_session_token(length: int = 32) -> str:
#     """Generate a random session token."""
#     alphabet = string.ascii_letters + string.digits
#     return "".join(secrets.choice(alphabet) for _ in range(length))
#
#
# def validate_credentials(username: str, password: str) -> bool:
#     """Validate user credentials.
#
#     Using secrets.compare_digest() instead of regular string comparison (==)
#     provides protection against timing attacks. A timing attack is where
#     an attacker measures the time it takes to compare strings to determine
#     if they're getting closer to the correct value. The secrets module ensures
#     that the comparison takes the same amount of time regardless of how many
#     characters match, making the comparison resistant to timing attacks.
#     """
#     return secrets.compare_digest(username, "admin") and secrets.compare_digest(
#         password, "vovk7777"
#     )
#
#
# def create_session(username: str, response: Response) -> str:
#     """Create a new session for the user and set the session cookie."""
#     session_token = get_random_session_token()
#     active_sessions[session_token] = username
#
#     # Set the session cookie
#     response.set_cookie(
#         key="session_token",
#         value=session_token,
#         httponly=True,  # Prevent JavaScript access
#         max_age=1800,  # 30 minutes
#         # secure=True,  # Uncomment in production (HTTPS only)
#         samesite="lax",  # Prevent CSRF
#     )
#
#     return session_token
#
#
# def get_current_user_from_cookie(session_token: Optional[str] = Cookie(None)) -> str:
#     """Validate the session token from cookie."""
#     if session_token is None or session_token not in active_sessions:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid session or session expired",
#         )
#
#     return active_sessions[session_token]
#
#
# def end_session(session_token: str, response: Response) -> None:
#     """End a user session and clear the cookie."""
#     if session_token in active_sessions:
#         del active_sessions[session_token]
#
#     response.delete_cookie(key="session_token")
#
#
# @router.post(
#     "/login/",
#     response_model=LoginResponse,
#     summary="Login with username and password",
#     description="Create a session and set a cookie",
#     responses={
#         200: {"description": "Login successful"},
#         401: {
#             "model": ErrorMessage,
#             "description": "Unauthorized: Invalid credentials",
#         },
#     },
# )
# async def login(login_request: LoginRequest, response: Response):
#     """Login endpoint that creates a session and sets a cookie."""
#     # Validate credentials
#     if not validate_credentials(login_request.username, login_request.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid username or password",
#         )
#
#     # Create session and set cookie
#     create_session(login_request.username, response)
#
#     return LoginResponse(username=login_request.username)
#
#
# @router.get(
#     "/protected/",
#     summary="Protected route (requires session cookie)",
#     description="This endpoint requires a valid session cookie to access",
#     responses={
#         200: {"description": "Successful response"},
#         401: {
#             "model": ErrorMessage,
#             "description": "Unauthorized: Invalid or missing session",
#         },
#     },
# )
# async def protected_route(username: str = Depends(get_current_user_from_cookie)):
#     """Protected route that requires a valid session cookie."""
#     return {
#         "message": "This is a protected route",
#         "data": "secret information accessible with cookie",
#         "authenticated_user": username,
#     }
#
#
# @router.post(
#     "/logout/",
#     summary="Logout and end session",
#     description="End the current session and clear the session cookie",
#     responses={
#         200: {"description": "Logout successful"},
#         401: {
#             "model": ErrorMessage,
#             "description": "Unauthorized: Invalid or missing session",
#         },
#     },
# )
# async def logout(
#     response: Response,
#     session_token: Optional[str] = Cookie(None, alias="session_token"),
# ):
#     """Logout endpoint that ends the session and clears the cookie."""
#     if not session_token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="No active session"
#         )
#
#     end_session(session_token, response)
#
#     return {"message": "Logout successful"}


##############################

######## jwt authentication ######


class ErrorMessage(BaseModel):
    """Error message model."""

    detail: str


class LoginRequest(BaseModel):
    """Login request model."""

    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""

    access_token: str
    token_type: str = "bearer"
    username: str
    message: str = "Login successful"


# Simple in-memory token blacklist store
# In production, use Redis or a database
blacklisted_tokens: Dict[str, datetime] = {}

# JWT Security
security = HTTPBearer()

# Global secret key to ensure consistency
_jwt_secret_key: Optional[str] = None


def get_jwt_secret_key() -> str:
    """Get JWT secret key from settings or generate a consistent one."""
    global _jwt_secret_key

    # First, try to get from settings
    if hasattr(settings, "JWT_SECRET_KEY") and settings.JWT_SECRET_KEY:
        return settings.JWT_SECRET_KEY

    # If not in settings, generate once and store globally
    if _jwt_secret_key is None:
        _jwt_secret_key = secrets.token_urlsafe(32)
        print(f"Generated JWT secret key: {_jwt_secret_key}")  # For debugging

    return _jwt_secret_key


def validate_credentials(username: str, password: str) -> bool:
    """Validate user credentials.

    Using secrets.compare_digest() instead of regular string comparison (==)
    provides protection against timing attacks. A timing attack is where
    an attacker measures the time it takes to compare strings to determine
    if they're getting closer to the correct value. The secrets module ensures
    that the comparison takes the same amount of time regardless of how many
    characters match, making the comparison resistant to timing attacks.
    """
    return secrets.compare_digest(username, settings.API_USERNAME) and secrets.compare_digest(
        password, settings.API_PASSWORD
    )


def create_jwt_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token for the user."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": username,  # Subject (user identifier)
        "exp": int(expire.timestamp()),  # Expiration time as Unix timestamp
        "iat": int(datetime.now(timezone.utc).timestamp()),  # Issued at as Unix timestamp
        "jti": secrets.token_urlsafe(16),  # JWT ID (unique identifier)
    }

    return jwt.encode(payload, get_jwt_secret_key(), algorithm="HS256")


def decode_jwt_token(token: str) -> Dict:
    """Decode and validate a JWT token."""
    try:
        # Check if token is blacklisted
        if token in blacklisted_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        # Decode the token
        payload = jwt.decode(token, get_jwt_secret_key(), algorithms=["HS256"])
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Extract and validate the current user from JWT token."""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    username = payload.get("sub")

    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    return username


def blacklist_token(token: str) -> None:
    """Add token to blacklist (for logout functionality)."""
    try:
        payload = jwt.decode(token, get_jwt_secret_key(), algorithms=["HS256"])
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            blacklisted_tokens[token] = exp_datetime

            # Clean up expired blacklisted tokens
            cleanup_expired_blacklisted_tokens()
    except jwt.InvalidTokenError:
        # If token is invalid, no need to blacklist
        pass


def cleanup_expired_blacklisted_tokens() -> None:
    """Remove expired tokens from blacklist to prevent memory leaks."""
    current_time = datetime.now(timezone.utc)
    expired_tokens = [token for token, exp_time in blacklisted_tokens.items() if exp_time < current_time]

    for token in expired_tokens:
        del blacklisted_tokens[token]


@router.post(
    "/login/",
    response_model=LoginResponse,
    summary="Login with username and password",
    description="Get a JWT access token",
    responses={
        200: {"description": "Login successful"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid credentials",
        },
    },
)
async def login(login_request: LoginRequest):
    """Login endpoint that returns a JWT access token."""
    # Validate credentials
    if not validate_credentials(login_request.username, login_request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create JWT token
    access_token = create_jwt_token(login_request.username)

    return LoginResponse(access_token=access_token, username=login_request.username)


@router.get(
    "/protected/",
    summary="Protected route (requires JWT token)",
    description="This endpoint requires a valid JWT token in Authorization header",
    responses={
        200: {"description": "Successful response"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token",
        },
    },
)
async def protected_route(username: str = Depends(get_current_user)):
    """Protected route that requires a valid JWT token."""
    return {
        "message": "This is a protected route",
        "data": "secret information accessible with JWT token",
        "authenticated_user": username,
    }


@router.post(
    "/logout/",
    summary="Logout and blacklist token",
    description="Blacklist the current JWT token to prevent further use",
    responses={
        200: {"description": "Logout successful"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token",
        },
    },
)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout endpoint that blacklists the current JWT token."""
    token = credentials.credentials
    blacklist_token(token)

    return {"message": "Logout successful"}


@router.get(
    "/me/",
    summary="Get current user info",
    description="Get information about the currently authenticated user",
    responses={
        200: {"description": "User information"},
        401: {
            "model": ErrorMessage,
            "description": "Unauthorized: Invalid or missing token",
        },
    },
)
async def get_user_info(username: str = Depends(get_current_user)):
    """Get current user information from JWT token."""
    return {"username": username, "message": "User information retrieved successfully"}
