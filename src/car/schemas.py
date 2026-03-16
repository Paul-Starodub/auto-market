from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

from src.category.schemas import Category
from src.models.car import CarTypeEnum, FuelTypeEnum, TransmissionTypeEnum


class CarBase(BaseModel):
    brand: str
    model: str
    car_type: Optional[CarTypeEnum] = None
    fuel_type: Optional[FuelTypeEnum] = None
    transmission_type: Optional[TransmissionTypeEnum] = None
    start_year: int
    end_year: int
    cost: Decimal
    category_id: Optional[int] = None

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
    brand: Optional[str] = None
    model: Optional[str] = None
    car_type: Optional[CarTypeEnum] = None
    fuel_type: Optional[FuelTypeEnum] = None
    transmission_type: Optional[TransmissionTypeEnum] = None
    start_year: int
    end_year: int
    cost: Decimal
    category_id: Optional[int] = None


class Car(BaseModel):
    id: int
    brand: str
    model: str
    car_type: Optional[CarTypeEnum] = None
    fuel_type: Optional[FuelTypeEnum] = None
    transmission_type: Optional[TransmissionTypeEnum] = None
    start_year: int
    end_year: int
    cost: Decimal
    category: Optional[Category]

    model_config = ConfigDict(from_attributes=True)
