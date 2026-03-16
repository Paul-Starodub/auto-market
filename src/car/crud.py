from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.car.schemas import CarCreate


async def create_car(db: AsyncSession, car_create: CarCreate):
    new_car = models.Car(**car_create.model_dump())
    db.add(new_car)
    await db.commit()
    await db.refresh(new_car)
    return new_car
