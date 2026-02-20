"""
TenderAI Ödeme Sistemi Testleri / Payment System Tests.

PaymentManager sınıfı için birim testleri.
Unit tests for PaymentManager class.

In-memory SQLite kullanır.
Uses in-memory SQLite.
"""

import pytest
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, User
from src.database.db import create_user
from src.payment.payment import PaymentManager, PLANS


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


@pytest.fixture
def pm(db_session):
    """PaymentManager instance."""
    return PaymentManager(db_session)


@pytest.fixture
def free_user(db_session):
    """Ücretsiz plan kullanıcısı / Free plan user."""
    user = create_user(
        db_session, "free@test.com", "hash", "Free User"
    )
    db_session.commit()
    return user


@pytest.fixture
def starter_user(db_session):
    """Başlangıç plan kullanıcısı / Starter plan user."""
    user = create_user(
        db_session, "starter@test.com", "hash", "Starter User"
    )
    user.plan = "starter"
    user.max_analysis_per_month = 20
    db_session.commit()
    return user


# ============================================================
# Plan Tanım Testleri / Plan Definition Tests
# ============================================================


class TestPlanDefinitions:
    """Plan tanımları testleri."""

    def test_three_plans_exist(self) -> None:
        """3 plan tanımlı olmalı / 3 plans should be defined."""
        assert len(PLANS) == 3
        assert "free" in PLANS
        assert "starter" in PLANS
        assert "pro" in PLANS

    def test_free_plan_values(self) -> None:
        """Ücretsiz plan değerleri / Free plan values."""
        p = PLANS["free"]
        assert p["price_monthly_try"] == 0
        assert p["max_analysis_per_month"] == 3
        assert isinstance(p["features"], list)

    def test_starter_plan_values(self) -> None:
        """Başlangıç plan değerleri / Starter plan values."""
        p = PLANS["starter"]
        assert p["price_monthly_try"] == 5_000
        assert p["max_analysis_per_month"] == 20

    def test_pro_plan_values(self) -> None:
        """Pro plan değerleri / Pro plan values."""
        p = PLANS["pro"]
        assert p["price_monthly_try"] == 15_000
        assert p["max_analysis_per_month"] == 9999

    def test_get_plans(self, pm) -> None:
        """get_plans tüm planları döndürmeli / Should return all plans."""
        plans = pm.get_plans()
        assert isinstance(plans, dict)
        assert len(plans) == 3

    def test_get_plan_valid(self, pm) -> None:
        """Geçerli plan getirme / Get valid plan."""
        plan = pm.get_plan("starter")
        assert plan is not None
        assert plan["name"] == "Başlangıç"

    def test_get_plan_invalid(self, pm) -> None:
        """Geçersiz plan None döndürmeli / Invalid plan should return None."""
        assert pm.get_plan("nonexistent") is None


# ============================================================
# Limit Kontrol Testleri / Limit Check Tests
# ============================================================


class TestCanAnalyze:
    """Analiz limit kontrol testleri."""

    def test_free_user_can_analyze(self, pm, free_user) -> None:
        """Yeni free kullanıcı analiz yapabilmeli / New free user should be able to analyze."""
        can, msg = pm.check_can_analyze(free_user)
        assert can is True
        assert "Kalan" in msg

    def test_free_user_limit_reached(self, db_session, pm, free_user) -> None:
        """3 analiz sonrası limit dolmalı / Limit should be reached after 3."""
        free_user.analysis_count = 3
        db_session.commit()

        can, msg = pm.check_can_analyze(free_user)
        assert can is False
        assert "doldu" in msg

    def test_starter_user_can_analyze(self, pm, starter_user) -> None:
        """Starter kullanıcı analiz yapabilmeli / Starter user should be able to analyze."""
        can, msg = pm.check_can_analyze(starter_user)
        assert can is True

    def test_pro_user_unlimited(self, db_session, pm) -> None:
        """Pro kullanıcı sınırsız olmalı / Pro user should be unlimited."""
        user = create_user(db_session, "pro@test.com", "hash", "Pro User")
        user.plan = "pro"
        user.analysis_count = 500
        db_session.commit()

        can, msg = pm.check_can_analyze(user)
        assert can is True
        assert "Sınırsız" in msg


# ============================================================
# Plan Info Testleri / Plan Info Tests
# ============================================================


class TestPlanInfo:
    """Plan bilgi testleri."""

    def test_free_plan_info(self, pm, free_user) -> None:
        """Free plan bilgileri doğru olmalı / Free plan info should be correct."""
        info = pm.get_user_plan_info(free_user)
        assert info["plan_key"] == "free"
        assert info["plan_name"] == "Ücretsiz"
        assert info["max_analysis_per_month"] == 3
        assert info["remaining_analyses"] == 3
        assert info["is_unlimited"] is False

    def test_starter_plan_info(self, pm, starter_user) -> None:
        """Starter plan bilgileri / Starter plan info."""
        info = pm.get_user_plan_info(starter_user)
        assert info["plan_key"] == "starter"
        assert info["remaining_analyses"] == 20

    def test_plan_info_with_usage(self, db_session, pm, free_user) -> None:
        """Kullanım sonrası kalan hak / Remaining after usage."""
        free_user.analysis_count = 2
        db_session.commit()
        info = pm.get_user_plan_info(free_user)
        assert info["remaining_analyses"] == 1


# ============================================================
# Kullanım İstatistikleri Testleri / Usage Stats Tests
# ============================================================


class TestUsageStats:
    """Kullanım istatistikleri testleri."""

    def test_empty_stats(self, pm, free_user) -> None:
        """Boş istatistikler / Empty stats."""
        stats = pm.get_usage_stats(free_user)
        assert stats["total_used"] == 0
        assert stats["usage_percent"] == 0
        assert stats["is_limit_reached"] is False

    def test_partial_usage(self, db_session, pm, free_user) -> None:
        """Kısmi kullanım / Partial usage."""
        free_user.analysis_count = 2
        db_session.commit()
        stats = pm.get_usage_stats(free_user)
        assert stats["total_used"] == 2
        assert stats["usage_percent"] == 67  # 2/3 * 100

    def test_full_usage(self, db_session, pm, free_user) -> None:
        """Tam kullanım / Full usage."""
        free_user.analysis_count = 3
        db_session.commit()
        stats = pm.get_usage_stats(free_user)
        assert stats["is_limit_reached"] is True
        assert stats["usage_percent"] == 100


# ============================================================
# Plan Yükseltme Testleri / Plan Upgrade Tests
# ============================================================


class TestUpgradePlan:
    """Plan yükseltme testleri."""

    def test_upgrade_free_to_starter(self, db_session, pm, free_user) -> None:
        """Free → Starter yükseltme / Free to Starter upgrade."""
        ok, msg = pm.upgrade_plan(free_user, "starter")
        db_session.commit()
        assert ok is True
        assert "güncellendi" in msg

        # DB'de güncellenmiş mi / Updated in DB?
        from src.database.db import get_user_by_id
        updated = get_user_by_id(db_session, free_user.id)
        assert updated.plan == "starter"
        assert updated.max_analysis_per_month == 20
        assert updated.analysis_count == 0  # Sıfırlanmış

    def test_upgrade_starter_to_pro(self, db_session, pm, starter_user) -> None:
        """Starter → Pro yükseltme / Starter to Pro upgrade."""
        ok, msg = pm.upgrade_plan(starter_user, "pro")
        db_session.commit()
        assert ok is True

    def test_upgrade_same_plan(self, pm, free_user) -> None:
        """Aynı plana yükseltme engellenmeli / Same plan should be blocked."""
        ok, msg = pm.upgrade_plan(free_user, "free")
        assert ok is False
        assert "Zaten" in msg

    def test_downgrade_blocked(self, pm, starter_user) -> None:
        """Düşürme engellenmeli / Downgrade should be blocked."""
        ok, msg = pm.upgrade_plan(starter_user, "free")
        assert ok is False
        assert "üst planlara" in msg

    def test_upgrade_invalid_plan(self, pm, free_user) -> None:
        """Geçersiz plan / Invalid plan."""
        ok, msg = pm.upgrade_plan(free_user, "nonexistent")
        assert ok is False

    def test_upgrade_creates_payment_record(self, db_session, pm, free_user) -> None:
        """Yükseltme ödeme kaydı oluşturmalı / Should create payment record."""
        from src.database.db import get_user_payments
        pm.upgrade_plan(free_user, "starter")
        db_session.commit()

        payments = get_user_payments(db_session, free_user.id)
        assert len(payments) == 1
        assert payments[0].payment_status == "completed"
        assert payments[0].plan == "starter"
        assert payments[0].amount_try == 5000


# ============================================================
# Karşılaştırma ve Placeholder Testleri
# ============================================================


class TestComparison:
    """Plan karşılaştırma testleri."""

    def test_comparison_returns_3_plans(self) -> None:
        comparison = PaymentManager.get_plan_comparison()
        assert len(comparison) == 3

    def test_comparison_has_required_fields(self) -> None:
        comparison = PaymentManager.get_plan_comparison()
        for item in comparison:
            assert "plan_key" in item
            assert "plan_name" in item
            assert "price" in item
            assert "analysis_limit" in item


class TestPlaceholders:
    """Placeholder testleri."""

    def test_iyzico_not_implemented(self, pm, free_user) -> None:
        with pytest.raises(NotImplementedError):
            pm._process_payment_iyzico(free_user, 5000, {})

    def test_paytr_not_implemented(self, pm, free_user) -> None:
        with pytest.raises(NotImplementedError):
            pm._process_payment_paytr(free_user, 5000, {})
