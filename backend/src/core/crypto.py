"""Symmetric encryption for secrets at rest (BYO API keys / GitHub tokens).

Isolated here (like core/security.py) so the algorithm can change in one place.
The Fernet key is passed in as an argument rather than read from settings — this
keeps the module pure and trivially testable, and avoids coupling to the
``@lru_cache``d settings singleton.
"""
from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken


def _fernet(key: str) -> Fernet:
    return Fernet(key.encode("utf-8"))


def encrypt_secret(plaintext: str, key: str) -> str:
    """Encrypt a secret, returning a URL-safe base64 token."""
    return _fernet(key).encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_secret(token: str, key: str) -> str:
    """Decrypt a token produced by :func:`encrypt_secret`."""
    try:
        return _fernet(key).decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:  # pragma: no cover - corrupted/rotated key
        raise ValueError("Could not decrypt secret (invalid token or key).") from exc


def mask_hint(plaintext: str) -> str:
    """A non-reversible display hint, e.g. ``••••a1b2`` — safe to return to clients."""
    if len(plaintext) <= 4:
        return "••••"
    return f"••••{plaintext[-4:]}"
