__all__ = (
    "cars_router",
    "categories_router",
    "customers_router",
)


from .cars import router as cars_router
from .categories import router as categories_router
from .customers import router as customers_router
