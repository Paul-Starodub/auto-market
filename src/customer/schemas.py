from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.customer.validators import validate_password_strength


class CustomerBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class CustomerCreate(CustomerBase):
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value) -> str:
        return validate_password_strength(value)


class CustomerPublic(BaseModel):
    id: int
    username: str
    image_file: str | None
    image_path: str

    model_config = ConfigDict(from_attributes=True)


class CustomerPrivate(CustomerPublic):
    email: EmailStr


class CustomerUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str


class Refresh(BaseModel):
    refresh_token: str
