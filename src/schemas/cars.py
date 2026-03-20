from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator, Field

from src.database.models.cars import CarTypeEnum, FuelTypeEnum, TransmissionTypeEnum
from src.database.validators.cars import current_year
from src.schemas.categories import PaginatedBaseResponse


class YearsValidationMixin(BaseModel):
    @model_validator(mode="after")
    def check_years(self):
        if self.start_year is not None and self.end_year is not None and self.start_year > self.end_year:
            raise ValueError("start_year must be <= end_year")
        return self


class CarCategory(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class CarBase(YearsValidationMixin, BaseModel):
    brand: str = Field(..., min_length=1, max_length=30)
    model: str = Field(..., min_length=1, max_length=50)
    car_type: CarTypeEnum | None = None
    fuel_type: FuelTypeEnum | None = None
    transmission_type: TransmissionTypeEnum | None = None
    start_year: int = Field(..., ge=1886, le=current_year())
    end_year: int = Field(..., ge=1886, le=current_year())
    cost: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2, description="Car price")
    category_id: int | None = Field(default=None, gt=0, description="Category ID")


class CarCreate(CarBase):
    pass


class CarUpdate(YearsValidationMixin, BaseModel):
    brand: str | None = None
    model: str | None = None
    car_type: CarTypeEnum | None = None
    fuel_type: FuelTypeEnum | None = None
    transmission_type: TransmissionTypeEnum | None = None
    start_year: int | None = None
    end_year: int | None = None
    cost: Decimal | None = None
    category_id: int | None = None


class Car(BaseModel):
    id: int
    brand: str = Field(..., min_length=1, max_length=30)
    model: str = Field(..., min_length=1, max_length=50)
    car_type: CarTypeEnum | None = None
    fuel_type: FuelTypeEnum | None = None
    transmission_type: TransmissionTypeEnum | None = None
    start_year: int = Field(..., ge=1886, le=datetime.now().year)
    end_year: int = Field(..., ge=1886, le=datetime.now().year)
    cost: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2, description="Car price")

    model_config = ConfigDict(from_attributes=True)


class CarFull(Car):
    category: CarCategory | None = None


class CarImageBase(BaseModel):
    file_path: str = Field(..., min_length=1, max_length=255)
    car_id: int


class CarImageCreate(CarImageBase):
    pass


class CarImageUpdate(CarImageCreate):
    pass


class CarImage(BaseModel):
    id: int
    file_path: str = Field(..., min_length=1, max_length=255)

    model_config = ConfigDict(from_attributes=True)


class CarImagesDelete(BaseModel):
    image_ids: list[int]


class PaginatedCarResponse(PaginatedBaseResponse):
    cars: list[Car]
