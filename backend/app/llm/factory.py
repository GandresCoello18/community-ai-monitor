from app.core.config import Settings
from app.llm.base import LLMProvider
from app.llm.ollama import OllamaProvider


def create_llm_provider(settings: Settings) -> LLMProvider:
    """Build the configured LLM provider.

    Only Ollama is implemented for now; the factory keeps the provider
    swappable (OpenAI, local Llama, etc.) without touching services.
    """
    if settings.llm_provider == "ollama":
        return OllamaProvider(
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
            temperature=settings.llm_temperature,
        )

    msg = f"Unsupported LLM provider: {settings.llm_provider}"
    raise ValueError(msg)
