from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.customer import crud
from src.customer.schemas import CustomerPrivate, CustomerCreate
from src.models.dependencies import get_db

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerPrivate, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    existing_user = await crud.get_customer_by_username(
        db=db, username=customer.username
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    existing_email = await crud.get_customer_by_email(db=db, email=customer.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    return await crud.create_customer(db=db, customer=customer)
