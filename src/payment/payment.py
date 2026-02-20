"""
TenderAI Ödeme ve Plan Yönetimi / Payment & Plan Management.

Abonelik planları, limit kontrolü ve ödeme altyapısı iskeleti.
Subscription plans, limit checks, and payment infrastructure scaffold.

MVP aşamasında gerçek ödeme entegrasyonu (iyzico, PayTR) yok.
No real payment integration in MVP phase.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from src.database.db import (
    create_payment,
    update_payment_status,
    update_user,
    get_user_by_id,
    get_user_analyses,
    check_active_subscription,
)
from src.database.models import User

logger = logging.getLogger(__name__)


# ============================================================
# Plan Tanımları / Plan Definitions
# ============================================================

PLANS: dict[str, dict[str, Any]] = {
    "free": {
        "name": "Ücretsiz",
        "price_monthly_try": 0,
        "max_analysis_per_month": 3,
        "features": [
            "Temel risk analizi",
            "PDF metin çıkarma",
            "PDF rapor indirme",
        ],
    },
    "starter": {
        "name": "Başlangıç",
        "price_monthly_try": 5_000,
        "max_analysis_per_month": 20,
        "features": [
            "6 analiz modülü",
            "Yönetici özeti",
            "PDF rapor indirme",
            "Analiz geçmişi",
            "E-posta desteği",
        ],
    },
    "pro": {
        "name": "Profesyonel",
        "price_monthly_try": 15_000,
        "max_analysis_per_month": 9999,  # Sınırsız
        "features": [
            "Sınırsız analiz",
            "Öncelikli destek",
            "API erişimi",
            "Özel raporlama",
            "Tüm analiz modülleri",
        ],
    },
}


# ============================================================
# PaymentManager Sınıfı / PaymentManager Class
# ============================================================


class PaymentManager:
    """
    Plan yönetimi ve ödeme işlemleri / Plan management and payment operations.

    Kullanıcı plan limitlerini kontrol eder, plan yükseltme işlemlerini
    yönetir ve ödeme altyapısı iskeletini sağlar.

    Manages user plan limits, plan upgrades, and payment infrastructure.
    """

    def __init__(self, db_session: Any) -> None:
        """
        PaymentManager başlat / Initialize PaymentManager.

        Args:
            db_session: SQLAlchemy Session nesnesi / SQLAlchemy Session object
        """
        self.db = db_session
        logger.info("PaymentManager başlatıldı / initialized")

    # ----------------------------------------------------------
    # Plan Bilgileri / Plan Information
    # ----------------------------------------------------------

    @staticmethod
    def get_plans() -> dict[str, dict]:
        """
        Tüm planları döndür / Return all plans.

        Returns:
            Plan tanımları sözlüğü / Plan definitions dictionary
        """
        return PLANS

    @staticmethod
    def get_plan(plan_key: str) -> dict | None:
        """
        Belirli bir planı döndür / Return a specific plan.

        Args:
            plan_key: Plan anahtarı (free/starter/pro)

        Returns:
            Plan detayları veya None / Plan details or None
        """
        return PLANS.get(plan_key)

    # ----------------------------------------------------------
    # Analiz Limit Kontrolü / Analysis Limit Check
    # ----------------------------------------------------------

    def check_can_analyze(self, user: User) -> tuple[bool, str]:
        """
        Kullanıcı analiz yapabilir mi kontrol et.
        Check if user can perform analysis.

        Args:
            user: Kullanıcı nesnesi / User object

        Returns:
            (yapabilir_mi, mesaj) / (can_analyze, message)
        """
        plan_key = user.plan or "free"
        plan = PLANS.get(plan_key, PLANS["free"])
        max_analysis = plan["max_analysis_per_month"]
        current_count = user.analysis_count or 0

        # Sınırsız plan kontrolü
        if max_analysis >= 9999:
            return True, "Sınırsız analiz hakkınız var."

        if current_count >= max_analysis:
            return (
                False,
                f"Aylık analiz limitiniz ({max_analysis}) doldu. "
                f"Planınızı yükselterek daha fazla analiz yapabilirsiniz."
            )

        remaining = max_analysis - current_count
        return True, f"Kalan analiz hakkınız: {remaining}/{max_analysis}"

    def get_user_plan_info(self, user: User) -> dict:
        """
        Kullanıcının plan bilgilerini döndür.
        Return user's plan information.

        Args:
            user: Kullanıcı nesnesi / User object

        Returns:
            Plan bilgileri / Plan information dict
        """
        plan_key = user.plan or "free"
        plan = PLANS.get(plan_key, PLANS["free"])
        max_analysis = plan["max_analysis_per_month"]
        current_count = user.analysis_count or 0
        remaining = max(0, max_analysis - current_count) if max_analysis < 9999 else 9999
        has_subscription = check_active_subscription(self.db, user.id)

        return {
            "plan_key": plan_key,
            "plan_name": plan["name"],
            "price_monthly_try": plan["price_monthly_try"],
            "max_analysis_per_month": max_analysis,
            "analysis_count": current_count,
            "remaining_analyses": remaining,
            "features": plan["features"],
            "has_active_subscription": has_subscription,
            "is_unlimited": max_analysis >= 9999,
        }

    # ----------------------------------------------------------
    # Kullanım İstatistikleri / Usage Statistics
    # ----------------------------------------------------------

    def get_usage_stats(self, user: User) -> dict:
        """
        Bu ayki kullanım istatistiklerini döndür.
        Return this month's usage statistics.

        Args:
            user: Kullanıcı nesnesi / User object

        Returns:
            Kullanım istatistikleri / Usage statistics dict
        """
        plan_key = user.plan or "free"
        plan = PLANS.get(plan_key, PLANS["free"])
        max_analysis = plan["max_analysis_per_month"]
        current_count = user.analysis_count or 0

        # Son analizler / Recent analyses
        recent = get_user_analyses(self.db, user.id, limit=5)

        # Yüzde hesapla / Calculate percentage
        if max_analysis >= 9999:
            usage_percent = 0
        elif max_analysis > 0:
            usage_percent = min(100, round((current_count / max_analysis) * 100))
        else:
            usage_percent = 100

        return {
            "plan_key": plan_key,
            "plan_name": plan["name"],
            "total_used": current_count,
            "max_allowed": max_analysis,
            "usage_percent": usage_percent,
            "recent_analyses_count": len(recent),
            "is_limit_reached": current_count >= max_analysis and max_analysis < 9999,
        }

    # ----------------------------------------------------------
    # Plan Yükseltme / Plan Upgrade
    # ----------------------------------------------------------

    def upgrade_plan(
        self,
        user: User,
        new_plan: str,
        payment_method: str = "credit_card",
    ) -> tuple[bool, str]:
        """
        Kullanıcının planını yükselt (simüle ödeme).
        Upgrade user's plan (simulated payment).

        MVP'de gerçek ödeme yapılmaz, sadece plan güncellenir ve
        ödeme kaydı oluşturulur.

        Args:
            user: Kullanıcı nesnesi / User object
            new_plan: Yeni plan anahtarı (starter/pro)
            payment_method: Ödeme yöntemi / Payment method

        Returns:
            (başarılı_mı, mesaj) / (success, message)
        """
        # Plan geçerliliği / Plan validity
        if new_plan not in PLANS:
            return False, f"Geçersiz plan: {new_plan}"

        target_plan = PLANS[new_plan]
        current_plan_key = user.plan or "free"

        # Aynı plan kontrolü
        if current_plan_key == new_plan:
            return False, "Zaten bu plana sahipsiniz."

        # Düşürme kontrolü (sadece yükseltme izinli)
        plan_order = {"free": 0, "starter": 1, "pro": 2}
        if plan_order.get(new_plan, 0) <= plan_order.get(current_plan_key, 0):
            return False, "Sadece üst planlara yükseltme yapılabilir."

        # Ödeme kaydı oluştur (simüle) / Create payment record (simulated)
        now = datetime.now(timezone.utc)
        period_end = now + timedelta(days=30)

        try:
            payment = create_payment(
                self.db,
                user_id=user.id,
                amount_try=float(target_plan["price_monthly_try"]),
                plan=new_plan,
                payment_method=payment_method,
                period_start=now,
                period_end=period_end,
            )

            # MVP: Ödemeyi otomatik onayla / Auto-approve payment in MVP
            update_payment_status(
                self.db, payment.id,
                status="completed",
                transaction_id=f"SIM_{int(now.timestamp())}",
            )

            # Kullanıcı planını güncelle / Update user plan
            new_max = target_plan["max_analysis_per_month"]
            update_user(
                self.db, user.id,
                plan=new_plan,
                max_analysis_per_month=new_max,
                analysis_count=0,  # Yeni plan → sayaç sıfırla
            )

            logger.info(
                f"Plan yükseltildi / Plan upgraded: user_id={user.id}, "
                f"{current_plan_key} → {new_plan}"
            )
            return True, f"Planınız {target_plan['name']} olarak güncellendi!"

        except Exception as e:
            logger.error(f"Plan yükseltme hatası / Upgrade error: {e}", exc_info=True)
            return False, f"Plan yükseltme sırasında hata: {e}"

    # ----------------------------------------------------------
    # Plan Karşılaştırma / Plan Comparison
    # ----------------------------------------------------------

    @staticmethod
    def get_plan_comparison() -> list[dict]:
        """
        Plan karşılaştırma tablosu verisi döndür.
        Return plan comparison table data.

        Returns:
            Karşılaştırma listesi / Comparison list
        """
        comparison = []
        for key, plan in PLANS.items():
            max_a = plan["max_analysis_per_month"]
            comparison.append({
                "plan_key": key,
                "plan_name": plan["name"],
                "price": f"{plan['price_monthly_try']:,.0f} ₺/ay" if plan["price_monthly_try"] > 0 else "Ücretsiz",
                "analysis_limit": "Sınırsız" if max_a >= 9999 else str(max_a),
                "features": plan["features"],
            })
        return comparison

    # ----------------------------------------------------------
    # Ödeme Entegrasyonu Placeholder'ları / Payment Integration Placeholders
    # ----------------------------------------------------------

    def _process_payment_iyzico(
        self, user: User, amount: float, card_info: dict
    ) -> bool:
        """
        iyzico ödeme entegrasyonu — TODO.
        iyzico payment integration — TODO.

        Args:
            user: Kullanıcı / User
            amount: Tutar (TL) / Amount (TRY)
            card_info: Kart bilgileri / Card details

        Raises:
            NotImplementedError: v2'de implement edilecek
        """
        raise NotImplementedError(
            "iyzico entegrasyonu Modül 8 v2'de implement edilecek / "
            "iyzico integration will be implemented in Module 8 v2"
        )

    def _process_payment_paytr(
        self, user: User, amount: float, card_info: dict
    ) -> bool:
        """
        PayTR ödeme entegrasyonu — TODO.
        PayTR payment integration — TODO.

        Raises:
            NotImplementedError: v2'de implement edilecek
        """
        raise NotImplementedError(
            "PayTR entegrasyonu Modül 8 v2'de implement edilecek / "
            "PayTR integration will be implemented in Module 8 v2"
        )
