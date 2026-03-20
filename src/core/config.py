from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent


class EmailConfig(BaseModel):
    HOST: str = "localhost"
    PORT: int = 1025
    HOST_USER: str = ""
    HOST_PASSWORD: str = ""
    USE_TLS: bool = False
    FROM_EMAIL: str = "noreply@automarket.com"


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class APIPrefix(BaseModel):
    prefix: str = "/api"


class DatabaseConfig(BaseModel):
    HOST: str
    PORT: int
    NAME: str
    USER: str
    PASSWORD: str
    ECHO: bool

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    api: APIPrefix = APIPrefix()
    db: DatabaseConfig
    email: EmailConfig = EmailConfig()

    SECRET_KEY_ACCESS: str
    SECRET_KEY_REFRESH: str
    JWT_SIGNING_ALGORITHM: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    max_upload_size_bytes: int = 5 * 1024 * 1024
    entities_per_page: int = 10

    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env.template", BASE_DIR / ".env"),
        env_nested_delimiter="__",
        case_sensitive=False,
    )


settings = Settings()
