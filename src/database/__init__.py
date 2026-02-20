"""
TenderAI Veritabanı Paketi / Database Package.

SQLite veritabanı modelleri, bağlantı yönetimi ve CRUD operasyonları.
SQLite database models, connection management, and CRUD operations.
"""

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

__all__ = [
    "Base",
    "User",
    "Analysis",
    "Payment",
    "AnalysisReport",
    "DatabaseManager",
    "create_user",
    "get_user_by_email",
    "get_user_by_id",
    "update_user",
    "increment_analysis_count",
    "check_analysis_limit",
    "create_analysis",
    "update_analysis_result",
    "get_analysis_by_id",
    "get_user_analyses",
    "get_analysis_stats",
    "create_payment",
    "update_payment_status",
    "get_user_payments",
    "check_active_subscription",
    "create_report",
]
