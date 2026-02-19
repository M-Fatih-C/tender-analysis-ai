"""
TenderAI Veritabanı Testleri / Database Tests.

Veritabanı modelleri ve DatabaseManager için birim testleri.
Unit tests for database models and DatabaseManager.
"""

import pytest

from src.database.models import Base, User, Analysis, Document
from src.database.db import DatabaseManager


class TestDatabaseModels:
    """Veritabanı model testleri / Database model tests."""

    def test_user_model_tablename(self) -> None:
        """User model tablo adı / User model table name."""
        assert User.__tablename__ == "users"

    def test_document_model_tablename(self) -> None:
        """Document model tablo adı / Document model table name."""
        assert Document.__tablename__ == "documents"

    def test_analysis_model_tablename(self) -> None:
        """Analysis model tablo adı / Analysis model table name."""
        assert Analysis.__tablename__ == "analyses"

    def test_base_class_exists(self) -> None:
        """Base sınıfının varlığı / Base class existence."""
        assert Base is not None


class TestDatabaseManager:
    """DatabaseManager testleri / DatabaseManager tests."""

    def test_db_manager_init(self) -> None:
        """DatabaseManager başlatma / Initialize DatabaseManager."""
        db = DatabaseManager(database_url="sqlite:///test.db")
        assert db.database_url == "sqlite:///test.db"

    def test_db_manager_create_tables_not_implemented(self) -> None:
        """create_tables henüz implement edilmemeli / should not be implemented yet."""
        db = DatabaseManager(database_url="sqlite:///test.db")
        with pytest.raises(NotImplementedError):
            db.create_tables()

    def test_db_manager_get_session_not_implemented(self) -> None:
        """get_session henüz implement edilmemeli / should not be implemented yet."""
        db = DatabaseManager(database_url="sqlite:///test.db")
        with pytest.raises(NotImplementedError):
            next(db.get_session())

    def test_db_manager_close_not_implemented(self) -> None:
        """close henüz implement edilmemeli / should not be implemented yet."""
        db = DatabaseManager(database_url="sqlite:///test.db")
        with pytest.raises(NotImplementedError):
            db.close()
