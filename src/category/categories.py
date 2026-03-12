from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.category import crud, schemas
from src.category.schemas import PaginatedCategoryResponse, Category
from src.config import settings
from src.models.dependencies import get_db

router = APIRouter(prefix="/categories", tags=["Categories"])


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
async def get_category(db: Annotated[AsyncSession, Depends(get_db)], category_id: int):
    category = await crud.get_category(db=db, category_id=category_id)
    if category is not None:
        return category
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
