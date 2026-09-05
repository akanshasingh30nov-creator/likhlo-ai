import os
from likhlo_ai.config import settings

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".webm"}


def validate_audio_file(file_path: str) -> bool:
    """Validate that audio file exists, has allowed format, and meets size limits."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found at: {file_path}")

    file_size_bytes = os.path.getsize(file_path)
    if file_size_bytes == 0:
        raise ValueError("Audio file is empty (0 bytes)")

    max_bytes = settings.max_audio_size_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise ValueError(
            f"Audio file size exceeds maximum limit of {settings.max_audio_size_mb} MB"
        )

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise ValueError(
            f"Unsupported audio format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
        )

    return True
