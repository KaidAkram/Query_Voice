"""
Core Configuration
===================
Application settings loaded from environment variables.
"""

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Application configuration — loaded from environment variables."""

    # App
    APP_NAME: str = "QueryVoice"
    DEBUG: bool = field(default_factory=lambda: os.getenv("DEBUG", "true").lower() == "true")

    # Database — PostgreSQL
    POSTGRES_HOST: str = field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    POSTGRES_PORT: int = field(default_factory=lambda: int(os.getenv("POSTGRES_PORT", "5432")))
    POSTGRES_USER: str = field(default_factory=lambda: os.getenv("POSTGRES_USER", "queryvoice"))
    POSTGRES_PASSWORD: str = field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", "queryvoice"))
    POSTGRES_DB: str = field(default_factory=lambda: os.getenv("POSTGRES_DB", "queryvoice_db"))

    # ChromaDB
    CHROMA_HOST: str = field(default_factory=lambda: os.getenv("CHROMA_HOST", "localhost"))
    CHROMA_PORT: int = field(default_factory=lambda: int(os.getenv("CHROMA_PORT", "8001")))

    # Models
    WHISPER_MODEL: str = field(default_factory=lambda: os.getenv("WHISPER_MODEL", "openai/whisper-base"))
    TEXT2SQL_MODEL: str = field(default_factory=lambda: os.getenv("TEXT2SQL_MODEL", "t5-base"))

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def async_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
