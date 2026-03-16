from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.customer import crud
from src.customer.schemas import (
    CustomerPrivate,
    CustomerCreate,
    Token,
    CustomerPublic,
    CustomerUpdate,
)
from src.customer.security.auth import CurrentCustomer
from src.customer.security.dependencies import get_jwt_auth_manager
from src.customer.security.secutity import verify_password
from src.customer.security.token_manager import JWTAuthManager
from src.models.dependencies import get_db

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerPrivate, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    existing_customer = await crud.get_customer_by_username(db=db, username=customer.username)
    if existing_customer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    existing_email = await crud.get_customer_by_email(db=db, email=customer.email)
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return await crud.create_customer(db=db, customer=customer)


@router.post("/token/", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: JWTAuthManager = Depends(get_jwt_auth_manager),
):
    customer = await crud.get_customer_by_email(db, form_data.username)
    if not customer or not verify_password(form_data.password, customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    jwt_refresh_token = jwt_manager.create_refresh_token({"sub": str(customer.id)})
    try:
        await crud.create_refresh_token(
            db=db,
            customer_id=customer.id,
            token=jwt_refresh_token,
            days_valid=settings.refresh_token_expire_days,
        )
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the request.",
        )
    jwt_access_token = jwt_manager.create_access_token({"sub": str(customer.id)})
    return Token(
        access_token=jwt_access_token,
        refresh_token=jwt_refresh_token,
        token_type="bearer",
    )


@router.get("/me/", response_model=CustomerPrivate)
async def get_current_customer(current_customer: CurrentCustomer):
    return current_customer


@router.get("/{customer_id}/", response_model=CustomerPublic)
async def get_customer(customer_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    customer = await crud.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.patch("/{customer_id}/", response_model=CustomerPrivate)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    current_customer: CurrentCustomer,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if customer_id != current_customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this customer",
        )
    customer = await crud.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    if customer_update.username and customer_update.username.lower() != customer.username.lower():
        existing = await crud.get_customer_by_username(db, customer_update.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
    if customer_update.email and customer_update.email.lower() != customer.email:
        existing = await crud.get_customer_by_email(db, customer_update.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    return await crud.update_customer(db, customer, customer_update)


# @router.delete("/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(
#     user_id: int,
#     current_user: CurrentUser,
#     db: Annotated[AsyncSession, Depends(get_db)],
# ):
#     if user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to delete this user",
#         )
#     result = await db.execute(select(models.User).where(models.User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found",
#         )
#     old_filename = user.image_file
#     await db.delete(user)
#     await db.commit()
#     if old_filename:
#         delete_profile_image(old_filename)
