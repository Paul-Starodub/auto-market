from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src import schemas
from src.database import Category


async def get_categories_count(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Category))
    return result.scalar() or 0


async def get_categories(db: AsyncSession, skip: int, limit: int) -> list[Category]:
    stmt = select(Category).order_by(Category.name).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_category(db: AsyncSession, category_id: int) -> Category | None:
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


async def create_category(db: AsyncSession, category_create: schemas.CategoryCreateSchema) -> Category:
    stmt = select(Category).where(Category.name == category_create.name)
    result = await db.execute(stmt)
    existing_category = result.scalar_one_or_none()
    if existing_category:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category with this name already exists")
    category = Category(**category_create.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession, category_id: int, category_update: schemas.CategoryCreateSchema
) -> Category:
    category = await get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if category.name != category_update.name:
        stmt = select(Category).where(Category.name == category_update.name)
        result = await db.execute(stmt)
        existing_category = result.scalar_one_or_none()
        if existing_category:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category with this name already exists")
    category.name = category_update.name
    db.add(category)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists",
        )
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: int) -> None:
    category = await get_category(db, category_id)
    await db.delete(category)
    await db.commit()
