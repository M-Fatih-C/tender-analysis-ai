"""
TenderAI Veritabanı Modelleri / Database Models.

SQLAlchemy ORM modelleri ile veritabanı şemasını tanımlar.
Defines database schema with SQLAlchemy ORM models.

Bu modül Modül 4'te implement edilecektir.
This module will be implemented in Module 4.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """SQLAlchemy deklaratif taban sınıfı / SQLAlchemy declarative base class."""
    pass


class User(Base):
    """
    Kullanıcı modeli / User model.

    Kullanıcı bilgilerini ve abonelik durumunu saklar.
    Stores user information and subscription status.
    """

    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    email: str = Column(String(255), unique=True, nullable=False, index=True)
    username: str = Column(String(100), unique=True, nullable=False)
    password_hash: str = Column(String(255), nullable=False)
    full_name: str = Column(String(255), nullable=True)
    company: str = Column(String(255), nullable=True)
    is_active: bool = Column(Boolean, default=True)
    is_premium: bool = Column(Boolean, default=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # İlişkiler / Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Document(Base):
    """
    Doküman modeli / Document model.

    Yüklenen PDF dosyalarının bilgilerini saklar.
    Stores information about uploaded PDF files.
    """

    __tablename__ = "documents"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    filename: str = Column(String(255), nullable=False)
    original_filename: str = Column(String(255), nullable=False)
    file_path: str = Column(String(500), nullable=False)
    file_size: int = Column(Integer, nullable=False)
    page_count: int = Column(Integer, nullable=True)
    upload_date: datetime = Column(DateTime, default=datetime.utcnow)

    # İlişkiler / Relationships
    analysis = relationship("Analysis", back_populates="document", uselist=False)

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename='{self.original_filename}')>"


class Analysis(Base):
    """
    Analiz modeli / Analysis model.

    İhale şartname analiz sonuçlarını saklar.
    Stores tender specification analysis results.
    """

    __tablename__ = "analyses"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id: int = Column(Integer, ForeignKey("documents.id"), nullable=False)
    status: str = Column(String(50), default="pending")  # pending, processing, completed, failed
    risk_score: float = Column(Float, nullable=True)
    risk_analysis: str = Column(Text, nullable=True)  # JSON string
    required_documents: str = Column(Text, nullable=True)  # JSON string
    penalty_clauses: str = Column(Text, nullable=True)  # JSON string
    financial_summary: str = Column(Text, nullable=True)  # JSON string
    timeline_analysis: str = Column(Text, nullable=True)  # JSON string
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    completed_at: datetime = Column(DateTime, nullable=True)

    # İlişkiler / Relationships
    user = relationship("User", back_populates="analyses")
    document = relationship("Document", back_populates="analysis")

    def __repr__(self) -> str:
        return f"<Analysis(id={self.id}, status='{self.status}', risk_score={self.risk_score})>"
