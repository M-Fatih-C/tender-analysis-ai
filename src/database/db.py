"""
TenderAI Veritabanı Bağlantı ve CRUD Yönetimi / Database Connection & CRUD Management.

SQLAlchemy engine, session yönetimi ve tüm CRUD operasyonlarını sağlar.
Provides SQLAlchemy engine, session management, and all CRUD operations.

DB dosyası: data/tenderai.db (SQLite)
"""

import json
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker

from src.database.models import (
    Base,
    User,
    Analysis,
    Payment,
    AnalysisReport,
)

logger = logging.getLogger(__name__)

# Varsayılan DB yolu / Default DB path
_DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "tenderai.db"
_DEFAULT_DB_URL = f"sqlite:///{_DEFAULT_DB_PATH}"


def _utcnow() -> datetime:
    """UTC şu an / UTC now."""
    return datetime.now(timezone.utc)


# ============================================================
# DatabaseManager Sınıfı / DatabaseManager Class
# ============================================================


class DatabaseManager:
    """
    Veritabanı bağlantı yöneticisi / Database connection manager.

    SQLite veritabanı bağlantısını, session yönetimini
    ve tablo oluşturma işlemlerini sağlar.

    Manages SQLite database connection, session management,
    and table creation operations.
    """

    def __init__(self, database_url: str | None = None) -> None:
        """
        DatabaseManager başlat / Initialize DatabaseManager.

        Args:
            database_url: Veritabanı URL'si / Database URL
                          Varsayılan: sqlite:///data/tenderai.db
        """
        self.database_url = database_url or _DEFAULT_DB_URL

        # data/ klasörünü oluştur / Create data/ directory
        if self.database_url.startswith("sqlite:///"):
            db_path = Path(self.database_url.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)

        self._engine = create_engine(
            self.database_url,
            echo=False,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {},
        )
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
        )

        logger.info(f"DatabaseManager başlatıldı / initialized: {self.database_url}")

    @property
    def engine(self):
        """SQLAlchemy engine."""
        return self._engine

    def init_db(self) -> None:
        """
        Veritabanı tablolarını oluştur / Create database tables.

        Tüm Base'den türetilen modellerin tablolarını oluşturur.
        Creates tables for all models derived from Base.
        """
        Base.metadata.create_all(bind=self._engine)
        logger.info("Veritabanı tabloları oluşturuldu / Database tables created")

    @contextmanager
    def get_db(self) -> Generator[Session, None, None]:
        """
        Veritabanı session context manager.

        Otomatik commit/rollback ve session kapatma sağlar.
        Provides automatic commit/rollback and session closing.

        Yields:
            SQLAlchemy Session nesnesi / SQLAlchemy Session object

        Examples:
            >>> with db_manager.get_db() as db:
            ...     user = create_user(db, ...)
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self) -> None:
        """Veritabanı engine'i kapat / Close database engine."""
        if self._engine:
            self._engine.dispose()
            logger.info("Veritabanı bağlantısı kapatıldı / Database connection closed")


# ============================================================
# Kullanıcı CRUD İşlemleri / User CRUD Operations
# ============================================================


def create_user(
    db: Session,
    email: str,
    password_hash: str,
    full_name: str,
    company_name: str | None = None,
    phone: str | None = None,
) -> User:
    """
    Yeni kullanıcı oluştur / Create new user.

    Args:
        db: Veritabanı session / Database session
        email: E-posta adresi / Email address
        password_hash: Hashlenmiş parola / Hashed password
        full_name: Tam isim / Full name
        company_name: Şirket adı (opsiyonel) / Company name
        phone: Telefon (opsiyonel) / Phone

    Returns:
        Oluşturulan kullanıcı / Created user
    """
    user = User(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        company_name=company_name,
        phone=phone,
    )
    db.add(user)
    db.flush()
    logger.info(f"Kullanıcı oluşturuldu / User created: {email}")
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    E-posta ile kullanıcı getir / Get user by email.

    Args:
        db: Veritabanı session
        email: E-posta adresi

    Returns:
        Kullanıcı veya None / User or None
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    ID ile kullanıcı getir / Get user by ID.

    Args:
        db: Veritabanı session
        user_id: Kullanıcı ID

    Returns:
        Kullanıcı veya None / User or None
    """
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, **kwargs) -> User | None:
    """
    Kullanıcı bilgilerini güncelle / Update user information.

    Args:
        db: Veritabanı session
        user_id: Kullanıcı ID
        **kwargs: Güncellenecek alanlar / Fields to update

    Returns:
        Güncellenen kullanıcı veya None / Updated user or None
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)

    user.updated_at = _utcnow()
    db.flush()
    logger.info(f"Kullanıcı güncellendi / User updated: id={user_id}")
    return user


def increment_analysis_count(db: Session, user_id: int) -> User | None:
    """
    Kullanıcının analiz sayısını 1 artır / Increment user's analysis count.

    Args:
        db: Veritabanı session
        user_id: Kullanıcı ID

    Returns:
        Güncellenen kullanıcı / Updated user
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    user.analysis_count = (user.analysis_count or 0) + 1
    user.updated_at = _utcnow()
    db.flush()
    return user


def check_analysis_limit(db: Session, user_id: int) -> bool:
    """
    Kullanıcının aylık analiz limitini aşıp aşmadığını kontrol et.
    Check if user has exceeded monthly analysis limit.

    Args:
        db: Veritabanı session
        user_id: Kullanıcı ID

    Returns:
        True ise limit aşılmış / True if limit exceeded
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return True  # Kullanıcı yoksa engelle

    return user.analysis_count >= user.max_analysis_per_month


# ============================================================
# Analiz CRUD İşlemleri / Analysis CRUD Operations
# ============================================================


def create_analysis(
    db: Session,
    user_id: int,
    file_name: str,
    file_size_mb: float | None = None,
    total_pages: int | None = None,
) -> Analysis:
    """
    Yeni analiz kaydı oluştur / Create new analysis record.

    Args:
        db: Veritabanı session
        user_id: Kullanıcı ID
        file_name: PDF dosya adı / PDF filename
        file_size_mb: Dosya boyutu (MB) / File size
        total_pages: Toplam sayfa / Total pages

    Returns:
        Oluşturulan analiz / Created analysis
    """
    analysis = Analysis(
        user_id=user_id,
        file_name=file_name,
        file_size_mb=file_size_mb,
        total_pages=total_pages,
        status="pending",
    )
    db.add(analysis)
    db.flush()
    logger.info(f"Analiz oluşturuldu / Analysis created: id={analysis.id}, file={file_name}")
    return analysis


def update_analysis_result(
    db: Session,
    analysis_id: int,
    risk_score: int | None = None,
    risk_level: str | None = None,
    result_json: dict | None = None,
    executive_summary: str | None = None,
    tokens_used: int = 0,
    cost_usd: float = 0.0,
    analysis_duration_seconds: float | None = None,
    status: str = "completed",
) -> Analysis | None:
    """
    Analiz sonucunu güncelle / Update analysis result.

    Args:
        db: Veritabanı session
        analysis_id: Analiz ID
        risk_score: Risk skoru (0-100)
        risk_level: Risk seviyesi
        result_json: Tüm analiz sonucu (dict → JSON string)
        executive_summary: Yönetici özeti metni
        tokens_used: Kullanılan token
        cost_usd: Maliyet (USD)
        analysis_duration_seconds: Analiz süresi (sn)
        status: Durum (completed/failed)

    Returns:
        Güncellenen analiz / Updated analysis
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        return None

    analysis.status = status
    analysis.risk_score = risk_score
    analysis.risk_level = risk_level
    analysis.tokens_used = tokens_used
    analysis.cost_usd = cost_usd
    analysis.analysis_duration_seconds = analysis_duration_seconds
    analysis.completed_at = _utcnow()

    if result_json is not None:
        analysis.result_json = json.dumps(result_json, ensure_ascii=False, default=str)

    if executive_summary is not None:
        analysis.executive_summary = executive_summary

    db.flush()
    logger.info(f"Analiz güncellendi / Analysis updated: id={analysis_id}, status={status}")
    return analysis


def get_analysis_by_id(db: Session, analysis_id: int) -> Analysis | None:
    """
    ID ile analiz getir / Get analysis by ID.

    Args:
        db: Veritabanı session
        analysis_id: Analiz ID

    Returns:
        Analiz veya None / Analysis or None
    """
    return db.query(Analysis).filter(Analysis.id == analysis_id).first()


def get_user_analyses(
    db: Session,
    user_id: int,
    limit: int = 20,
    offset: int = 0,
) -> list[Analysis]:
    """
    Kullanıcının analizlerini getir / Get user's analyses.

    Args:
        db: Veritabanı session
        user_id: Kullanıcı ID
        limit: Sayfa boyutu / Page size
        offset: Başlangıç ofseti / Start offset

    Returns:
        Analiz listesi / List of analyses
    """
    return (
        db.query(Analysis)
        .filter(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_analysis_stats(db: Session, user_id: int) -> dict:
    """
    Kullanıcının analiz istatistiklerini getir / Get user's analysis stats.

    Args:
        db: Veritabanı session
        user_id: Kullanıcı ID

    Returns:
        İstatistik sözlüğü / Statistics dictionary
        {
            "total_analyses": int,
            "completed_analyses": int,
            "average_risk_score": float | None,
            "total_tokens_used": int,
            "total_cost_usd": float,
        }
    """
    total = db.query(func.count(Analysis.id)).filter(
        Analysis.user_id == user_id
    ).scalar() or 0

    completed = db.query(func.count(Analysis.id)).filter(
        Analysis.user_id == user_id,
        Analysis.status == "completed",
    ).scalar() or 0

    avg_risk = db.query(func.avg(Analysis.risk_score)).filter(
        Analysis.user_id == user_id,
        Analysis.risk_score.isnot(None),
    ).scalar()

    total_tokens = db.query(func.sum(Analysis.tokens_used)).filter(
        Analysis.user_id == user_id,
    ).scalar() or 0

    total_cost = db.query(func.sum(Analysis.cost_usd)).filter(
        Analysis.user_id == user_id,
    ).scalar() or 0.0

    return {
        "total_analyses": total,
        "completed_analyses": completed,
        "average_risk_score": round(avg_risk, 1) if avg_risk is not None else None,
        "total_tokens_used": total_tokens,
        "total_cost_usd": round(total_cost, 4),
    }


# ============================================================
# Ödeme CRUD İşlemleri / Payment CRUD Operations
# ============================================================


def create_payment(
    db: Session,
    user_id: int,
    amount_try: float,
    plan: str,
    payment_method: str | None = None,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
) -> Payment:
    """
    Yeni ödeme kaydı oluştur / Create new payment record.

    Args:
        db: Veritabanı session
        user_id: Kullanıcı ID
        amount_try: Tutar (TL) / Amount (TRY)
        plan: Plan adı / Plan name
        payment_method: Ödeme yöntemi / Payment method
        period_start: Dönem başlangıcı / Period start
        period_end: Dönem bitişi / Period end

    Returns:
        Oluşturulan ödeme / Created payment
    """
    payment = Payment(
        user_id=user_id,
        amount_try=amount_try,
        plan=plan,
        payment_method=payment_method,
        period_start=period_start,
        period_end=period_end,
    )
    db.add(payment)
    db.flush()
    logger.info(f"Ödeme oluşturuldu / Payment created: id={payment.id}, {amount_try}₺")
    return payment


def update_payment_status(
    db: Session,
    payment_id: int,
    status: str,
    transaction_id: str | None = None,
) -> Payment | None:
    """
    Ödeme durumunu güncelle / Update payment status.

    Args:
        db: Veritabanı session
        payment_id: Ödeme ID
        status: Yeni durum / New status (completed/failed/refunded)
        transaction_id: İşlem ID / Transaction ID

    Returns:
        Güncellenen ödeme / Updated payment
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        return None

    payment.payment_status = status
    if transaction_id:
        payment.transaction_id = transaction_id

    db.flush()
    logger.info(f"Ödeme güncellendi / Payment updated: id={payment_id}, status={status}")
    return payment


def get_user_payments(db: Session, user_id: int) -> list[Payment]:
    """
    Kullanıcının ödemelerini getir / Get user's payments.

    Args:
        db: Veritabanı session
        user_id: Kullanıcı ID

    Returns:
        Ödeme listesi / List of payments
    """
    return (
        db.query(Payment)
        .filter(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .all()
    )


def check_active_subscription(db: Session, user_id: int) -> bool:
    """
    Kullanıcının aktif aboneliği var mı kontrol et.
    Check if user has an active subscription.

    Args:
        db: Veritabanı session
        user_id: Kullanıcı ID

    Returns:
        True ise aktif abonelik var / True if active subscription exists
    """
    now = _utcnow()
    active = (
        db.query(Payment)
        .filter(
            Payment.user_id == user_id,
            Payment.payment_status == "completed",
            Payment.period_end >= now,
        )
        .first()
    )
    return active is not None


# ============================================================
# Rapor CRUD İşlemleri / Report CRUD Operations
# ============================================================


def create_report(
    db: Session,
    analysis_id: int,
    report_path: str,
    report_type: str = "full",
) -> AnalysisReport:
    """
    Yeni rapor kaydı oluştur / Create new report record.

    Args:
        db: Veritabanı session
        analysis_id: Analiz ID
        report_path: Rapor dosya yolu / Report file path
        report_type: Rapor tipi (full/summary/risk_only)

    Returns:
        Oluşturulan rapor / Created report
    """
    report = AnalysisReport(
        analysis_id=analysis_id,
        report_path=report_path,
        report_type=report_type,
    )
    db.add(report)
    db.flush()
    logger.info(f"Rapor oluşturuldu / Report created: id={report.id}")
    return report
