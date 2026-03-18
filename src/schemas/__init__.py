__all__ = (
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerPrivate",
    "CustomerPublic",
    "Profile",
    "ProfileCreate",
    "ProfileUpdate",
    "Token",
    "Refresh",
    "CarCreate",
    "CarUpdate",
    "Car",
    "CarImageCreate",
    "CarImageUpdate",
    "CarImagesDelete",
    "CarImage",
    "CategoryCreate",
    "CategoryUpdate",
    "Category",
    "PaginatedCategoryResponse",
)

from .customers import (
    CustomerCreate,
    CustomerUpdate,
    CustomerPrivate,
    CustomerPublic,
    Profile,
    ProfileCreate,
    ProfileUpdate,
    Token,
    Refresh,
)
from .cars import CarCreate, CarUpdate, Car, CarImageCreate, CarImageUpdate, CarImagesDelete, CarImage
from .categories import CategoryCreate, CategoryUpdate, Category, PaginatedCategoryResponse


from .cars import Car
from .categories import Category

# 🔥 ВАЖНО
Car.model_rebuild()
Category.model_rebuild()
