from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.car.schemas import CarCreate


async def get_car_by_id(db: AsyncSession, car_id: int):
    result = await db.execute(select(models.Car).where(models.Car.id == car_id))
    return result.scalars().first()


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


async def get_car_images_by_car_id(db: AsyncSession, car_id: int):
    result = await db.execute(select(models.CarImage).where(models.CarImage.car_id == car_id))
    return result.scalars().all()


async def delete_car_images(db: AsyncSession, image_ids: list[int], car_id: int):
    result = await db.execute(
        select(models.CarImage).where(models.CarImage.id.in_(image_ids), models.CarImage.car_id == car_id)
    )
    images = result.scalars().all()
    for image in images:
        filepath = Path(image.file_path)
        if filepath.exists():
            filepath.unlink()
    for image in images:
        await db.delete(image)
    await db.commit()
    return len(images)
