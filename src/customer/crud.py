from datetime import datetime, UTC
from sqlalchemy import select, func, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.customer.image_utils import delete_image
from src.customer.schemas import CustomerCreate, CustomerUpdate
from src.customer.security.secutity import hash_password


async def get_customer_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.Customer).where(func.lower(models.Customer.username) == username.lower()))
    return result.scalars().first()


async def get_customer_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.Customer).where(models.Customer.email == email.lower()))
    return result.scalars().first()


async def create_customer(db: AsyncSession, customer: CustomerCreate):
    new_customer = models.Customer(
        username=customer.username,
        email=customer.email.lower(),
        password_hash=hash_password(customer.password),
    )
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    return new_customer


async def create_refresh_token(db: AsyncSession, customer_id: int, token: str, days_valid: int):
    refresh_token = models.RefreshTokenModel.create(customer_id=customer_id, token=token, days_valid=days_valid)
    db.add(refresh_token)
    await db.commit()


async def get_refresh_token(db: AsyncSession, token: str):
    result = await db.execute(select(models.RefreshTokenModel).where(models.RefreshTokenModel.token == token))
    return result.scalars().first()


async def delete_refresh_token(db: AsyncSession, token: str):
    await db.execute(delete(models.RefreshTokenModel).where(models.RefreshTokenModel.token == token))
    await db.commit()


async def delete_expired_refresh_tokens(db: AsyncSession, customer_id: int):
    await db.execute(
        delete(models.RefreshTokenModel).where(
            models.RefreshTokenModel.customer_id == customer_id,
            models.RefreshTokenModel.expires_at < datetime.now(UTC),
        )
    )
    await db.commit()


async def cleanup_old_refresh_tokens(db: AsyncSession, customer_id: int, keep_latest: int = 5):
    """Keep only N most recent refresh tokens per customer to prevent token accumulation"""
    result = await db.execute(
        select(models.RefreshTokenModel)
        .where(models.RefreshTokenModel.customer_id == customer_id)
        .order_by(desc(models.RefreshTokenModel.id))
    )
    tokens = result.scalars().all()
    if len(tokens) > keep_latest:
        tokens_to_delete = tokens[keep_latest:]
        for token in tokens_to_delete:
            await db.delete(token)
        await db.commit()


async def get_customer_by_id(db: AsyncSession, customer_id: int):
    result = await db.execute(select(models.Customer).where(models.Customer.id == customer_id))
    return result.scalars().first()


async def update_customer(db: AsyncSession, customer, customer_update: CustomerUpdate):
    if customer_update.username is not None:
        customer.username = customer_update.username
    if customer_update.email is not None:
        customer.email = customer_update.email.lower()
    await db.commit()
    await db.refresh(customer)
    return customer


async def delete_customer(db: AsyncSession, customer):
    await db.execute(delete(models.RefreshTokenModel).where(models.RefreshTokenModel.customer_id == customer.id))
    old_filename = customer.image_file
    await db.delete(customer)
    await db.commit()
    if old_filename:
        delete_image(old_filename)


async def get_profile_by_customer_id(db: AsyncSession, customer_id: int):
    result = await db.execute(select(models.Profile).where(models.Profile.customer_id == customer_id))
    return result.scalars().first()


async def create_profile(db: AsyncSession, customer_id: int, data):
    profile = models.Profile(customer_id=customer_id, **data.model_dump())
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def update_profile(db: AsyncSession, profile, data):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await db.commit()
    await db.refresh(profile)
    return profile


async def delete_profile(db: AsyncSession, profile):
    await db.delete(profile)
    await db.commit()
