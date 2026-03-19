from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator, Field

from src.database.models.cars import CarTypeEnum, FuelTypeEnum, TransmissionTypeEnum
from src.schemas.categories import PaginatedBaseResponse


class CarCategory(BaseModel):
    id: int
    name: str


class CarBase(BaseModel):
    brand: str = Field(..., min_length=1, max_length=30)
    model: str = Field(..., min_length=1, max_length=50)
    car_type: CarTypeEnum | None = None
    fuel_type: FuelTypeEnum | None = None
    transmission_type: TransmissionTypeEnum | None = None
    start_year: int = Field(..., ge=1886, le=datetime.now().year)
    end_year: int = Field(..., ge=1886, le=datetime.now().year)
    cost: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2, description="Car price")
    category_id: int | None = Field(default=None, gt=0, description="Category ID")

    @model_validator(mode="before")
    def check_years(cls, values):
        start = values.get("start_year")
        end = values.get("end_year")
        if start is not None and end is not None and start > end:
            raise ValueError("start_year must be less than or equal to end_year")
        return values


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
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
