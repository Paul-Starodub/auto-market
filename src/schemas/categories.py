from pydantic import BaseModel, ConfigDict, Field


class PaginatedBaseResponseSchema(BaseModel):
    total: int
    skip: int
    limit: int
    has_more: bool


class CategoryBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)


class CategoryCreateSchema(CategoryBaseSchema):
    pass


class CategoryUpdateSchema(CategoryCreateSchema):
    pass


class CategorySchema(CategoryBaseSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PaginatedCategoryResponseSchema(PaginatedBaseResponseSchema):
    categories: list[CategorySchema]
