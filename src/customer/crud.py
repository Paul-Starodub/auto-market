from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.customer.schemas import CustomerCreate
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
