"""
Technify VisionAI — Application Entrypoint

Run locally with:
    uvicorn app.main:app --reload

Run in production with:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app import __version__

from app.core.config import settings
from app.core.database import check_database_connection, dispose_engine

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
    # ---- Startup ----
    logger.info(f"Starting {settings.PROJECT_NAME} [{settings.ENVIRONMENT}]")

    db_ok = await check_database_connection()
    if db_ok:
        logger.info("✅ Database connection verified.")
    else:
        logger.error("❌ Database connection FAILED at startup — check DATABASE_URL in .env")

    yield

    # ---- Shutdown ----
    logger.info("Shutting down — disposing database engine.")
    await dispose_engine()


# --------------------------------------------------------------------------
# App instance
# --------------------------------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=__version__,
    description="AI-powered video surveillance and security intelligence platform.",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
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
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handles raised HTTPExceptions (404, 401, 403, etc.) with a consistent shape."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic/FastAPI request validation errors (bad request bodies, missing fields)."""
    logger.warning(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catches anything unhandled so clients never see raw Python tracebacks.
    Full error is always logged server-side regardless of environment.
    """
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error." if settings.is_production else str(exc)},
    )


# --------------------------------------------------------------------------
# Root & health endpoints
# --------------------------------------------------------------------------
@app.get("/", tags=["Root"])
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if not settings.is_production else "disabled in production",
    }


@app.get("/health", tags=["Root"])
async def health():
    """
    Health check for uptime monitoring / load balancers.
    Verifies both the API process AND the database are reachable.
    """
    db_ok = await check_database_connection()
    status_code = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if db_ok else "unhealthy",
            "database": "connected" if db_ok else "disconnected",
            "environment": settings.ENVIRONMENT,
        },
    )


# --------------------------------------------------------------------------
# API routers
# --------------------------------------------------------------------------
# Enable once app/api/v1/router.py has real endpoint routers registered
# (starting with the cameras endpoint we build next).
#
# from app.api.v1.router import api_router
# app.include_router(api_router, prefix=settings.API_V1_PREFIX)