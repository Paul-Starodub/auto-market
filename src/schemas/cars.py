from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator

from src.database.models.cars import CarTypeEnum, FuelTypeEnum, TransmissionTypeEnum
from src.schemas import Category


class CarBase(BaseModel):
    brand: str
    model: str
    car_type: CarTypeEnum | None = None
    fuel_type: FuelTypeEnum | None = None
    transmission_type: TransmissionTypeEnum | None = None
    start_year: int
    end_year: int
    cost: Decimal
    category_id: int | None = None

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
    brand: str
    model: str
    car_type: CarTypeEnum | None = None
    fuel_type: FuelTypeEnum | None = None
    transmission_type: TransmissionTypeEnum | None = None
    start_year: int
    end_year: int
    cost: Decimal
    category: Category | None = None

    model_config = ConfigDict(from_attributes=True)


class CarImageBase(BaseModel):
    file_path: str
    car_id: int


class CarImageCreate(CarImageBase):
    pass


class CarImageUpdate(CarImageCreate):
    pass


class CarImage(BaseModel):
    id: int
    file_path: str

    model_config = ConfigDict(from_attributes=True)


class CarImagesDelete(BaseModel):
    image_ids: list[int]
