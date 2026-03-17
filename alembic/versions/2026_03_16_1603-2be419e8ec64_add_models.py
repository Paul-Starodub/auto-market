"""add models

Revision ID: 2be419e8ec64
Revises:
Create Date: 2026-03-16 16:03:29.197315

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2be419e8ec64"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "categories",
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)
    op.create_table(
        "customers",
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=200), nullable=False),
        sa.Column("image_file", sa.String(length=200), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_customers_id"), "customers", ["id"], unique=False)
    op.create_table(
        "cars",
        sa.Column("brand", sa.String(length=30), nullable=False),
        sa.Column("model", sa.String(length=50), nullable=False),
        sa.Column("car_type", sa.Enum("PASSENGER", "MOTO", "TRUCK", name="car_type_enum"), nullable=True),
        sa.Column(
            "fuel_type", sa.Enum("PETROL", "DIESEL", "ELECTRIC", "GAS", "HYBRID", name="fuel_type_enum"), nullable=True
        ),
        sa.Column(
            "transmission_type",
            sa.Enum("MANUAL", "AUTOMATIC", "TIPTRONIC", "ROBOT", "CVT", "REDUCER", name="transmission_type_enum"),
            nullable=True,
        ),
        sa.Column("start_year", sa.Integer(), nullable=False),
        sa.Column("end_year", sa.Integer(), nullable=False),
        sa.Column("cost", sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cars_category_id"), "cars", ["category_id"], unique=False)
    op.create_index(op.f("ix_cars_id"), "cars", ["id"], unique=False)
    op.create_table(
        "profiles",
        sa.Column("first_name", sa.String(length=40), nullable=True),
        sa.Column("last_name", sa.String(length=40), nullable=True),
        sa.Column("bio", sa.String(), nullable=True),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("customer_id"),
    )
    op.create_index(op.f("ix_profiles_id"), "profiles", ["id"], unique=False)
    op.create_table(
        "refresh_tokens",
        sa.Column("token", sa.String(length=512), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index(op.f("ix_refresh_tokens_id"), "refresh_tokens", ["id"], unique=False)
    op.create_table(
        "car_images",
        sa.Column("file_path", sa.String(length=255), nullable=False),
        sa.Column("car_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["car_id"], ["cars.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_car_images_car_id"), "car_images", ["car_id"], unique=False)
    op.create_index(op.f("ix_car_images_id"), "car_images", ["id"], unique=False)
    op.create_table(
        "customers_cars",
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("car_id", sa.Integer(), nullable=False),
        sa.Column("offer", sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["car_id"], ["cars.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("customer_id", "car_id", name="idx_unique_customer_car"),
    )
    op.create_index(op.f("ix_customers_cars_id"), "customers_cars", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_customers_cars_id"), table_name="customers_cars")
    op.drop_table("customers_cars")
    op.drop_index(op.f("ix_car_images_id"), table_name="car_images")
    op.drop_index(op.f("ix_car_images_car_id"), table_name="car_images")
    op.drop_table("car_images")
    op.drop_index(op.f("ix_refresh_tokens_id"), table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_index(op.f("ix_profiles_id"), table_name="profiles")
    op.drop_table("profiles")
    op.drop_index(op.f("ix_cars_id"), table_name="cars")
    op.drop_index(op.f("ix_cars_category_id"), table_name="cars")
    op.drop_table("cars")
    op.drop_index(op.f("ix_customers_id"), table_name="customers")
    op.drop_table("customers")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")
