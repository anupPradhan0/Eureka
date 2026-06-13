"""Small shared utilities used across layers."""
from __future__ import annotations

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Timezone-aware current UTC time. The single source for timestamps."""
    return datetime.now(timezone.utc)
