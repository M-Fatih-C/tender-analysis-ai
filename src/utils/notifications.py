"""
TenderAI Bildirim Yöneticisi / Notification Manager.
"""

import logging
from src.database.db import (
    create_notification,
    get_user_notifications,
    mark_notification_read,
    get_unread_notification_count,
)

logger = logging.getLogger(__name__)


class NotificationManager:
    """Uygulama içi bildirim yönetimi."""

    def __init__(self, db_session) -> None:
        self._db = db_session

    def notify_analysis_complete(self, user_id: int, analysis_id: int, risk_score: int) -> None:
        """Analiz tamamlandı bildirimi."""
        emoji = "🟢" if risk_score <= 40 else "🟡" if risk_score <= 70 else "🔴"
        create_notification(
            self._db, user_id,
            title=f"{emoji} Analiz tamamlandı",
            message=f"Risk skoru: {risk_score}",
            type_="success",
            link="history",
        )

    def notify_plan_limit_warning(self, user_id: int, remaining: int) -> None:
        """Plan limiti uyarısı."""
        if remaining <= 3 and remaining > 0:
            create_notification(
                self._db, user_id,
                title="⚠️ Analiz limitiniz azalıyor",
                message=f"Kalan hakkınız: {remaining}. Planınızı yükseltin!",
                type_="warning",
                link="payment",
            )

    def notify_welcome(self, user_id: int) -> None:
        """Hoşgeldin bildirimi."""
        create_notification(
            self._db, user_id,
            title="🎉 TenderAI'a hoş geldiniz!",
            message="İlk ihale analizinizi yaparak platformu keşfedin.",
            type_="info",
            link="analysis",
        )

    def notify_plan_upgraded(self, user_id: int, new_plan: str) -> None:
        """Plan yükseltme bildirimi."""
        names = {"starter": "Başlangıç", "pro": "Profesyonel"}
        create_notification(
            self._db, user_id,
            title=f"✅ {names.get(new_plan, new_plan)} planına geçildi",
            message="Yeni özelliklerinizin keyfini çıkarın!",
            type_="success",
            link="dashboard",
        )

    def get_notifications(self, user_id: int, limit: int = 20) -> list:
        """Bildirimleri getir."""
        return get_user_notifications(self._db, user_id, limit=limit)

    def get_unread_count(self, user_id: int) -> int:
        """Okunmamış sayısı."""
        return get_unread_notification_count(self._db, user_id)

    def mark_as_read(self, notification_id: int) -> None:
        """Okundu yap."""
        mark_notification_read(self._db, notification_id)
