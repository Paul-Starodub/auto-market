from pydantic import BaseModel, ConfigDict
from datetime import date
from decimal import Decimal
from typing import Optional

from src.category.schemas import Category
from src.models.car import CarTypeEnum, FuelTypeEnum, TransmissionTypeEnum


class CarBase(BaseModel):
    brand: str
    model: str
    car_type: Optional[CarTypeEnum] = None
    fuel_type: Optional[FuelTypeEnum] = None
    transmission_type: Optional[TransmissionTypeEnum] = None
    start_year: date
    end_year: date
    costs: Decimal
    category_id: Optional[int] = None


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    car_type: Optional[CarTypeEnum] = None
    fuel_type: Optional[FuelTypeEnum] = None
    transmission_type: Optional[TransmissionTypeEnum] = None
    start_year: Optional[date] = None
    end_year: Optional[date] = None
    costs: Optional[Decimal] = None
    category_id: Optional[int] = None


class Car(BaseModel):
    id: int
    brand: str
    model: str
    car_type: Optional[CarTypeEnum] = None
    fuel_type: Optional[FuelTypeEnum] = None
    transmission_type: Optional[TransmissionTypeEnum] = None
    start_year: date
    end_year: date
    costs: Decimal
    category: Optional[Category]

    model_config = ConfigDict(from_attributes=True)
