from typing import Annotated

from PIL import UnidentifiedImageError
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from src.car import crud
from src.car.schemas import CarCreate, CarImage, CarImagesDelete
from src.config import settings
from src.customer.image_utils import process_image
from src.models.dependencies import get_db

MAX_FILE_SIZE = settings.max_upload_size_bytes

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
    saved_file_paths = []
    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{file.filename} is not an image")
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"{file.filename} exceeds maximum size of {MAX_FILE_SIZE // (1024*1024)} MB",
            )
        try:
            filename = await run_in_threadpool(process_image, content)
        except UnidentifiedImageError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image file: {file.filename}. Please upload a valid image.",
            ) from err
        saved_file_paths.append(f"media/pics/{filename}")
    images = await crud.add_car_images(db, car_id, saved_file_paths)
    return images


@router.get("/{car_id}/images", response_model=list[CarImage])
async def list_car_images(
    car_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    images = await crud.get_car_images_by_car_id(db, car_id)
    return images


@router.delete("/{car_id}/images", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car_images_endpoint(
    car_id: int,
    payload: CarImagesDelete,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    deleted_count = await crud.delete_car_images(db, payload.image_ids, car_id)
    if deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No images found to delete")
