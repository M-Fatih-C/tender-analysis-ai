"""
TenderAI Audit Log Sistemi / Audit Log System.

Kullanıcı işlemlerini takip eder — KVKK uyumluluk.
"""

import json
import logging
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """İzlenen işlem türleri."""
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    ANALYSIS_START = "analysis_start"
    ANALYSIS_COMPLETE = "analysis_complete"
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    REPORT_EXPORT = "report_export"
    PROFILE_UPDATE = "profile_update"
    PASSWORD_CHANGE = "password_change"
    SETTINGS_CHANGE = "settings_change"
    DATA_EXPORT = "data_export"  # KVKK
    DATA_DELETE = "data_delete"  # KVKK
    PAYMENT = "payment"
    CHAT_MESSAGE = "chat_message"


def log_audit(
    db: Session,
    user_id: int,
    action: str,
    details: str = "",
    ip_address: str = "",
    resource_type: str = "",
    resource_id: int | None = None,
) -> None:
    """
    Audit log kaydı oluştur.

    Args:
        db: Database session
        user_id: İşlemi yapan kullanıcı ID
        action: İşlem türü (AuditAction enum)
        details: Ek detaylar (JSON string)
        ip_address: Kullanıcı IP adresi
        resource_type: İlgili kaynak türü (analysis, chat, profile vb.)
        resource_id: İlgili kaynak ID
    """
    try:
        from src.database.models import Base

        # AuditLog tablosu yoksa oluştur
        if not _ensure_audit_table(db):
            return

        db.execute(
            _AUDIT_TABLE.insert().values(
                user_id=user_id,
                action=action,
                details=details[:2000] if details else "",
                ip_address=ip_address[:45] if ip_address else "",
                resource_type=resource_type[:50] if resource_type else "",
                resource_id=resource_id,
                created_at=datetime.utcnow(),
            )
        )
        db.commit()
        logger.debug(f"Audit: user={user_id} action={action}")
    except Exception as e:
        logger.warning(f"Audit log hatası: {e}")


def get_user_audit_logs(
    db: Session, user_id: int, limit: int = 50
) -> list[dict]:
    """Kullanıcının audit log'larını getir."""
    try:
        if not _ensure_audit_table(db):
            return []
        rows = (
            db.execute(
                _AUDIT_TABLE.select()
                .where(_AUDIT_TABLE.c.user_id == user_id)
                .order_by(_AUDIT_TABLE.c.created_at.desc())
                .limit(limit)
            )
            .fetchall()
        )
        return [
            {
                "id": r.id,
                "action": r.action,
                "details": r.details,
                "ip_address": r.ip_address,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "created_at": r.created_at,
            }
            for r in rows
        ]
    except Exception as e:
        logger.warning(f"Audit log okuma hatası: {e}")
        return []


# ==============================================================
# KVKK Modülü
# ==============================================================

def export_user_data(db: Session, user_id: int) -> dict:
    """
    KVKK — Kullanıcının tüm verilerini dışa aktar.
    Kullanıcı kişisel verilerinin bir kopyasını alabilir.
    """
    data = {"user_id": user_id, "export_date": datetime.utcnow().isoformat()}

    try:
        from src.database.db import get_user_analyses, get_company_profile

        # Analizler
        analyses = get_user_analyses(db, user_id, limit=1000)
        data["analyses"] = [
            {
                "id": a.id, "file_name": a.file_name,
                "risk_score": a.risk_score, "risk_level": a.risk_level,
                "created_at": str(a.created_at),
            }
            for a in analyses
        ]

        # Firma profili
        profile = get_company_profile(db, user_id)
        if profile:
            data["company_profile"] = {
                "company_name": profile.company_name,
                "tax_id": profile.tax_id,
                "city": profile.city,
                "employee_count": profile.employee_count,
            }

        # Audit logları
        data["audit_logs"] = get_user_audit_logs(db, user_id, limit=500)

        log_audit(db, user_id, AuditAction.DATA_EXPORT, "KVKK veri dışa aktarma")

    except Exception as e:
        logger.error(f"KVKK veri dışa aktarma hatası: {e}")
        data["error"] = str(e)

    return data


def delete_user_data(db: Session, user_id: int) -> bool:
    """
    KVKK — Kullanıcının tüm verilerini sil (unutulma hakkı).
    """
    try:
        from src.database.models import Analysis, CompanyProfile, ChatMessage, Notification

        # Analizleri sil
        db.query(Analysis).filter(Analysis.user_id == user_id).delete()
        # Firma profili
        db.query(CompanyProfile).filter(CompanyProfile.user_id == user_id).delete()
        # Chat mesajları
        db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
        # Bildirimler
        db.query(Notification).filter(Notification.user_id == user_id).delete()
        # Audit log — son kayıt
        log_audit(db, user_id, AuditAction.DATA_DELETE, "KVKK veri silme talebi")

        db.commit()
        logger.info(f"KVKK veri silme tamamlandı: user_id={user_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"KVKK veri silme hatası: {e}")
        return False


# ==============================================================
# Audit Table (SQLAlchemy Core — model bağımlılığı olmadan)
# ==============================================================

from sqlalchemy import Table, MetaData
_metadata = MetaData()

_AUDIT_TABLE = Table(
    "audit_logs", _metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, nullable=False, index=True),
    Column("action", String(50), nullable=False, index=True),
    Column("details", Text, default=""),
    Column("ip_address", String(45), default=""),
    Column("resource_type", String(50), default=""),
    Column("resource_id", Integer, nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow, index=True),
)


def _ensure_audit_table(db: Session) -> bool:
    """Audit log tablosunu oluştur (yoksa)."""
    try:
        engine = db.get_bind()
        _AUDIT_TABLE.create(engine, checkfirst=True)
        return True
    except Exception as e:
        logger.warning(f"Audit table oluşturulamadı: {e}")
        return False
