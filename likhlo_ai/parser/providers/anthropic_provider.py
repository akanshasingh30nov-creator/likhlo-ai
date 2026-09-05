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

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider for Claude 3.5 Haiku and Sonnet."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.anthropic_model

    @property
    def provider_name(self) -> str:
        return f"Anthropic Claude ({self.model})"

    def parse(self, transcript: str) -> Optional[ExtractedTransaction]:
        if not self.api_key:
            return None

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "system": SYSTEM_INSTRUCTION,
            "messages": [
                {"role": "user", "content": f"Parse this voice note and output strictly valid JSON: \"{transcript}\""}
            ]
        }

        try:
            with httpx.Client(timeout=14.0) as client:
                response = client.post(ANTHROPIC_API_URL, headers=headers, json=payload)
                if response.status_code != 200:
                    logger.error(f"Anthropic API returned error {response.status_code}: {response.text}")
                    return None

                data = response.json()
                content_blocks = data.get("content", [])
                text_response = ""
                for block in content_blocks:
                    if block.get("type") == "text":
                        text_response += block.get("text", "")

                json_dict = clean_json_response(text_response)
                if json_dict:
                    return dict_to_extracted_transaction(json_dict, raw_transcript=transcript)
        except Exception as e:
            logger.error(f"Anthropic Claude parsing error: {e}")
            return None

        return None
