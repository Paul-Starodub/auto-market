from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.mixins import CustomerRelationMixin

if TYPE_CHECKING:
    from src.models.car import CustomerCar


class Customer(Base):
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    image_file: Mapped[str | None] = mapped_column(
        String(200), nullable=True, default=None
    )

    profile: Mapped["Profile"] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )
    cars: Mapped[list["CustomerCar"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/customer_pics/{self.image_file}"
        return "/static/customer_pics/default.jpg"

    def __repr__(self) -> str:
        return f"User(username={self.username}, email={self.email}, password_hash={self.password_hash}, image_file={self.image_file})"


class Profile(CustomerRelationMixin, Base):
    _customer_id_unique = True  # for a one-to-one relationship
    _customer_back_populate = "profile"

    first_name: Mapped[str | None] = mapped_column(String(40))
    last_name: Mapped[str | None] = mapped_column(String(40))
    bio: Mapped[str | None]

    def __repr__(self) -> str:
        return f"Profile(id={self.id}, first_name={self.first_name}, last_name={self.last_name})"
