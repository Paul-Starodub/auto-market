from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.customer.schemas import CustomerCreate, CustomerUpdate
from src.customer.security.secutity import hash_password


async def get_customer_by_username(db: AsyncSession, username: str):
    result = await db.execute(
        select(models.Customer).where(
            func.lower(models.Customer.username) == username.lower()
        )
    )
    return result.scalars().first()


async def get_customer_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(models.Customer).where(models.Customer.email == email.lower())
    )
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


async def create_refresh_token(
    db: AsyncSession, customer_id: int, token: str, days_valid: int
):
    refresh_token = models.RefreshTokenModel.create(
        customer_id=customer_id, token=token, days_valid=days_valid
    )
    db.add(refresh_token)
    await db.commit()


async def get_customer_by_id(db: AsyncSession, customer_id: int):
    result = await db.execute(
        select(models.Customer).where(models.Customer.id == customer_id)
    )
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
    await db.execute(
        delete(models.RefreshTokenModel).where(
            models.RefreshTokenModel.customer_id == customer.id
        )
    )
    await db.delete(customer)
    await db.commit()
