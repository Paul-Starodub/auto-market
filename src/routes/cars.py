from typing import Annotated

from PIL import UnidentifiedImageError
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from src.core.config import settings
from src.crud import cars_crud
from src.database import get_db
from src.schemas import Car, CarCreate, CarUpdate, CarImage, CarImagesDelete
from src.security.auth import get_current_customer
from src.services.image_utils import process_image

MAX_FILE_SIZE = settings.max_upload_size_bytes

router = APIRouter(prefix="/cars", tags=["cars"], dependencies=[Depends(get_current_customer)])


@router.get("/", response_model=list[Car])  # TODO pagination
async def list_cars(db: Annotated[AsyncSession, Depends(get_db)]):
    return await cars_crud.list_cars(db)


@router.get("/{car_id}/", response_model=Car)
async def get_car(car_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    car = await cars_crud.get_car_by_id(db, car_id)
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    return car


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Car,
)
async def create_car(car_create: CarCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await cars_crud.create_car(db=db, car_create=car_create)


@router.patch("/{car_id}/", response_model=Car)
async def update_car(
    car_id: int,
    car_update: CarUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    updated_car = await cars_crud.update_car(db, car_id, car_update)
    if not updated_car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    return updated_car


@router.post("/{car_id}/images/", response_model=list[CarImage])
async def upload_car_images(
    car_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    files: Annotated[list[UploadFile], File(description="Multiple files as UploadFile")],
):
    car = await cars_crud.get_car_by_id(db, car_id)
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
    images = await cars_crud.add_car_images(db, car_id, saved_file_paths)
    return images


@router.get("/{car_id}/images/", response_model=list[CarImage])
async def list_car_images(
    car_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    images = await cars_crud.get_car_images_by_car_id(db, car_id)
    return images


@router.delete("/{car_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(
    car_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    car = await cars_crud.delete_car(db, car_id)
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")


@router.delete("/{car_id}/images/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car_images(
    car_id: int,
    payload: CarImagesDelete,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    deleted_count = await cars_crud.delete_car_images(db, payload.image_ids, car_id)
    if deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No images found to delete")
