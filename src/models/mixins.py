from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import declared_attr, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.models.customer import Customer


class CustomerRelationMixin:
    """Mixin for a one-to-one relationship with a Customer (for example, Profile)."""

    _customer_id_unique: bool = False
    _customer_back_populate: str | None = None
    _customer_id_nullable: bool = False

    @declared_attr
    def customer_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("customers.id"), unique=cls._customer_id_unique, nullable=cls._customer_id_nullable
        )

    @declared_attr
    def customer(cls) -> Mapped["Customer"]:
        return relationship("Customer", back_populates=cls._customer_back_populate)
