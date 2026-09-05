import logging
from typing import Optional
from likhlo_ai.schema import ExtractedTransaction
from likhlo_ai.config import settings
from likhlo_ai.parser.providers.base import BaseLLMProvider, SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Structured Outputs provider using GPT-4o-mini."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.client = None

    @property
    def provider_name(self) -> str:
        return "OpenAI (GPT-4o-mini)"

    def parse(self, transcript: str) -> Optional[ExtractedTransaction]:
        if not self.client:
            return None

        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": f"Parse this voice note: \"{transcript}\""}
                ],
                response_format=ExtractedTransaction,
                timeout=12.0
            )
            parsed = response.choices[0].message.parsed
            if parsed:
                parsed.raw_transcript = transcript
                return parsed
        except Exception as e:
            logger.error(f"OpenAI parsing error: {e}")
            return None

        return None
