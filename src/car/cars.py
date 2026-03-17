from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.car import crud
from src.car.schemas import CarCreate, CarImageCreate
from src.models.dependencies import get_db

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post("/")
async def create_car(
    car_create: CarCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    return await crud.create_car(db=db, car_create=car_create)


@router.post("{car_id}/images/")  # TODO
async def create_car_image(
    car_id: int,
    car_image_create: CarImageCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await crud.create_car_image(db=db, car_image_create=car_image_create)
