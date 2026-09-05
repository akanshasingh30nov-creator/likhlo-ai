# Backwards-compatible import wrapper for OpenAIProvider
from likhlo_ai.parser.providers.openai_provider import OpenAIProvider as LLMParser
from likhlo_ai.parser.providers.base import SYSTEM_INSTRUCTION

__all__ = ["LLMParser", "SYSTEM_INSTRUCTION"]
