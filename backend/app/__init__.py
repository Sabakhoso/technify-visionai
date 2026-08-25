"""
Technify VisionAI — Backend Application Package.

AI-powered video surveillance and security intelligence platform.

Architecture:
    FastAPI (async API layer)
    Supabase (Postgres database, Auth, Storage)
    SQLAlchemy (async ORM) + Alembic (migrations)
    Google Colab (model training/experimentation — weights deployed separately)
    Edge AI Gateway (YOLO detection, ByteTrack tracking, PPE/ANPR/fire-smoke models)

Package layout:
    app/core          -> config, database, security, logging
    app/api            -> versioned API routers and endpoints
    app/models          -> SQLAlchemy ORM models (database tables)
    app/schemas         -> Pydantic request/response schemas
    app/crud            -> database access layer (create/read/update/delete)
    app/services        -> business logic (event engine, alerts, AI search, evidence)
    app/ml              -> inference client, model registry (talks to Edge AI Gateway)
    app/integrations    -> Supabase client, storage client, notification channels
    app/websockets      -> live event streaming to the dashboard
    app/utils           -> shared helper functions
"""

__version__ = "0.1.0"
__title__ = "Technify VisionAI"