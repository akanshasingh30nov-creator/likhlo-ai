import logging
from typing import Optional, Dict
from likhlo_ai.schema import ExtractedTransaction
from likhlo_ai.config import settings
from likhlo_ai.parser.heuristic import parse_spoken_text_heuristically
from likhlo_ai.parser.providers import (
    BaseLLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    GenericOpenAICompatibleProvider
)

logger = logging.getLogger(__name__)


class UnifiedParser:
    """Universal Multi-Provider Parser for LikhLo AI.
    
    Supports:
    - ⚡ Offline Rule Engine (Deterministic Heuristics, 0ms, Free)
    - 🟣 Anthropic Claude (Claude 3.5 Haiku, Sonnet)
    - 🟢 OpenAI (GPT-4o-mini, GPT-4o)
    - 🦙 Hermes / Ollama / Groq / OpenRouter (OpenAI-compatible)
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.default_provider = provider or settings.ai_provider
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self._providers: Dict[str, BaseLLMProvider] = {}
        self._init_providers()

    def _init_providers(self):
        """Initialize available providers based on configuration."""
        # 1. OpenAI
        openai_key = self.api_key if self.default_provider == "openai" else settings.openai_api_key
        if openai_key:
            self._providers["openai"] = OpenAIProvider(api_key=openai_key)

        # 2. Anthropic Claude
        anthropic_key = self.api_key if self.default_provider == "anthropic" else settings.anthropic_api_key
        if anthropic_key:
            self._providers["anthropic"] = AnthropicProvider(api_key=anthropic_key, model=self.model)

        # 3. Hermes / Ollama / OpenRouter / Custom
        custom_base = self.api_base or settings.custom_api_base
        if custom_base or self.default_provider in ("hermes", "ollama", "openrouter", "custom"):
            self._providers["hermes"] = GenericOpenAICompatibleProvider(
                base_url=custom_base,
                api_key=self.api_key or settings.custom_api_key,
                model=self.model or settings.custom_model_name
            )

    def get_provider(
        self,
        name: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None
    ) -> Optional[BaseLLMProvider]:
        """Resolve requested provider or fallback to configured active provider."""
        provider_name = (name or self.default_provider or "auto").lower()

        if provider_name in ("offline", "none", "heuristic"):
            return None

        # Ad-hoc provider initialization if custom parameters provided
        if api_key or api_base or model:
            if provider_name == "anthropic":
                return AnthropicProvider(api_key=api_key or settings.anthropic_api_key, model=model)
            elif provider_name in ("hermes", "ollama", "openrouter", "custom"):
                return GenericOpenAICompatibleProvider(base_url=api_base, api_key=api_key, model=model)
            elif provider_name == "openai":
                return OpenAIProvider(api_key=api_key or settings.openai_api_key, model=model)

        if provider_name in self._providers:
            return self._providers[provider_name]

        # Auto detection: pick first available cloud provider
        if provider_name == "auto":
            if "anthropic" in self._providers:
                return self._providers["anthropic"]
            if "openai" in self._providers:
                return self._providers["openai"]
            if "hermes" in self._providers:
                return self._providers["hermes"]

        return None

    def parse(
        self,
        transcript: str,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None
    ) -> ExtractedTransaction:
        """Parse spoken transcript using selected AI provider with graceful offline fallback."""
        cleaned_transcript = transcript.strip()
        if not cleaned_transcript:
            raise ValueError("Transcript cannot be empty")

        active_provider = self.get_provider(
            name=provider,
            api_key=api_key,
            api_base=api_base,
            model=model
        )

        if active_provider:
            try:
                result = active_provider.parse(cleaned_transcript)
                if result:
                    return result
                logger.info(f"{active_provider.provider_name} returned empty, falling back to heuristic engine")
            except Exception as e:
                logger.warning(f"{active_provider.provider_name} failed: {e}. Falling back to heuristic engine")

        # Zero-downtime offline fallback
        return parse_spoken_text_heuristically(cleaned_transcript)
