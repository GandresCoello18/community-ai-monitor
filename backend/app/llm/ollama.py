import logging

import httpx

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class LLMProviderError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(code="LLM_PROVIDER_ERROR", message=message, status_code=503)


class OllamaProvider:
    """LLM provider backed by a local Ollama server (open models, no API key)."""

    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        timeout_seconds: float = 120.0,
        temperature: float = 0.3,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout_seconds
        self._temperature = temperature

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(self, prompt: str) -> str:
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self._temperature},
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Ollama returned HTTP %s for model %s",
                exc.response.status_code,
                self._model,
            )
            raise LLMProviderError(
                "Language model request failed",
            ) from exc
        except httpx.HTTPError as exc:
            logger.error("Ollama unreachable at %s: %s", self._base_url, exc)
            raise LLMProviderError(
                "Language model service is not available",
            ) from exc

        text = str(data.get("response", "")).strip()
        if not text:
            raise LLMProviderError("Language model returned an empty response")
        return text

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self._base_url}/api/version")
                return response.status_code == 200
        except httpx.HTTPError:
            return False
