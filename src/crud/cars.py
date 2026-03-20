from pathlib import Path

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src import database
from src.schemas import CarCreate, CarUpdate


async def get_car_by_id(db: AsyncSession, car_id: int):
    result = await db.execute(
        select(database.Car)
        .options(joinedload(database.Car.images), joinedload(database.Car.category))
        .where(database.Car.id == car_id)
    )
    return result.scalars().first()


async def get_cars_count(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(database.Car))
    return result.scalar() or 0


async def list_cars(db: AsyncSession, skip: int, limit: int):
    result = await db.execute(
        select(database.Car)
        .order_by(database.Car.id.desc())
        .options(joinedload(database.Car.images), joinedload(database.Car.category))
        .offset(skip)
        .limit(limit)
    )
    return result.unique().scalars().all()


async def create_car(db: AsyncSession, car_create: CarCreate):
    new_car = database.Car(**car_create.model_dump())
    db.add(new_car)
    await db.commit()
    await db.refresh(new_car, attribute_names=["category"])
    return new_car


async def add_car_images(db: AsyncSession, car_id: int, file_paths: list[str]):
    images = [database.CarImage(file_path=path, car_id=car_id) for path in file_paths]
    db.add_all(images)
    await db.commit()
    return images


async def get_car_images_by_car_id(db: AsyncSession, car_id: int):
    result = await db.execute(select(database.CarImage).where(database.CarImage.car_id == car_id))
    return result.scalars().all()


async def update_car(db: AsyncSession, car_id: int, car_update: CarUpdate):
    car = await get_car_by_id(db, car_id)
    if not car:
        return None
    data = car_update.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(car, key, value)
    await db.commit()
    await db.refresh(car, attribute_names=["category"])
    return car


async def delete_car(db: AsyncSession, car_id: int):
    car = await get_car_by_id(db, car_id)
    if not car:
        return None
    result = await db.execute(select(database.CarImage).where(database.CarImage.car_id == car_id))
    images = result.scalars().all()
    for image in images:
        filepath = Path(image.file_path)
        if filepath.exists():
            filepath.unlink()
    await db.execute(delete(database.CarImage).where(database.CarImage.car_id == car_id))
    await db.delete(car)
    await db.commit()
    return car


async def delete_car_images(db: AsyncSession, image_ids: list[int], car_id: int):
    result = await db.execute(
        select(database.CarImage).where(database.CarImage.id.in_(image_ids), database.CarImage.car_id == car_id)
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
