from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.car import Category


async def get_categories_count(db: AsyncSession) -> int:
    result = await db.execute(select(func.count()).select_from(Category))
    return result.scalar() or 0


async def get_categories(db: AsyncSession, skip: int, limit: int) -> list[Category]:
    stmt = select(Category).order_by(Category.name).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_category(db: AsyncSession, category_id: int) -> Category | None:
    return await db.get(Category, category_id)
