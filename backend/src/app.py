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
from .repositories.user_repository import UserRepository
from .routes import health_router, user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open the DB connection on startup, close it on shutdown."""
    database = get_database()
    database.connect()
    # Ensure indexes (e.g. unique email) exist.
    await UserRepository(database.db).ensure_indexes()
    try:
        yield
    finally:
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
    return app


app = create_app()
