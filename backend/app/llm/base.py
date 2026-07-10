from typing import Protocol


class LLMProvider(Protocol):
    """Adapter interface for language model providers.

    Implementations must be swappable (Ollama, OpenAI, local Llama) without
    changing the summary generation logic.
    """

    @property
    def provider_name(self) -> str: ...

    @property
    def model_name(self) -> str: ...

    async def generate(self, prompt: str) -> str: ...

    async def is_available(self) -> bool: ...
