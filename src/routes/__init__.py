from fastapi import APIRouter

from .cars import router as cars_router
from .categories import router as categories_router
from .customers import router as customers_router

src_router = APIRouter()

src_router.include_router(customers_router)
src_router.include_router(cars_router)
src_router.include_router(categories_router)
