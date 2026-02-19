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
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.1

    # === Veritabanı / Database ===
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'tenderai.db'}"

    # === Güvenlik / Security ===
    SECRET_KEY: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # === Uygulama / Application ===
    APP_NAME: str = "TenderAI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # === Dosya Yükleme / File Upload ===
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list[str] = [".pdf"]

    # === Vektör Veritabanı / Vector Database ===
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    @property
    def upload_dir_path(self) -> Path:
        """Upload dizinini oluştur ve döndür / Create and return upload directory."""
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        return self.UPLOAD_DIR


# Global settings instance — tek bir yerden import edilir
# Global settings instance — imported from a single place
settings = Settings()
