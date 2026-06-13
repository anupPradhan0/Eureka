"""Domain-level exceptions.

Services raise these instead of HTTP errors, keeping business logic free of any
web-framework concern. The HTTP layer (controllers / an exception handler) maps
them to status codes.
"""
from __future__ import annotations


class AppError(Exception):
    """Base class for all application errors. Carries an HTTP status hint."""

    status_code: int = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    status_code = 422


class UnauthorizedError(AppError):
    status_code = 401


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class UpstreamError(AppError):
    """A third-party service (AI provider, GitHub) failed or was unreachable."""

    status_code = 502


class ServiceUnavailableError(AppError):
    status_code = 503
