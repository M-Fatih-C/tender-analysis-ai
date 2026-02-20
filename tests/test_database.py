"""
TenderAI Veritabanı Testleri / Database Tests.

SQLAlchemy modelleri ve CRUD operasyonları için birim testleri.
Unit tests for SQLAlchemy models and CRUD operations.

Her test in-memory SQLite kullanır — diske yazmaz.
Each test uses in-memory SQLite — no disk writes.
"""

import json
import pytest
from datetime import datetime, timezone, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, User, Analysis, Payment, AnalysisReport
from src.database.db import (
    DatabaseManager,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
    increment_analysis_count,
    check_analysis_limit,
    create_analysis,
    update_analysis_result,
    get_analysis_by_id,
    get_user_analyses,
    get_analysis_stats,
    create_payment,
    update_payment_status,
    get_user_payments,
    check_active_subscription,
    create_report,
)


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def db_session():
    """In-memory SQLite session oluştur / Create in-memory SQLite session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def sample_user(db_session):
    """Örnek kullanıcı oluştur / Create sample user."""
    user = create_user(
        db_session,
        email="test@example.com",
        password_hash="hashed_password_123",
        full_name="Test Kullanıcı",
        company_name="Test Şirket",
        phone="+905551234567",
    )
    db_session.commit()
    return user


@pytest.fixture
def sample_analysis(db_session, sample_user):
    """Örnek analiz oluştur / Create sample analysis."""
    analysis = create_analysis(
        db_session,
        user_id=sample_user.id,
        file_name="sartname.pdf",
        file_size_mb=2.5,
        total_pages=45,
    )
    db_session.commit()
    return analysis


# ============================================================
# Model Testleri / Model Tests
# ============================================================


class TestModels:
    """Model tablosu ve alan testleri / Model table and field tests."""

    def test_user_table_name(self) -> None:
        assert User.__tablename__ == "users"

    def test_analysis_table_name(self) -> None:
        assert Analysis.__tablename__ == "analyses"

    def test_payment_table_name(self) -> None:
        assert Payment.__tablename__ == "payments"

    def test_analysis_report_table_name(self) -> None:
        assert AnalysisReport.__tablename__ == "analysis_reports"

    def test_base_class(self) -> None:
        assert issubclass(User, Base)
        assert issubclass(Analysis, Base)
        assert issubclass(Payment, Base)
        assert issubclass(AnalysisReport, Base)


# ============================================================
# DatabaseManager Testleri
# ============================================================


class TestDatabaseManager:
    """DatabaseManager testleri / tests."""

    def test_init_with_custom_url(self) -> None:
        """Özel URL ile başlatma / Init with custom URL."""
        db_mgr = DatabaseManager(database_url="sqlite:///:memory:")
        assert db_mgr.database_url == "sqlite:///:memory:"
        db_mgr.close()

    def test_init_db_creates_tables(self) -> None:
        """init_db tabloları oluşturmalı / Should create tables."""
        db_mgr = DatabaseManager(database_url="sqlite:///:memory:")
        db_mgr.init_db()

        # Tablolar var mı kontrol et / Check tables exist
        from sqlalchemy import inspect
        inspector = inspect(db_mgr.engine)
        tables = inspector.get_table_names()
        assert "users" in tables
        assert "analyses" in tables
        assert "payments" in tables
        assert "analysis_reports" in tables
        db_mgr.close()

    def test_get_db_context_manager(self) -> None:
        """get_db context manager çalışmalı / Should work as context manager."""
        db_mgr = DatabaseManager(database_url="sqlite:///:memory:")
        db_mgr.init_db()

        with db_mgr.get_db() as session:
            assert session is not None
            user = User(
                email="cm@test.com",
                password_hash="hash",
                full_name="CM Test",
            )
            session.add(user)

        # Commit olmuş mu kontrol et / Check if committed
        with db_mgr.get_db() as session:
            found = session.query(User).filter_by(email="cm@test.com").first()
            assert found is not None
            assert found.full_name == "CM Test"

        db_mgr.close()

    def test_get_db_rollback_on_error(self) -> None:
        """Hata durumunda rollback yapmalı / Should rollback on error."""
        db_mgr = DatabaseManager(database_url="sqlite:///:memory:")
        db_mgr.init_db()

        with pytest.raises(ValueError):
            with db_mgr.get_db() as session:
                session.add(User(
                    email="rollback@test.com",
                    password_hash="hash",
                    full_name="Rollback Test",
                ))
                raise ValueError("Test error")

        # Rollback olmuş mu / Was it rolled back?
        with db_mgr.get_db() as session:
            found = session.query(User).filter_by(email="rollback@test.com").first()
            assert found is None

        db_mgr.close()


# ============================================================
# User CRUD Testleri
# ============================================================


class TestUserCRUD:
    """Kullanıcı CRUD testleri / User CRUD tests."""

    def test_create_user(self, db_session) -> None:
        """Kullanıcı oluşturma / Create user."""
        user = create_user(
            db_session,
            email="new@test.com",
            password_hash="hash123",
            full_name="Yeni Kullanıcı",
        )
        db_session.commit()

        assert user.id is not None
        assert user.email == "new@test.com"
        assert user.plan == "free"
        assert user.analysis_count == 0
        assert user.max_analysis_per_month == 3
        assert user.is_active is True

    def test_create_user_with_company(self, db_session) -> None:
        """Şirket bilgisiyle kullanıcı oluşturma / Create user with company."""
        user = create_user(
            db_session,
            email="corp@test.com",
            password_hash="hash",
            full_name="Şirket Kullanıcı",
            company_name="ABC Ltd.",
            phone="+905551112233",
        )
        db_session.commit()

        assert user.company_name == "ABC Ltd."
        assert user.phone == "+905551112233"

    def test_get_user_by_email(self, db_session, sample_user) -> None:
        """E-posta ile kullanıcı getirme / Get user by email."""
        found = get_user_by_email(db_session, "test@example.com")
        assert found is not None
        assert found.id == sample_user.id

    def test_get_user_by_email_not_found(self, db_session) -> None:
        """Olmayan e-posta ile None dönmeli / Should return None for missing email."""
        found = get_user_by_email(db_session, "nonexistent@test.com")
        assert found is None

    def test_get_user_by_id(self, db_session, sample_user) -> None:
        """ID ile kullanıcı getirme / Get user by ID."""
        found = get_user_by_id(db_session, sample_user.id)
        assert found is not None
        assert found.email == "test@example.com"

    def test_update_user(self, db_session, sample_user) -> None:
        """Kullanıcı güncelleme / Update user."""
        updated = update_user(
            db_session, sample_user.id,
            full_name="Güncellenen İsim",
            plan="pro",
        )
        db_session.commit()

        assert updated.full_name == "Güncellenen İsim"
        assert updated.plan == "pro"

    def test_update_user_not_found(self, db_session) -> None:
        """Olmayan kullanıcı güncellemesi / Update missing user."""
        result = update_user(db_session, 99999, full_name="X")
        assert result is None

    def test_increment_analysis_count(self, db_session, sample_user) -> None:
        """Analiz sayısı artırma / Increment analysis count."""
        assert sample_user.analysis_count == 0
        increment_analysis_count(db_session, sample_user.id)
        db_session.commit()
        assert sample_user.analysis_count == 1

        increment_analysis_count(db_session, sample_user.id)
        db_session.commit()
        assert sample_user.analysis_count == 2

    def test_check_analysis_limit_not_exceeded(self, db_session, sample_user) -> None:
        """Limit aşılmamış / Limit not exceeded."""
        assert check_analysis_limit(db_session, sample_user.id) is False

    def test_check_analysis_limit_exceeded(self, db_session, sample_user) -> None:
        """Limit aşılmış / Limit exceeded."""
        sample_user.analysis_count = 3
        db_session.commit()
        assert check_analysis_limit(db_session, sample_user.id) is True

    def test_check_analysis_limit_missing_user(self, db_session) -> None:
        """Olmayan kullanıcı engellenmeli / Missing user should be blocked."""
        assert check_analysis_limit(db_session, 99999) is True

    def test_user_repr(self, db_session, sample_user) -> None:
        """User __repr__ çalışmalı / Should produce readable repr."""
        r = repr(sample_user)
        assert "test@example.com" in r
        assert "free" in r


# ============================================================
# Analysis CRUD Testleri
# ============================================================


class TestAnalysisCRUD:
    """Analiz CRUD testleri / Analysis CRUD tests."""

    def test_create_analysis(self, db_session, sample_user) -> None:
        """Analiz oluşturma / Create analysis."""
        analysis = create_analysis(
            db_session,
            user_id=sample_user.id,
            file_name="ihale.pdf",
            file_size_mb=5.2,
            total_pages=120,
        )
        db_session.commit()

        assert analysis.id is not None
        assert analysis.file_name == "ihale.pdf"
        assert analysis.status == "pending"
        assert analysis.risk_score is None

    def test_update_analysis_result(self, db_session, sample_analysis) -> None:
        """Analiz sonucu güncelleme / Update analysis result."""
        result_data = {
            "risk_analysis": {"risk_skoru": 65},
            "penalty_clauses": {"toplam_ceza_sayisi": 3},
        }
        updated = update_analysis_result(
            db_session,
            analysis_id=sample_analysis.id,
            risk_score=65,
            risk_level="YÜKSEK",
            result_json=result_data,
            executive_summary="Bu ihale yüksek riskli.",
            tokens_used=12000,
            cost_usd=0.12,
            analysis_duration_seconds=45.3,
        )
        db_session.commit()

        assert updated.status == "completed"
        assert updated.risk_score == 65
        assert updated.risk_level == "YÜKSEK"
        assert updated.tokens_used == 12000
        assert updated.completed_at is not None

        # JSON parse edilebilmeli / Should be JSON-parseable
        parsed = json.loads(updated.result_json)
        assert parsed["risk_analysis"]["risk_skoru"] == 65

    def test_update_analysis_not_found(self, db_session) -> None:
        """Olmayan analiz güncellemesi / Update missing analysis."""
        result = update_analysis_result(db_session, analysis_id=99999, risk_score=50)
        assert result is None

    def test_get_analysis_by_id(self, db_session, sample_analysis) -> None:
        """ID ile analiz getirme / Get analysis by ID."""
        found = get_analysis_by_id(db_session, sample_analysis.id)
        assert found is not None
        assert found.file_name == "sartname.pdf"

    def test_get_user_analyses(self, db_session, sample_user) -> None:
        """Kullanıcının analizlerini getirme / Get user analyses."""
        for i in range(5):
            create_analysis(db_session, sample_user.id, f"doc_{i}.pdf")
        db_session.commit()

        analyses = get_user_analyses(db_session, sample_user.id, limit=3)
        assert len(analyses) == 3

    def test_get_user_analyses_with_offset(self, db_session, sample_user) -> None:
        """Offset ile analiz getirme / Get analyses with offset."""
        for i in range(5):
            create_analysis(db_session, sample_user.id, f"doc_{i}.pdf")
        db_session.commit()

        analyses = get_user_analyses(db_session, sample_user.id, limit=10, offset=3)
        assert len(analyses) == 2

    def test_get_analysis_stats(self, db_session, sample_user) -> None:
        """Analiz istatistikleri / Analysis stats."""
        a1 = create_analysis(db_session, sample_user.id, "a.pdf")
        a2 = create_analysis(db_session, sample_user.id, "b.pdf")
        db_session.commit()

        update_analysis_result(db_session, a1.id, risk_score=60, tokens_used=5000, cost_usd=0.05)
        update_analysis_result(db_session, a2.id, risk_score=80, tokens_used=8000, cost_usd=0.08)
        db_session.commit()

        stats = get_analysis_stats(db_session, sample_user.id)
        assert stats["total_analyses"] == 2
        assert stats["completed_analyses"] == 2
        assert stats["average_risk_score"] == 70.0
        assert stats["total_tokens_used"] == 13000
        assert stats["total_cost_usd"] == 0.13

    def test_get_analysis_stats_empty(self, db_session, sample_user) -> None:
        """Boş istatistikler / Empty stats."""
        stats = get_analysis_stats(db_session, sample_user.id)
        assert stats["total_analyses"] == 0
        assert stats["average_risk_score"] is None

    def test_analysis_repr(self, db_session, sample_analysis) -> None:
        """Analysis __repr__ çalışmalı."""
        r = repr(sample_analysis)
        assert "sartname.pdf" in r
        assert "pending" in r

    def test_analysis_user_relationship(self, db_session, sample_user, sample_analysis) -> None:
        """Analiz-kullanıcı ilişkisi / Analysis-user relationship."""
        assert sample_analysis.user.id == sample_user.id
        assert sample_analysis in sample_user.analyses


# ============================================================
# Payment CRUD Testleri
# ============================================================


class TestPaymentCRUD:
    """Ödeme CRUD testleri / Payment CRUD tests."""

    def test_create_payment(self, db_session, sample_user) -> None:
        """Ödeme oluşturma / Create payment."""
        payment = create_payment(
            db_session,
            user_id=sample_user.id,
            amount_try=299.0,
            plan="pro",
            payment_method="credit_card",
        )
        db_session.commit()

        assert payment.id is not None
        assert payment.amount_try == 299.0
        assert payment.plan == "pro"
        assert payment.payment_status == "pending"

    def test_update_payment_status(self, db_session, sample_user) -> None:
        """Ödeme durumu güncelleme / Update payment status."""
        payment = create_payment(
            db_session, sample_user.id, 299.0, "pro",
        )
        db_session.commit()

        updated = update_payment_status(
            db_session, payment.id, "completed", transaction_id="TXN_12345",
        )
        db_session.commit()

        assert updated.payment_status == "completed"
        assert updated.transaction_id == "TXN_12345"

    def test_update_payment_not_found(self, db_session) -> None:
        """Olmayan ödeme güncellemesi / Update missing payment."""
        result = update_payment_status(db_session, 99999, "completed")
        assert result is None

    def test_get_user_payments(self, db_session, sample_user) -> None:
        """Kullanıcı ödemelerini getirme / Get user payments."""
        create_payment(db_session, sample_user.id, 99.0, "starter")
        create_payment(db_session, sample_user.id, 299.0, "pro")
        db_session.commit()

        payments = get_user_payments(db_session, sample_user.id)
        assert len(payments) == 2

    def test_check_active_subscription_none(self, db_session, sample_user) -> None:
        """Aktif abonelik yok / No active subscription."""
        assert check_active_subscription(db_session, sample_user.id) is False

    def test_check_active_subscription_active(self, db_session, sample_user) -> None:
        """Aktif abonelik var / Has active subscription."""
        now = datetime.now(timezone.utc)
        payment = create_payment(
            db_session, sample_user.id, 299.0, "pro",
            period_start=now - timedelta(days=10),
            period_end=now + timedelta(days=20),
        )
        db_session.commit()
        update_payment_status(db_session, payment.id, "completed")
        db_session.commit()

        assert check_active_subscription(db_session, sample_user.id) is True

    def test_check_active_subscription_expired(self, db_session, sample_user) -> None:
        """Süresi dolmuş abonelik / Expired subscription."""
        now = datetime.now(timezone.utc)
        payment = create_payment(
            db_session, sample_user.id, 299.0, "pro",
            period_start=now - timedelta(days=60),
            period_end=now - timedelta(days=30),
        )
        db_session.commit()
        update_payment_status(db_session, payment.id, "completed")
        db_session.commit()

        assert check_active_subscription(db_session, sample_user.id) is False

    def test_payment_user_relationship(self, db_session, sample_user) -> None:
        """Ödeme-kullanıcı ilişkisi / Payment-user relationship."""
        payment = create_payment(db_session, sample_user.id, 99.0, "starter")
        db_session.commit()
        assert payment.user.id == sample_user.id

    def test_payment_repr(self, db_session, sample_user) -> None:
        """Payment __repr__ çalışmalı."""
        payment = create_payment(db_session, sample_user.id, 199.0, "starter")
        db_session.commit()
        r = repr(payment)
        assert "199.0" in r
        assert "pending" in r


# ============================================================
# Report Testleri
# ============================================================


class TestReportCRUD:
    """Rapor CRUD testleri / Report CRUD tests."""

    def test_create_report(self, db_session, sample_analysis) -> None:
        """Rapor oluşturma / Create report."""
        report = create_report(
            db_session, sample_analysis.id,
            report_path="/data/reports/report_1.pdf",
            report_type="full",
        )
        db_session.commit()

        assert report.id is not None
        assert report.report_path == "/data/reports/report_1.pdf"
        assert report.report_type == "full"

    def test_report_analysis_relationship(self, db_session, sample_analysis) -> None:
        """Rapor-analiz ilişkisi / Report-analysis relationship."""
        report = create_report(
            db_session, sample_analysis.id,
            report_path="/data/reports/r.pdf",
        )
        db_session.commit()

        assert report.analysis.id == sample_analysis.id
        assert report in sample_analysis.reports

    def test_report_repr(self, db_session, sample_analysis) -> None:
        """AnalysisReport __repr__ çalışmalı."""
        report = create_report(
            db_session, sample_analysis.id,
            report_path="/x.pdf",
            report_type="summary",
        )
        db_session.commit()
        r = repr(report)
        assert "summary" in r


# ============================================================
# Cascade ve Edge Case Testleri
# ============================================================


class TestCascadeAndEdgeCases:
    """Cascade silme ve edge case testleri."""

    def test_delete_user_cascades_analyses(self, db_session) -> None:
        """Kullanıcı silinince analizleri de silinmeli / Cascade delete."""
        user = create_user(db_session, "cascade@test.com", "hash", "Cascade User")
        db_session.commit()
        analysis = create_analysis(db_session, user.id, "del.pdf")
        db_session.commit()

        analysis_id = analysis.id
        db_session.delete(user)
        db_session.commit()

        assert get_analysis_by_id(db_session, analysis_id) is None

    def test_delete_user_cascades_payments(self, db_session) -> None:
        """Kullanıcı silinince ödemeleri de silinmeli / Cascade delete."""
        user = create_user(db_session, "pay_del@test.com", "hash", "Pay Del")
        db_session.commit()
        create_payment(db_session, user.id, 99.0, "starter")
        db_session.commit()

        db_session.delete(user)
        db_session.commit()

        payments = get_user_payments(db_session, user.id)
        assert len(payments) == 0

    def test_unique_email_constraint(self, db_session) -> None:
        """Aynı e-posta ile ikinci kullanıcı oluşturulamamalı / Duplicate email."""
        create_user(db_session, "dup@test.com", "h1", "User1")
        db_session.commit()

        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            create_user(db_session, "dup@test.com", "h2", "User2")
            db_session.commit()
