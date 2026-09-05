import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "LikhLo AI"
    app_tagline: str = "Bhaiya, Likh Lo! - Voice-First AI Khata & Ledger Copilot"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Storage & Database (ACID SQLite WAL)
    data_dir: Path = Field(default_factory=lambda: Path(os.path.expanduser("~")) / ".likhlo_ai")
    database_filename: str = "likhlo_khata.db"
    
    # Merchant Defaults
    default_merchant_name: str = "Apka Kirana Store"
    default_merchant_upi: str = "merchant@okhdfcbank"
    
    # OpenAI Model Parameters
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4o-mini"
    whisper_model: str = "whisper-1"
    
    # Audio Limits
    max_audio_size_mb: int = 10
    max_audio_duration_seconds: int = 60
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

    @property
    def database_url(self) -> str:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        db_path = self.data_dir / self.database_filename
        return f"sqlite:///{db_path}"


settings = Settings()
