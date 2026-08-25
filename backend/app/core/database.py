"""
Database engine and session management.

Uses SQLAlchemy's async engine against Supabase's Postgres (via the
transaction pooler, port 6543). Connection pool settings here are tuned
specifically for pgbouncer-style poolers like Supabase's — NullPool is
used because Supabase already manages pooling on its side; layering
SQLAlchemy's own connection pool on top of an external pooler causes
connection exhaustion and "prepared statement already exists" errors
with asyncpg in transaction pooling mode.
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
    """
    Builds the async SQLAlchemy engine.

    NullPool is deliberate: Supabase's transaction pooler (pgbouncer)
    already handles connection pooling server-side. Running SQLAlchemy's
    own pool on top of it leads to stale/broken connections and
    "prepared statement does not exist" errors under asyncpg, because
    pgbouncer in transaction mode doesn't guarantee the same underlying
    connection persists between statements.
    """
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.is_development,       # log SQL only in dev, never in prod
        poolclass=NullPool,
        pool_pre_ping=True,                  # detect dead connections before using them
        connect_args={
            "server_settings": {"jit": "off"},   # avoids odd query planning on pgbouncer
            "statement_cache_size": 0,           # required for asyncpg + pgbouncer transaction mode
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
    """
    FastAPI dependency — yields a database session per request and
    guarantees it's closed afterward, with rollback on error.

    Usage in an endpoint:
        @router.get("/cameras")
        async def list_cameras(db: AsyncSession = Depends(get_db)):
            ...
    """
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
    """
    Session context manager for use OUTSIDE of FastAPI request handling —
    e.g. in scripts, background jobs, the event engine, or Colab-triggered
    retraining callbacks that write results back to the DB.

    Usage:
        async with get_db_context() as db:
            result = await db.execute(...)
    """
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
    """
    Lightweight health check — used by /health endpoint and startup checks.
    Returns True if the DB is reachable, False otherwise. Never raises.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def init_models() -> None:
    """
    Creates tables from SQLAlchemy models if they don't exist.

    NOTE: This is only for local development convenience/quick prototyping.
    In staging/production, schema changes must go through Alembic
    migrations (alembic revision --autogenerate / alembic upgrade head),
    never through this function — it doesn't track schema history and
    will silently skip altering existing tables.
    """
    if settings.is_production:
        logger.warning("init_models() called in production — skipping. Use Alembic migrations instead.")
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (development mode).")


async def dispose_engine() -> None:
    """
    Cleanly closes all database connections. Call this on FastAPI shutdown
    (see main.py lifespan handler) to avoid leaking connections when the
    app restarts or scales down.
    """
    await engine.dispose()
    logger.info("Database engine disposed.")