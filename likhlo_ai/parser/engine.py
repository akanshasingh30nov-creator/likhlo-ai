import logging
from typing import Optional
from likhlo_ai.schema import ExtractedTransaction
from likhlo_ai.parser.heuristic import parse_spoken_text_heuristically
from likhlo_ai.parser.llm import LLMParser

logger = logging.getLogger(__name__)


class UnifiedParser:
    def __init__(self, api_key: Optional[str] = None):
        self.llm_parser = LLMParser(api_key=api_key)

    def parse(self, transcript: str) -> ExtractedTransaction:
        """Parse spoken transcript using LLM or deterministic fallback."""
        cleaned_transcript = transcript.strip()
        if not cleaned_transcript:
            raise ValueError("Transcript cannot be empty")

        if self.llm_parser.client:
            try:
                result = self.llm_parser.parse(cleaned_transcript)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"LLM parsing failed, using heuristic engine: {e}")

        return parse_spoken_text_heuristically(cleaned_transcript)
