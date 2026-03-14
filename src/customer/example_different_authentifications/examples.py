from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic

router = APIRouter(prefix="/examples", tags=["examples"])


##### basic authentication ######

USERNAME = "admin"
PASSWORD = "vovk7777"

security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    import secrets

    is_correct_username = secrets.compare_digest(credentials.username, USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.get("/protected/")
async def protected_endpoint(username: str = Depends(get_current_user)):
    """Protected endpoint that requires basic authentication."""
    return {"message": "This is a protected endpoint", "username": username}


################################################
