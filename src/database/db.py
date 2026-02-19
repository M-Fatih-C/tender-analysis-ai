"""
TenderAI Veritabanı Bağlantı Yönetimi / Database Connection Management.

SQLAlchemy engine ve session yönetimini sağlar.
Provides SQLAlchemy engine and session management.

Bu modül Modül 4'te implement edilecektir.
This module will be implemented in Module 4.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import settings
from src.database.models import Base


class DatabaseManager:
    """
    Veritabanı bağlantı yöneticisi / Database connection manager.

    SQLite veritabanı bağlantısını ve session yönetimini sağlar.
    Manages SQLite database connection and session management.
    """

    def __init__(self, database_url: str | None = None) -> None:
        """
        DatabaseManager başlat / Initialize DatabaseManager.

        Args:
            database_url: Veritabanı URL'si / Database URL (opsiyonel, config'den okunur)
        """
        self.database_url = database_url or settings.DATABASE_URL
        self._engine = None
        self._session_factory = None

    def _get_engine(self):
        """
        SQLAlchemy engine oluştur / Create SQLAlchemy engine.

        Returns:
            SQLAlchemy Engine nesnesi / SQLAlchemy Engine object

        Raises:
            NotImplementedError: Modül 4'te implement edilecek
        """
        raise NotImplementedError("Modül 4'te implement edilecek / Will be implemented in Module 4")

    def create_tables(self) -> None:
        """
        Veritabanı tablolarını oluştur / Create database tables.

        Raises:
            NotImplementedError: Modül 4'te implement edilecek
        """
        raise NotImplementedError("Modül 4'te implement edilecek / Will be implemented in Module 4")

    def get_session(self) -> Generator[Session, None, None]:
        """
        Veritabanı session'ı al / Get database session.

        Yields:
            SQLAlchemy Session nesnesi / SQLAlchemy Session object

        Raises:
            NotImplementedError: Modül 4'te implement edilecek
        """
        raise NotImplementedError("Modül 4'te implement edilecek / Will be implemented in Module 4")

    def close(self) -> None:
        """
        Veritabanı bağlantısını kapat / Close database connection.

        Raises:
            NotImplementedError: Modül 4'te implement edilecek
        """
        raise NotImplementedError("Modül 4'te implement edilecek / Will be implemented in Module 4")
