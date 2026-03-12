from pydantic import BaseModel, ConfigDict


class PaginatedBaseResponse(BaseModel):
    total: int
    skip: int
    limit: int
    has_more: bool


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryCreate):
    pass


class Category(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PaginatedCategoryResponse(PaginatedBaseResponse):
    categories: list[Category]
