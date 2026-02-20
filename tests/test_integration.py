"""
TenderAI Entegrasyon Testleri / Integration Tests.

Uçtan uca akışları test eder: kayıt → giriş → analiz limiti →
plan yükseltme → PDF rapor üretme.

End-to-end flow tests: register → login → analysis limit →
plan upgrade → PDF report generation.

In-memory SQLite kullanır.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base
from src.database.db import (
    create_user,
    create_analysis,
    update_analysis_result,
    get_user_analyses,
    get_analysis_stats,
    increment_analysis_count,
)
from src.auth.auth import AuthManager
from src.payment.payment import PaymentManager
from src.report.generator import ReportGenerator
from config.demo_data import DEMO_ANALYSIS_RESULT


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def db_session():
    """In-memory SQLite session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


# ============================================================
# Uçtan Uca Akış Testleri / End-to-End Flow Tests
# ============================================================


class TestUserRegistrationAndLogin:
    """Kayıt → Giriş akışı."""

    def test_register_then_login(self, db_session) -> None:
        """Kayıt yap, sonra giriş yap / Register then login."""
        auth = AuthManager(db_session)

        # Kayıt
        ok, msg, user = auth.register(
            "flow@test.com", "FlowTest1", "Flow User", "Flow Corp"
        )
        db_session.commit()
        assert ok is True
        assert user is not None

        # Giriş
        ok, msg, logged_in = auth.login("flow@test.com", "FlowTest1")
        assert ok is True
        assert logged_in.id == user.id
        assert logged_in.full_name == "Flow User"

    def test_register_change_password_login(self, db_session) -> None:
        """Kayıt → şifre değiştir → yeni şifreyle giriş."""
        auth = AuthManager(db_session)
        ok, _, user = auth.register("pwd@test.com", "OldPass1x", "Pwd User")
        db_session.commit()

        ok, msg = auth.change_password(user.id, "OldPass1x", "NewPass1x")
        db_session.commit()
        assert ok is True

        # Eski şifreyle giriş olmaz
        ok, _, _ = auth.login("pwd@test.com", "OldPass1x")
        assert ok is False

        # Yeni şifreyle giriş olur
        ok, _, _ = auth.login("pwd@test.com", "NewPass1x")
        assert ok is True


class TestAnalysisFlow:
    """Analiz akışı: oluştur → güncelle → istatistik → geçmiş."""

    def test_create_and_update_analysis(self, db_session) -> None:
        """Analiz oluştur ve sonuç kaydet."""
        user = create_user(db_session, "analyst@test.com", "hash", "Analyst")
        db_session.commit()

        analysis = create_analysis(
            db_session, user.id,
            file_name="test_sartname.pdf",
            file_size_mb=2.5,
            total_pages=15,
        )
        db_session.commit()
        assert analysis.status == "pending"

        # Sonuç güncelle
        update_analysis_result(
            db_session, analysis.id,
            risk_score=67, risk_level="YÜKSEK",
            result_json=DEMO_ANALYSIS_RESULT,
            executive_summary="Orta-yüksek risk",
            tokens_used=12000, cost_usd=0.06,
            analysis_duration_seconds=38.5,
        )
        db_session.commit()

        # Geçmişte görünsün
        history = get_user_analyses(db_session, user.id)
        assert len(history) == 1
        assert history[0].risk_score == 67
        assert history[0].status == "completed"

    def test_analysis_stats(self, db_session) -> None:
        """İstatistik hesaplaması."""
        user = create_user(db_session, "stats@test.com", "hash", "Stats User")
        db_session.commit()

        for score in [30, 50, 80]:
            a = create_analysis(db_session, user.id, file_name=f"doc_{score}.pdf")
            db_session.commit()
            update_analysis_result(
                db_session, a.id,
                risk_score=score, risk_level="X",
                result_json={},
            )
            db_session.commit()

        stats = get_analysis_stats(db_session, user.id)
        assert stats["total_analyses"] == 3
        assert stats["completed_analyses"] == 3


class TestPlanLimitFlow:
    """Plan limiti akışı: free limit → yükseltme → sınırsız."""

    def test_free_limit_then_upgrade(self, db_session) -> None:
        """Free kullanıcı 3 limit → starter'a yükselt → devam."""
        auth = AuthManager(db_session)
        ok, _, user = auth.register("limit@test.com", "Limit1xx", "Limit User")
        db_session.commit()

        pm = PaymentManager(db_session)

        # 3 analiz yap
        for _ in range(3):
            increment_analysis_count(db_session, user.id)
        db_session.commit()
        db_session.refresh(user)

        # 4. analiz engellenmeli
        can, msg = pm.check_can_analyze(user)
        assert can is False

        # Plan yükselt
        ok, msg = pm.upgrade_plan(user, "starter")
        db_session.commit()
        db_session.refresh(user)
        assert ok is True
        assert user.plan == "starter"
        assert user.analysis_count == 0  # Sıfırlandı

        # Artık analiz yapabilir
        can, msg = pm.check_can_analyze(user)
        assert can is True


class TestPDFReportGeneration:
    """PDF rapor üretimi."""

    def test_generate_report_from_demo_data(self) -> None:
        """Demo veriden PDF rapor üret."""
        gen = ReportGenerator()
        pdf_bytes = gen.generate(DEMO_ANALYSIS_RESULT, "demo_sartname.pdf")
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes[:5] == b"%PDF-"
        assert len(pdf_bytes) > 5000  # Anlamlı boyut


class TestFullCycle:
    """Tam döngü: kayıt → giriş → analiz → rapor."""

    def test_complete_user_journey(self, db_session) -> None:
        """Kullanıcı yolculuğunun tamamı."""
        # 1. Kayıt
        auth = AuthManager(db_session)
        ok, _, user = auth.register("journey@test.com", "Journey1", "Journey User")
        db_session.commit()
        assert ok

        # 2. Giriş
        ok, _, user = auth.login("journey@test.com", "Journey1")
        assert ok

        # 3. Plan kontrol
        pm = PaymentManager(db_session)
        can, _ = pm.check_can_analyze(user)
        assert can

        # 4. Analiz oluştur
        analysis = create_analysis(
            db_session, user.id,
            file_name="journey_doc.pdf",
            file_size_mb=1.0,
            total_pages=10,
        )
        db_session.commit()

        # 5. Sonuç kaydet
        update_analysis_result(
            db_session, analysis.id,
            risk_score=67, risk_level="YÜKSEK",
            result_json=DEMO_ANALYSIS_RESULT,
        )
        increment_analysis_count(db_session, user.id)
        db_session.commit()

        # 6. Rapor üret
        gen = ReportGenerator()
        pdf = gen.generate(DEMO_ANALYSIS_RESULT, "journey_doc.pdf")
        assert len(pdf) > 5000

        # 7. Geçmiş kontrol
        history = get_user_analyses(db_session, user.id)
        assert len(history) == 1

        # 8. İstatistik
        stats = get_analysis_stats(db_session, user.id)
        assert stats["total_analyses"] == 1
