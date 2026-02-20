"""
TenderAI Uygulama Ayarları / Application Settings.

Pydantic BaseSettings kullanarak tüm konfigürasyonu yönetir.
Manages all configuration using Pydantic BaseSettings.
Ortam değişkenlerini .env dosyasından okur.
Reads environment variables from .env file.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Proje kök dizini / Project root directory
BASE_DIR: Path = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    TenderAI uygulama ayarları / Application settings.

    Tüm ayarlar .env dosyasından veya ortam değişkenlerinden okunur.
    All settings are read from .env file or environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # === OpenAI Ayarları / OpenAI Settings ===
    OPENAI_API_KEY: str = "sk-your-key-here"
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.1

    # === Gemini API ===
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # === Veritabanı / Database ===
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'tenderai.db'}"

    # === Güvenlik / Security ===
    SECRET_KEY: str = "your-secret-key-here"

    # === Uygulama / Application ===
    APP_NAME: str = "TenderAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # === Demo Modu / Demo Mode ===
    DEMO_MODE: bool = False

    # === Dosya Yükleme / File Upload ===
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list[str] = [".pdf"]

    # === Logging ===
    LOG_LEVEL: str = "INFO"

    @property
    def upload_dir_path(self) -> Path:
        """Upload dizinini oluştur ve döndür / Create and return upload directory."""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        return self.UPLOAD_DIR

    @property
    def is_demo(self) -> bool:
        """Demo modunda mı / Is in demo mode."""
        return self.DEMO_MODE


# Global settings instance
settings = Settings()
