from datetime import date
from decimal import Decimal
from enum import StrEnum, auto
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLAlchemyEnum, ForeignKey, UniqueConstraint
from sqlalchemy import String, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.customer import Customer


class CarTypeEnum(StrEnum):
    PASSENGER = auto()
    MOTO = auto()
    TRUCK = auto()


class FuelTypeEnum(StrEnum):
    PETROL = auto()
    DIESEL = auto()
    ELECTRIC = auto()
    GAS = auto()
    HYBRID = auto()


class TransmissionTypeEnum(StrEnum):
    MANUAL = auto()
    AUTOMATIC = auto()
    TIPTRONIC = auto()
    ROBOT = auto()
    CVT = auto()
    REDUCER = auto()


class CustomerCar(Base):
    __tablename__ = "customers_cars"
    __table_args__ = (UniqueConstraint("customer_id", "car_id", name="idx_unique_customer_car"),)

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"))
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"))
    offer: Mapped[Decimal] = mapped_column(DECIMAL(15, 2))

    customer: Mapped["Customer"] = relationship(back_populates="cars")
    car: Mapped["Car"] = relationship(back_populates="customers")


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(20), unique=True)

    cars: Mapped[list["Car"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"Genre(id={self.id}, name={self.name})"


class Car(Base):
    brand: Mapped[str] = mapped_column(String(30))
    model: Mapped[str] = mapped_column(String(50))
    car_type: Mapped[CarTypeEnum | None] = mapped_column(SQLAlchemyEnum(CarTypeEnum, name="car_type_enum"))
    fuel_type: Mapped[FuelTypeEnum | None] = mapped_column(SQLAlchemyEnum(FuelTypeEnum, name="fuel_type_enum"))
    transmission_type: Mapped[TransmissionTypeEnum | None] = mapped_column(
        SQLAlchemyEnum(TransmissionTypeEnum, name="transmission_type_enum")
    )
    start_year: Mapped[date]
    end_year: Mapped[date]
    costs: Mapped[Decimal] = mapped_column(DECIMAL(15, 2))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    category: Mapped[Category | None] = relationship(back_populates="cars")
    customers: Mapped[list["CustomerCar"]] = relationship(back_populates="car", cascade="all, delete-orphan")
    images: Mapped[list["CarImage"]] = relationship(back_populates="car", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Car(brand={self.brand}, model={self.model}, car_type={self.car_type}, fuel_type={self.fuel_type}, transmission_type={self.transmission_type}, start_year={self.start_year}, end_year={self.end_year}, costs={self.costs})"


class CarImage(Base):
    __tablename__ = "car_images"

    file_path: Mapped[str] = mapped_column(String(255))
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"), index=True)

    car: Mapped["Car"] = relationship(back_populates="images")

    def __repr__(self) -> str:
        return f"CarImage(id={self.id}, file_path={self.file_path})"
