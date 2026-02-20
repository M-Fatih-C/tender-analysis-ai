"""
TenderAI Veritabanı Modelleri / Database Models.

SQLAlchemy 2.0 ORM modelleri ile veritabanı şemasını tanımlar.
Defines database schema with SQLAlchemy 2.0 ORM models.

Tablolar / Tables:
    1. users — Kullanıcılar
    2. analyses — Analizler
    3. payments — Ödemeler
    4. analysis_reports — Oluşturulan PDF raporlar
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def _utcnow() -> datetime:
    """UTC şu an / UTC now — timezone-aware."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 deklaratif taban sınıfı / Declarative base class."""
    pass


# ============================================================
# 1. User Modeli / User Model
# ============================================================


class User(Base):
    """
    Kullanıcı modeli / User model.

    Kullanıcı bilgilerini, abonelik planını ve analiz limitlerini saklar.
    Stores user information, subscription plan, and analysis limits.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    plan = Column(String(50), default="free")  # free, starter, pro, enterprise
    analysis_count = Column(Integer, default=0)
    max_analysis_per_month = Column(Integer, default=3)  # free plan limiti
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # İlişkiler / Relationships
    analyses = relationship(
        "Analysis", back_populates="user", cascade="all, delete-orphan",
        order_by="Analysis.created_at.desc()",
    )
    payments = relationship(
        "Payment", back_populates="user", cascade="all, delete-orphan",
        order_by="Payment.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', plan='{self.plan}')>"


# ============================================================
# 2. Analysis Modeli / Analysis Model
# ============================================================


class Analysis(Base):
    """
    Analiz modeli / Analysis model.

    İhale şartname analiz sonuçlarını ve meta verilerini saklar.
    Stores tender specification analysis results and metadata.
    """

    __tablename__ = "analyses"
    __table_args__ = (
        Index("ix_analyses_user_created", "user_id", "created_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_size_mb = Column(Float, nullable=True)
    total_pages = Column(Integer, nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    risk_score = Column(Integer, nullable=True)  # 0-100
    risk_level = Column(String(50), nullable=True)  # DÜŞÜK/ORTA/YÜKSEK/ÇOK YÜKSEK
    result_json = Column(Text, nullable=True)  # Tüm analiz sonucu JSON olarak
    executive_summary = Column(Text, nullable=True)
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    analysis_duration_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    completed_at = Column(DateTime, nullable=True)

    # İlişkiler / Relationships
    user = relationship("User", back_populates="analyses")
    reports = relationship(
        "AnalysisReport", back_populates="analysis", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Analysis(id={self.id}, file='{self.file_name}', "
            f"status='{self.status}', risk_score={self.risk_score})>"
        )


# ============================================================
# 3. Payment Modeli / Payment Model
# ============================================================


class Payment(Base):
    """
    Ödeme modeli / Payment model.

    Abonelik ödemelerini ve işlem durumlarını saklar.
    Stores subscription payments and transaction statuses.
    """

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount_try = Column(Float, nullable=False)  # TL cinsinden
    plan = Column(String(50), nullable=False)
    payment_method = Column(String(50), nullable=True)  # credit_card, bank_transfer
    payment_status = Column(String(50), default="pending")  # pending, completed, failed, refunded
    transaction_id = Column(String(255), nullable=True)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    # İlişkiler / Relationships
    user = relationship("User", back_populates="payments")

    def __repr__(self) -> str:
        return (
            f"<Payment(id={self.id}, user_id={self.user_id}, "
            f"amount={self.amount_try}₺, status='{self.payment_status}')>"
        )


# ============================================================
# 4. AnalysisReport Modeli / AnalysisReport Model
# ============================================================


class AnalysisReport(Base):
    """
    Analiz raporu modeli / Analysis report model.

    Oluşturulan PDF raporların bilgilerini saklar.
    Stores information about generated PDF reports.
    """

    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    report_path = Column(String(500), nullable=False)
    report_type = Column(String(50), default="full")  # full, summary, risk_only
    generated_at = Column(DateTime, default=_utcnow)

    # İlişkiler / Relationships
    analysis = relationship("Analysis", back_populates="reports")

    def __repr__(self) -> str:
        return (
            f"<AnalysisReport(id={self.id}, analysis_id={self.analysis_id}, "
            f"type='{self.report_type}')>"
        )
