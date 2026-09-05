import logging
import httpx
from typing import Optional
from likhlo_ai.schema import ExtractedTransaction
from likhlo_ai.config import settings
from likhlo_ai.parser.providers.base import (
    BaseLLMProvider,
    SYSTEM_INSTRUCTION,
    clean_json_response,
    dict_to_extracted_transaction
)

logger = logging.getLogger(__name__)


class GenericOpenAICompatibleProvider(BaseLLMProvider):
    """Universal provider for Nous Hermes, Ollama, Groq, OpenRouter, and local LLMs."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.base_url = (base_url or settings.custom_api_base or "http://localhost:11434/v1").rstrip("/")
        self.api_key = api_key or settings.custom_api_key or "local"
        self.model = model or settings.custom_model_name or "hermes3"

    @property
    def provider_name(self) -> str:
        return f"OpenAI-Compatible ({self.model} @ {self.base_url})"

    def parse(self, transcript: str) -> Optional[ExtractedTransaction]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": f"Parse this voice note and output strictly valid JSON: \"{transcript}\""}
            ]
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(url, headers=headers, json=payload)
                if response.status_code != 200:
                    logger.warning(f"Provider {self.base_url} returned {response.status_code}: {response.text[:200]}")
                    return None

                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    return None

                raw_content = choices[0].get("message", {}).get("content", "")
                json_dict = clean_json_response(raw_content)
                if json_dict:
                    return dict_to_extracted_transaction(json_dict, raw_transcript=transcript)
        except Exception as e:
            logger.warning(f"Error connecting to OpenAI-compatible provider at {self.base_url}: {e}")
            return None

        return None
