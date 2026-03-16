from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from src.customer import validators
from src.customer.utils import generate_secure_token
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
    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/pics/{self.image_file}"
        return "/static/customer_pics/default.jpg"

    @validates("email")
    def validate_email(self, key, value) -> str:
        return validators.validate_email(value.lower())

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


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(
        String(512), unique=True, nullable=False, default=generate_secure_token
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(days=1),
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE")
    )

    customer: Mapped[Customer] = relationship(back_populates="refresh_tokens")

    @classmethod
    def create(
        cls, customer_id: int | Mapped[int], days_valid: int, token: str
    ) -> "RefreshTokenModel":
        """
        Factory method to create a new RefreshTokenModel instance.

        This method simplifies the creation of a new refresh token by calculating
        the expiration date based on the provided number of valid days and setting
        the required attributes.
        """
        expires_at = datetime.now(timezone.utc) + timedelta(days=days_valid)
        return cls(customer_id=customer_id, expires_at=expires_at, token=token)

    def __repr__(self) -> str:
        return f"<RefreshTokenModel(id={self.id}, token={self.token}, expires_at={self.expires_at})>"
