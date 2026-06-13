"""AI-config business logic.

Validates the user's key against the chosen provider **before** persisting it
(validate-then-encrypt-then-store), so an invalid key is never saved. Depends on
abstractions: the repository interface, an injected httpx client, and the
provider registry.
"""
from __future__ import annotations

import httpx

from ..core.crypto import encrypt_secret, mask_hint
from ..core.utils import utcnow
from ..models.ai_config_model import AIConfigModel
from ..providers.ai.registry import get_provider
from ..repositories.interfaces.iai_config_repository import IAIConfigRepository
from ..schemas.ai_config_schema import AIConfigResponse, AIConfigSaveRequest


class AIConfigService:
    def __init__(
        self,
        repository: IAIConfigRepository,
        http_client: httpx.AsyncClient,
        encryption_key: str,
    ) -> None:
        self._repo = repository
        self._http = http_client
        self._encryption_key = encryption_key

    async def get_status(self, user_id: str) -> AIConfigResponse:
        config = await self._repo.find_by_user_id(user_id)
        if config is None:
            return AIConfigResponse.not_configured()
        return AIConfigResponse.from_model(config)

    async def save(self, user_id: str, payload: AIConfigSaveRequest) -> AIConfigResponse:
        # 1. Validate live — raises UnauthorizedError/UpstreamError on failure,
        #    so nothing below runs and nothing is persisted.
        provider = get_provider(payload.provider)
        await provider.validate(payload.model, payload.api_key, self._http)

        # 2. Encrypt and persist.
        now = utcnow()
        config = AIConfigModel(
            user_id=user_id,
            provider=payload.provider,
            model=payload.model,
            api_key_encrypted=encrypt_secret(payload.api_key, self._encryption_key),
            key_hint=mask_hint(payload.api_key),
            created_at=now,
            updated_at=now,
        )
        saved = await self._repo.upsert(config)
        return AIConfigResponse.from_model(saved)
