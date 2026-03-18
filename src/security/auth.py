from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.customer.security.dependencies import get_jwt_auth_manager
from src.customer.security.token_manager import JWTAuthManager
from src.database.dependencies import get_db

if TYPE_CHECKING:
    from src import database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="customers/login")


async def get_current_customer(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: JWTAuthManager = Depends(get_jwt_auth_manager),
) -> "database.Customer":
    from src import database

    customer_id = jwt_manager.decode_access_token(token)
    if customer_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        customer_id_int = int(customer_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = await db.execute(
        select(database.Customer).where(database.Customer.id == customer_id_int),
    )
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return customer


CurrentCustomer = Annotated["models.Customer", Depends(get_current_customer)]
