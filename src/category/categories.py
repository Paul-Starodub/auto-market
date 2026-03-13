from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.category import crud, schemas
from src.category.schemas import PaginatedCategoryResponse, Category
from src.config import settings
from src.models.dependencies import get_db

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=PaginatedCategoryResponse)
async def get_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = settings.posts_per_page,
):
    total = await crud.get_categories_count(db)
    categories = await crud.get_categories(db=db, skip=skip, limit=limit)
    has_more = skip + len(categories) < total
    return PaginatedCategoryResponse(
        categories=[schemas.Category.model_validate(cat) for cat in categories],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@router.get("/{category_id}/", response_model=Category)
async def get_category_route(
    db: Annotated[AsyncSession, Depends(get_db)], category_id: int
):
    return await crud.get_category(db=db, category_id=category_id)


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_create: schemas.CategoryCreate,
):
    return await crud.create_category(db=db, category_create=category_create)


@router.put("/{category_id}/", response_model=Category)
async def update_category(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: int,
    category_update: schemas.CategoryUpdate,
):
    return await crud.update_category(
        db=db, category_id=category_id, category_update=category_update
    )


@router.delete("/{category_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category_route(
    db: Annotated[AsyncSession, Depends(get_db)], category_id: int
):
    await crud.delete_category(db, category_id)
