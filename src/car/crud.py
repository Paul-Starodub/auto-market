from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.car.schemas import CarCreate


async def get_car_by_id(db: AsyncSession, car_id: int):
    result = await db.execute(select(models.Car).where(models.Car.id == car_id))
    return result.scalars().first()


# async def get_car_by_id(db: AsyncSession, car_id: int):  # TODO for future
#     result = await db.execute(
#         select(models.Car)
#         .options(
#             selectinload(models.Car.images),
#             selectinload(models.Car.category),
#         )
#         .where(models.Car.id == car_id)
#     )
#     return result.scalars().first()


async def create_car(db: AsyncSession, car_create: CarCreate):
    new_car = models.Car(**car_create.model_dump())
    db.add(new_car)
    await db.commit()
    await db.refresh(new_car)
    return new_car


async def add_car_images(db: AsyncSession, car_id: int, file_paths: list[str]):
    images = [models.CarImage(file_path=path, car_id=car_id) for path in file_paths]
    db.add_all(images)
    await db.commit()
    return images
