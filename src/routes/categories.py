from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.database import get_db
from src.crud import categories_crud
from src.schemas import PaginatedCategoryResponseSchema, CategorySchema, CategoryCreateSchema, CategoryUpdateSchema
from src.security.auth import get_current_customer, http_bearer

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    dependencies=[
        Depends(get_current_customer),
        Depends(http_bearer),  # optional case to see a form for token in swagger
    ],
)


@router.get("/", response_model=PaginatedCategoryResponseSchema)
async def get_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = settings.entities_per_page,
):
    total = await categories_crud.get_categories_count(db)
    categories = await categories_crud.get_categories(db=db, skip=skip, limit=limit)
    has_more = skip + len(categories) < total
    return PaginatedCategoryResponseSchema(
        categories=[CategorySchema.model_validate(cat) for cat in categories],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@router.get("/{category_id}/", response_model=CategorySchema)
async def get_category(db: Annotated[AsyncSession, Depends(get_db)], category_id: int):
    return await categories_crud.get_category(db=db, category_id=category_id)


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_create: CategoryCreateSchema,
):
    return await categories_crud.create_category(db=db, category_create=category_create)


@router.put("/{category_id}/", response_model=CategorySchema)
async def update_category(
    db: Annotated[AsyncSession, Depends(get_db)], category_id: int, category_update: CategoryUpdateSchema
):
    return await categories_crud.update_category(db=db, category_id=category_id, category_update=category_update)


@router.delete("/{category_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(db: Annotated[AsyncSession, Depends(get_db)], category_id: int):
    await categories_crud.delete_category(db=db, category_id=category_id)
