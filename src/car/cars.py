from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.car import crud
from src.car.schemas import CarCreate, CarImage
from src.customer.image_utils import process_image
from src.models.dependencies import get_db

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post("/")
async def create_car(car_create: CarCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await crud.create_car(db=db, car_create=car_create)


@router.post("/{car_id}/images", response_model=list[CarImage])
async def upload_car_images(
    car_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    files: list[UploadFile] = File(...),
):
    car = await crud.get_car_by_id(db, car_id)
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    file_paths = []
    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only images allowed")
        content = await file.read()
        filename = process_image(content)
        file_path = f"media/pics/{filename}"
        file_paths.append(file_path)
    images = await crud.add_car_images(db, car_id, file_paths)
    return images
