"""
Technify VisionAI — Application Entrypoint

Run locally:

    uvicorn app.main:app --reload

Run in production:

    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import __version__
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import (
    check_database_connection,
    dispose_engine,
    get_db_context,
)
from app.services.camera_monitor import check_all_cameras


# --------------------------------------------------------------------------
# Logging setup
# --------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO if settings.is_production else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("technify_visionai")


# --------------------------------------------------------------------------
# Lifespan — startup and shutdown hooks
# --------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---------------- Startup ----------------

    logger.info(
        f"Starting {settings.PROJECT_NAME} "
        f"[{settings.ENVIRONMENT}]"
    )

    # Check database connection
    db_ok = await check_database_connection()

    if db_ok:
        logger.info("✅ Database connection verified.")
    else:
        logger.error(
            "❌ Database connection FAILED at startup — "
            "check DATABASE_URL in .env"
        )

    # ------------------------------------------------------------------
    # Camera health monitor
    # ------------------------------------------------------------------

    async def camera_monitor_loop():
        """
        Periodically check all active cameras and update their
        health status in the database.
        """

        interval_seconds = 30

        logger.info(
            f"Camera health monitor interval: "
            f"{interval_seconds} seconds."
        )

        while True:
            try:
                async with get_db_context() as db:
                    await check_all_cameras(db)

                logger.debug(
                    "Camera health check completed successfully."
                )

            except asyncio.CancelledError:
                logger.info(
                    "Camera health monitor cancellation requested."
                )
                raise

            except Exception:
                logger.exception(
                    "Unexpected error during camera health check."
                )

            await asyncio.sleep(interval_seconds)

    # Start monitor in background
    camera_monitor_task = asyncio.create_task(
        camera_monitor_loop()
    )

    logger.info(
        "✅ Camera health monitor started."
    )

    try:
        yield

    finally:
        # ---------------- Shutdown ----------------

        logger.info(
            "Shutting down camera health monitor."
        )

        camera_monitor_task.cancel()

        try:
            await camera_monitor_task

        except asyncio.CancelledError:
            logger.info(
                "Camera health monitor stopped."
            )

        logger.info(
            "Shutting down — disposing database engine."
        )

        await dispose_engine()


# --------------------------------------------------------------------------
# FastAPI application
# --------------------------------------------------------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=__version__,
    description=(
        "AI-powered video surveillance and "
        "security intelligence platform."
    ),
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url=(
        "/openapi.json"
        if not settings.is_production
        else None
    ),
    lifespan=lifespan,
)


# --------------------------------------------------------------------------
# CORS
# --------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------
# Exception handlers
# --------------------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    """
    Handles HTTP exceptions such as:
    401, 403, 404, etc.
    """

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """
    Handles Pydantic/FastAPI validation errors.
    """

    logger.warning(
        f"Validation error on "
        f"{request.method} {request.url.path}: "
        f"{exc.errors()}"
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Handles unexpected server errors.

    Full error is logged server-side.
    """

    logger.exception(
        f"Unhandled exception on "
        f"{request.method} {request.url.path}: {exc}"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": (
                "Internal server error."
                if settings.is_production
                else str(exc)
            )
        },
    )


# --------------------------------------------------------------------------
# Root endpoint
# --------------------------------------------------------------------------

@app.get("/", tags=["Root"])
async def root():
    """
    Basic API information.
    """

    return {
        "project": settings.PROJECT_NAME,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": (
            "/docs"
            if not settings.is_production
            else "disabled in production"
        ),
    }


# --------------------------------------------------------------------------
# Health endpoint
# --------------------------------------------------------------------------

@app.get("/health", tags=["Root"])
async def health():
    """
    Health check.

    Verifies both:
    - API process
    - Database connection
    """

    db_ok = await check_database_connection()

    status_code = (
        status.HTTP_200_OK
        if db_ok
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "status": (
                "healthy"
                if db_ok
                else "unhealthy"
            ),
            "database": (
                "connected"
                if db_ok
                else "disconnected"
            ),
            "environment": settings.ENVIRONMENT,
        },
    )


# --------------------------------------------------------------------------
# API v1 routers
# --------------------------------------------------------------------------

#
# IMPORTANT:
# app must be created BEFORE include_router().
#

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


# --------------------------------------------------------------------------
# Application startup message
# --------------------------------------------------------------------------

logger.info(
    "Technify VisionAI application configured successfully."
)