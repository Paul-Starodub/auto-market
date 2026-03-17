from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.car.schemas import CarCreate, CarImageCreate


async def create_car(db: AsyncSession, car_create: CarCreate):
    new_car = models.Car(**car_create.model_dump())
    db.add(new_car)
    await db.commit()
    await db.refresh(new_car)
    return new_car


async def create_car_image(
    db: AsyncSession,
    car_image_create: CarImageCreate,
):  # TODO
    new_car_image = models.CarImage(**car_image_create.model_dump())
    db.add(new_car_image)
    await db.commit()
    await db.refresh(new_car_image)
    return new_car_image
