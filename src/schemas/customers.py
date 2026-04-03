from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.database.validators.customers import validate_password_strength


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshSchema(BaseModel):
    refresh_token: str


class CustomerBaseSchema(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class CustomerCreateSchema(CustomerBaseSchema):
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value) -> str:
        return validate_password_strength(value)


class CustomerPublicSchema(BaseModel):
    id: int
    username: str
    image_file: str | None
    image_path: str

    model_config = ConfigDict(from_attributes=True)


class CustomerPrivateSchema(CustomerPublicSchema):
    email: EmailStr


class CustomerUpdateSchema(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)


class ProfileBaseSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None


class ProfileCreateSchema(ProfileBaseSchema):
    pass


class ProfileUpdateSchema(ProfileBaseSchema):
    pass


class ProfileSchema(ProfileBaseSchema):
    id: int
    customer_id: int

    model_config = ConfigDict(from_attributes=True)


class ForgotPasswordRequestSchema(BaseModel):
    email: EmailStr = Field(max_length=120)


class ResetPasswordRequestSchema(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class ChangePasswordRequestSchema(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
