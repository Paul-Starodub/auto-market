from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import settings

engine = create_async_engine(settings.db.DATABASE_URL, echo=settings.db.ECHO)

# Prevent attribute expiration on commit to avoid async lazy-loads in response serialization.
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
