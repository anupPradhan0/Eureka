"""Security primitives: password hashing and JWT creation/verification.

Isolated here so hashing/token algorithms can change in one place without
touching business logic (DRY + single responsibility).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from ..config.settings import get_settings

# bcrypt only considers the first 72 bytes of a password; encoding once here
# keeps hashing and verification consistent and avoids length errors.
_BCRYPT_MAX_BYTES = 72


def _encode(plain_password: str) -> bytes:
    return plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash for the given plaintext password."""
    return bcrypt.hashpw(_encode(plain_password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored hash."""
    try:
        return bcrypt.checkpw(_encode(plain_password), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """Create a signed JWT for the given subject (typically the user id)."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expires_minutes),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and verify a JWT. Returns the claims, or None if invalid/expired."""
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
