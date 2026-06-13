"""AI provider abstraction.

Services depend on :class:`IAIProvider`, not on any concrete provider. Each
provider knows the single cheapest authenticated request that proves a key works.
The ``httpx.AsyncClient`` is injected (never constructed here) so the whole layer
is unit-testable with ``httpx.MockTransport`` and no network.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import httpx

from ...core.exceptions import UnauthorizedError, UpstreamError


class IAIProvider(ABC):
    """A configurable AI backend the user brings their own key for."""

    #: Stable identifier used in the registry and stored on the config.
    name: str

    @abstractmethod
    async def validate(self, model: str, api_key: str, client: httpx.AsyncClient) -> None:
        """Confirm the API key works. Raise an :class:`AppError` on failure.

        Note: this validates the **API key only** (via the provider's list/key
        endpoint). The ``model`` name is not verified here — an unknown model is
        accepted at save time and would only surface when inference is attempted.
        """


def _raise_for_status(response: httpx.Response, provider: str) -> None:
    status = response.status_code
    if 200 <= status < 300:
        return
    if status in (401, 403):
        raise UnauthorizedError(f"{provider} rejected the API key.")
    if status == 429:
        raise UpstreamError(f"{provider} is rate limiting requests. Try again shortly.")
    raise UpstreamError(f"{provider} validation failed (HTTP {status}).")


async def validate_via_get(
    client: httpx.AsyncClient,
    url: str,
    *,
    provider: str,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
) -> None:
    """Issue an authenticated GET and map the outcome to domain exceptions.

    Never logs ``headers`` or ``params`` — they carry the API key.
    """
    try:
        response = await client.get(url, headers=headers, params=params)
    except httpx.RequestError as exc:
        raise UpstreamError(f"Could not reach {provider}.") from exc
    _raise_for_status(response, provider)
