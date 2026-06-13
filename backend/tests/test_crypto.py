"""Unit tests for the secret-encryption helpers."""
from __future__ import annotations

from cryptography.fernet import Fernet

from src.core.crypto import decrypt_secret, encrypt_secret, mask_hint


def test_encrypt_decrypt_roundtrip():
    key = Fernet.generate_key().decode()
    secret = "sk-super-secret-1234"

    token = encrypt_secret(secret, key)

    assert token != secret
    assert decrypt_secret(token, key) == secret


def test_encryption_is_nondeterministic():
    key = Fernet.generate_key().decode()
    assert encrypt_secret("same", key) != encrypt_secret("same", key)


def test_mask_hint_shows_only_last_four():
    assert mask_hint("sk-1234abcd") == "••••abcd"


def test_mask_hint_hides_short_secrets():
    assert mask_hint("abcd") == "••••"
    assert mask_hint("xy") == "••••"
