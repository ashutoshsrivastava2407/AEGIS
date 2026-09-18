"""PostgreSQL Async Engine and Session Management."""

from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from packages.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.AEGIS_ENV == "development",
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync engine for synchronous session dependency
from packages.database.base import Base
import packages.database.models  # Ensure all models are registered

sync_db_url = "sqlite:///./aegis_data.db"
sync_engine = create_engine(
    sync_db_url,
    connect_args={"check_same_thread": False},
    echo=False
)
Base.metadata.create_all(bind=sync_engine)
SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_db() -> Generator[Session, None, None]:
    """Synchronous DB session generator dependency for FastAPI."""
    import packages.database.models  # Ensure all ORM models are registered in Base.metadata
    Base.metadata.create_all(bind=sync_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

