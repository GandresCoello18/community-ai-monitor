"""Language model integration layer (FASE 7).

Flow: structured events → prompt → LLM provider → text summary.
The LLM never receives frames, images or personal data.
"""

from app.llm.base import LLMProvider
from app.llm.factory import create_llm_provider
from app.llm.ollama import LLMProviderError, OllamaProvider
from app.llm.prompts import build_summary_prompt
from app.llm.schemas import EventSummaryItem, SummaryContext

__all__ = [
    "EventSummaryItem",
    "LLMProvider",
    "LLMProviderError",
    "OllamaProvider",
    "SummaryContext",
    "build_summary_prompt",
    "create_llm_provider",
]
