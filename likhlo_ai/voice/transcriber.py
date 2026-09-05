import logging
from typing import Optional
from likhlo_ai.config import settings
from likhlo_ai.voice.audio_utils import validate_audio_file

logger = logging.getLogger(__name__)

RETAIL_PROMPT = (
    "LikhLo AI, Bhaiya Likh Lo, Khata, Udhaar, Atta, Dal, Chawal, Doodh, Cheeni, Tel, Chai, Biscuits, "
    "Sabun, Sharma ji, Ramesh bhaiya, Gupta ji, Suresh, UPI, Rupaye, Baki hai, Cash diya, "
    "Mandi kharcha, Vasooli, Jama karaya, Somvaar, Mangalvaar"
)


class WhisperTranscriber:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client for Whisper: {e}")
                self.client = None

    def transcribe(self, file_path: str, custom_prompt: Optional[str] = None) -> str:
        """Transcribe an audio file using OpenAI Whisper or local simulation."""
        validate_audio_file(file_path)

        if self.client:
            try:
                with open(file_path, "rb") as audio_file:
                    prompt = custom_prompt or RETAIL_PROMPT
                    transcription = self.client.audio.transcriptions.create(
                        model=settings.whisper_model,
                        file=audio_file,
                        prompt=prompt,
                        language="hi"
                    )
                    return transcription.text
            except Exception as e:
                logger.error(f"Whisper API transcription failed: {e}. Falling back to simulation.")

        return self._simulate(file_path)

    def _simulate(self, file_path: str) -> str:
        """Deterministic simulation for offline local testing."""
        return "Sharma ji ko 5kg atta aur 2 packet doodh udhaar diya, 280 rupaye baki hai, somvaar ko denge"
