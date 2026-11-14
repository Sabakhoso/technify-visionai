"""
Database engine and session management.

Supports both asyncpg (for Supabase PostgreSQL) and aiosqlite (for local development/offline).
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class every ORM model inherits from."""
    pass


def _build_engine() -> AsyncEngine:
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite"):
        return create_async_engine(
            db_url,
            echo=False,
            connect_args={"check_same_thread": False},
            future=True,
        )

    return create_async_engine(
        db_url,
        echo=settings.is_development,
        poolclass=NullPool,
        pool_pre_ping=True,
        connect_args={
            "server_settings": {"jit": "off"},
            "statement_cache_size": 0,
        },
        future=True,
    )


engine: AsyncEngine = _build_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_connection() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def init_models() -> None:
    try:
        # Import all models to ensure they are registered with Base.metadata
        import app.models  # noqa: F401
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.warning(f"Model initialization error: {e}")


async def dispose_engine() -> None:
    await engine.dispose()
    logger.info("Database engine disposed.")
