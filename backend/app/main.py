"""
Technify VisionAI — Application Entrypoint

Run locally:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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
    init_models,
)
from app.services.camera_monitor import check_all_cameras
from app.websockets.live_events import ws_router

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
        f"Starting {settings.PROJECT_NAME} [{settings.ENVIRONMENT}]"
    )

    # Initialize database tables
    try:
        await init_models()
    except Exception as e:
        logger.warning(f"Model init warning: {e}")

    # Check database connection
    db_ok = await check_database_connection()
    if db_ok:
        logger.info("✅ Database connection verified.")
    else:
        logger.warning("⚠️ Database connection check failed — running in fallback mode.")

    # ------------------------------------------------------------------
    # Camera health monitor
    # ------------------------------------------------------------------
    async def camera_monitor_loop():
        interval_seconds = 30
        logger.info(f"Camera health monitor running every {interval_seconds}s.")

        while True:
            try:
                async with get_db_context() as db:
                    await check_all_cameras(db)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"Camera health monitor tick: {e}")

            await asyncio.sleep(interval_seconds)

    camera_monitor_task = asyncio.create_task(camera_monitor_loop())

    try:
        yield
    finally:
        camera_monitor_task.cancel()
        try:
            await camera_monitor_task
        except asyncio.CancelledError:
            pass

        await dispose_engine()


# --------------------------------------------------------------------------
# FastAPI application
# --------------------------------------------------------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=__version__,
    description="AI-powered video surveillance and security intelligence platform.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# --------------------------------------------------------------------------
# CORS
# --------------------------------------------------------------------------

allowed_origins = list({
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    *settings.cors_origins_list,
})

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------
# Exception handlers
# --------------------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


# --------------------------------------------------------------------------
# Root & Health endpoints
# --------------------------------------------------------------------------

@app.get("/", tags=["Root"])
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


@app.get("/health", tags=["Root"])
async def health():
    db_ok = await check_database_connection()
    return JSONResponse(
        status_code=status.HTTP_200_OK if db_ok else status.HTTP_200_OK,
        content={
            "status": "healthy" if db_ok else "running",
            "database": "connected" if db_ok else "disconnected",
            "environment": settings.ENVIRONMENT,
        },
    )


# --------------------------------------------------------------------------
# Mount API routers & Root WebSocket router
# --------------------------------------------------------------------------

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(ws_router)
