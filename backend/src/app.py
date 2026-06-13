"""Application entry point.

Creates the FastAPI app, manages the database lifecycle, registers routers, and
maps domain errors to HTTP responses. Run with:

    uvicorn src.app:app --reload
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config.database import get_database
from .config.settings import get_settings
from .core.exceptions import AppError
from .dependencies.container import close_http_client
from .repositories.ai_config_repository import AIConfigRepository
from .repositories.repository_repository import RepositoryRepository
from .repositories.user_repository import UserRepository
from .routes import ai_config_router, health_router, repository_router, user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open the DB connection on startup, close it (and the HTTP client) on shutdown."""
    database = get_database()
    database.connect()
    # Ensure indexes (e.g. unique email, one config/repo per user) exist.
    await UserRepository(database.db).ensure_indexes()
    await AIConfigRepository(database.db).ensure_indexes()
    await RepositoryRepository(database.db).ensure_indexes()
    try:
        yield
    finally:
        await close_http_client()
        database.disconnect()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    # CORS — the frontend (Vite) runs on a different origin in development.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    app.include_router(health_router)
    app.include_router(user_router)
    app.include_router(ai_config_router)
    app.include_router(repository_router)
    return app


app = create_app()
