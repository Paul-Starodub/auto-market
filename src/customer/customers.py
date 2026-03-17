from datetime import datetime, UTC
from typing import Annotated

from PIL import UnidentifiedImageError
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from src.config import settings
from src.customer import crud
from src.customer.image_utils import process_image, delete_image
from src.customer.schemas import (
    CustomerPrivate,
    CustomerCreate,
    Token,
    CustomerPublic,
    CustomerUpdate,
    Refresh,
    Profile,
    ProfileCreate,
    ProfileUpdate,
)
from src.customer.security.auth import CurrentCustomer
from src.customer.security.dependencies import get_jwt_auth_manager
from src.customer.security.secutity import verify_password
from src.customer.security.token_manager import JWTAuthManager
from src.models.dependencies import get_db

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerPrivate, status_code=status.HTTP_201_CREATED)
async def create_customer(customer: CustomerCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    existing_customer = await crud.get_customer_by_username(db=db, username=customer.username)
    if existing_customer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    existing_email = await crud.get_customer_by_email(db=db, email=customer.email)
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return await crud.create_customer(db=db, customer=customer)


@router.post("/login/", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: JWTAuthManager = Depends(get_jwt_auth_manager),
):
    customer = await crud.get_customer_by_email(db=db, email=form_data.username)
    if not customer or not verify_password(form_data.password, customer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    await crud.delete_expired_refresh_tokens(db, customer.id)
    jwt_refresh_token = jwt_manager.create_refresh_token({"sub": str(customer.id)})
    try:
        await crud.create_refresh_token(
            db=db,
            customer_id=customer.id,
            token=jwt_refresh_token,
            days_valid=settings.refresh_token_expire_days,
        )
        await crud.cleanup_old_refresh_tokens(db=db, customer_id=customer.id, keep_latest=5)
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


@router.post("/refresh/", response_model=Token)
async def refresh_tokens(
    payload: Refresh,
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: JWTAuthManager = Depends(get_jwt_auth_manager),
):
    refresh_token = payload.refresh_token
    customer_id = jwt_manager.decode_refresh_token(refresh_token)
    if not customer_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    db_token = await crud.get_refresh_token(db=db, token=refresh_token)
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )
    if db_token.expires_at < datetime.now(UTC):
        await crud.delete_refresh_token(db=db, token=refresh_token)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    await crud.delete_refresh_token(db=db, token=refresh_token)
    new_access_token = jwt_manager.create_access_token({"sub": str(customer_id)})
    new_refresh_token = jwt_manager.create_refresh_token({"sub": str(customer_id)})
    await crud.create_refresh_token(
        db=db,
        customer_id=int(customer_id),
        token=new_refresh_token,
        days_valid=settings.refresh_token_expire_days,
    )
    return Token(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer")


@router.post("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: Refresh, current_customer: CurrentCustomer, db: Annotated[AsyncSession, Depends(get_db)]):
    db_token = await crud.get_refresh_token(db=db, token=payload.refresh_token)
    if db_token and db_token.customer_id == current_customer.id:
        await crud.delete_refresh_token(db=db, token=payload.refresh_token)


@router.get("/me/", response_model=CustomerPrivate)
async def get_current_customer(current_customer: CurrentCustomer):
    return current_customer


@router.get("/{customer_id}/", response_model=CustomerPublic)
async def get_customer(customer_id: int, db: Annotated[AsyncSession, Depends(get_db)], _: CurrentCustomer):
    customer = await crud.get_customer_by_id(db=db, customer_id=customer_id)
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
    customer = await crud.get_customer_by_id(db=db, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    if customer_update.username and customer_update.username.lower() != customer.username.lower():
        existing = await crud.get_customer_by_username(db=db, username=customer_update.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
    if customer_update.email and customer_update.email.lower() != customer.email:
        existing = await crud.get_customer_by_email(db=db, email=customer_update.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    return await crud.update_customer(db=db, customer=customer, customer_update=customer_update)


@router.delete("/{customer_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    current_customer: CurrentCustomer,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if customer_id != current_customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this customer",
        )
    customer = await crud.get_customer_by_id(db=db, customer_id=customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    await crud.delete_customer(db=db, customer=customer)


@router.patch("/{customer_id}/picture/", response_model=CustomerPrivate)
async def upload_customer_picture(
    customer_id: int,
    file: UploadFile,
    current_customer: CurrentCustomer,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if current_customer.id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this customer's picture",
        )
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.max_upload_size_bytes // (1024 * 1024)}MB",
        )
    try:
        new_filename = await run_in_threadpool(process_image, content)
    except UnidentifiedImageError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file. Please upload a valid image (JPEG, PNG, GIF, WebP).",
        ) from err
    old_filename = current_customer.image_file
    current_customer.image_file = new_filename
    await db.commit()
    await db.refresh(current_customer)
    if old_filename:
        delete_image(old_filename)
    return current_customer


@router.delete("/{customer_id}/picture/", response_model=CustomerPrivate)
async def delete_customer_picture(
    customer_id: int,
    current_customer: CurrentCustomer,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if current_customer.id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this customer's picture",
        )
    old_filename = current_customer.image_file
    if old_filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No picture to delete",
        )
    current_customer.image_file = None
    await db.commit()
    await db.refresh(current_customer)
    delete_image(old_filename)
    return current_customer


@router.get("/me/profile/", response_model=Profile)
async def get_my_profile(
    current_customer: CurrentCustomer,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    profile = await crud.get_profile_by_customer_id(db=db, customer_id=current_customer.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.post("/me/profile/", response_model=Profile, status_code=status.HTTP_201_CREATED)
async def create_my_profile(
    data: ProfileCreate,
    current_customer: CurrentCustomer,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    existing = await crud.get_profile_by_customer_id(db=db, customer_id=current_customer.id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already exists")
    return await crud.create_profile(db=db, customer_id=current_customer.id, data=data)


@router.patch("/me/profile/", response_model=Profile)
async def update_my_profile(
    data: ProfileUpdate,
    current_customer: CurrentCustomer,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    profile = await crud.get_profile_by_customer_id(db=db, customer_id=current_customer.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return await crud.update_profile(db=db, profile=profile, data=data)


@router.delete("/me/profile/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_profile(
    current_customer: CurrentCustomer,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    profile = await crud.get_profile_by_customer_id(db=db, customer_id=current_customer.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    await crud.delete_profile(db=db, profile=profile)
