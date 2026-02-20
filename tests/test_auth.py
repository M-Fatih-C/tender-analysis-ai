"""
TenderAI Authentication Testleri / Authentication Tests.

AuthManager sınıfı için birim testleri.
Unit tests for AuthManager class.

In-memory SQLite kullanır — diske yazmaz.
Uses in-memory SQLite — no disk writes.
"""

import time
import pytest
from unittest.mock import patch, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, User
from src.database.db import create_user, get_user_by_id
from src.auth.auth import AuthManager, login_required


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
def auth(db_session):
    """AuthManager instance."""
    return AuthManager(db_session)


@pytest.fixture
def registered_user(db_session, auth):
    """Kayıtlı kullanıcı / Registered user."""
    success, msg, user = auth.register(
        email="user@test.com",
        password="Test1234",
        full_name="Test User",
        company_name="Test Co",
    )
    db_session.commit()
    return user


# ============================================================
# Password Hashing Testleri
# ============================================================


class TestPasswordHashing:
    """Şifre hashleme testleri / Password hashing tests."""

    def test_hash_password_produces_hash(self, auth) -> None:
        """Hash oluşturulmalı / Should produce hash."""
        hashed = auth.hash_password("Test1234")
        assert isinstance(hashed, str)
        assert hashed != "Test1234"
        assert len(hashed) > 20

    def test_hash_password_different_hashes(self, auth) -> None:
        """Aynı şifre farklı hash üretmeli (salt) / Same password different hashes."""
        h1 = auth.hash_password("Test1234")
        h2 = auth.hash_password("Test1234")
        assert h1 != h2  # bcrypt salt farklı

    def test_verify_password_correct(self, auth) -> None:
        """Doğru şifre True dönmeli / Correct password should return True."""
        hashed = auth.hash_password("MyPass1234")
        assert auth.verify_password("MyPass1234", hashed) is True

    def test_verify_password_incorrect(self, auth) -> None:
        """Yanlış şifre False dönmeli / Wrong password should return False."""
        hashed = auth.hash_password("MyPass1234")
        assert auth.verify_password("WrongPass", hashed) is False

    def test_verify_password_invalid_hash(self, auth) -> None:
        """Geçersiz hash False dönmeli / Invalid hash should return False."""
        assert auth.verify_password("test", "invalid_hash") is False


# ============================================================
# Email Validasyon Testleri
# ============================================================


class TestEmailValidation:
    """E-posta validasyon testleri / Email validation tests."""

    def test_valid_emails(self) -> None:
        """Geçerli e-postalar / Valid emails."""
        assert AuthManager.validate_email("user@test.com") is True
        assert AuthManager.validate_email("first.last@example.org") is True
        assert AuthManager.validate_email("user+tag@domain.co") is True

    def test_invalid_emails(self) -> None:
        """Geçersiz e-postalar / Invalid emails."""
        assert AuthManager.validate_email("") is False
        assert AuthManager.validate_email("not-an-email") is False
        assert AuthManager.validate_email("@domain.com") is False
        assert AuthManager.validate_email("user@") is False
        assert AuthManager.validate_email("user@.com") is False

    def test_none_email(self) -> None:
        """None e-posta / None email."""
        assert AuthManager.validate_email(None) is False


# ============================================================
# Password Validasyon Testleri
# ============================================================


class TestPasswordValidation:
    """Şifre validasyon testleri / Password validation tests."""

    def test_valid_password(self) -> None:
        """Geçerli şifre / Valid password."""
        valid, msg = AuthManager.validate_password("Test1234")
        assert valid is True
        assert msg == ""

    def test_too_short(self) -> None:
        """Çok kısa şifre / Too short password."""
        valid, msg = AuthManager.validate_password("Te1")
        assert valid is False
        assert "8 karakter" in msg

    def test_no_uppercase(self) -> None:
        """Büyük harf yok / No uppercase."""
        valid, msg = AuthManager.validate_password("test1234")
        assert valid is False
        assert "büyük harf" in msg

    def test_no_lowercase(self) -> None:
        """Küçük harf yok / No lowercase."""
        valid, msg = AuthManager.validate_password("TEST1234")
        assert valid is False
        assert "küçük harf" in msg

    def test_no_digit(self) -> None:
        """Rakam yok / No digit."""
        valid, msg = AuthManager.validate_password("TestTest")
        assert valid is False
        assert "rakam" in msg

    def test_empty_password(self) -> None:
        """Boş şifre / Empty password."""
        valid, msg = AuthManager.validate_password("")
        assert valid is False


# ============================================================
# Register Testleri
# ============================================================


class TestRegister:
    """Kayıt testleri / Registration tests."""

    def test_register_success(self, db_session, auth) -> None:
        """Başarılı kayıt / Successful registration."""
        success, msg, user = auth.register(
            email="new@test.com",
            password="NewPass1",
            full_name="New User",
        )
        db_session.commit()

        assert success is True
        assert "başarılı" in msg.lower()
        assert user is not None
        assert user.email == "new@test.com"
        assert user.plan == "free"

    def test_register_with_company(self, db_session, auth) -> None:
        """Şirket bilgisiyle kayıt / Registration with company."""
        success, msg, user = auth.register(
            email="corp@test.com",
            password="Corp1234",
            full_name="Corp User",
            company_name="ACME Ltd.",
        )
        db_session.commit()

        assert success is True
        assert user.company_name == "ACME Ltd."

    def test_register_invalid_email(self, auth) -> None:
        """Geçersiz e-posta / Invalid email."""
        success, msg, user = auth.register(
            email="invalid-email",
            password="Test1234",
            full_name="Test",
        )
        assert success is False
        assert user is None

    def test_register_duplicate_email(self, db_session, auth, registered_user) -> None:
        """Aynı e-posta tekrar / Duplicate email."""
        success, msg, user = auth.register(
            email="user@test.com",
            password="Test1234",
            full_name="Another User",
        )
        assert success is False
        assert "zaten kayıtlı" in msg

    def test_register_weak_password(self, auth) -> None:
        """Zayıf şifre / Weak password."""
        success, msg, user = auth.register(
            email="weak@test.com",
            password="123",
            full_name="Weak",
        )
        assert success is False
        assert user is None

    def test_register_empty_name(self, auth) -> None:
        """Boş isim / Empty name."""
        success, msg, user = auth.register(
            email="empty@test.com",
            password="Test1234",
            full_name="",
        )
        assert success is False

    def test_register_email_lowercased(self, db_session, auth) -> None:
        """E-posta küçük harfe çevrilmeli / Email should be lowercased."""
        success, msg, user = auth.register(
            email="UPPER@Test.COM",
            password="Test1234",
            full_name="Upper Case",
        )
        db_session.commit()
        assert success is True
        assert user.email == "upper@test.com"


# ============================================================
# Login Testleri
# ============================================================


class TestLogin:
    """Giriş testleri / Login tests."""

    def test_login_success(self, db_session, auth, registered_user) -> None:
        """Başarılı giriş / Successful login."""
        success, msg, user = auth.login("user@test.com", "Test1234")
        assert success is True
        assert user is not None
        assert user.id == registered_user.id

    def test_login_wrong_password(self, auth, registered_user) -> None:
        """Yanlış şifre / Wrong password."""
        success, msg, user = auth.login("user@test.com", "WrongPass1")
        assert success is False
        assert user is None

    def test_login_nonexistent_email(self, auth) -> None:
        """Olmayan e-posta / Nonexistent email."""
        success, msg, user = auth.login("nobody@test.com", "Test1234")
        assert success is False

    def test_login_inactive_user(self, db_session, auth, registered_user) -> None:
        """Devre dışı kullanıcı / Inactive user."""
        registered_user.is_active = False
        db_session.commit()

        success, msg, user = auth.login("user@test.com", "Test1234")
        assert success is False
        assert "devre dışı" in msg

    def test_login_email_case_insensitive(self, auth, registered_user) -> None:
        """E-posta büyük/küçük harf duyarsız / Email case insensitive."""
        success, msg, user = auth.login("USER@TEST.COM", "Test1234")
        assert success is True


# ============================================================
# Rate Limiting Testleri
# ============================================================


class TestRateLimiting:
    """Rate limiting testleri / Rate limiting tests."""

    def test_rate_limit_after_many_attempts(self, auth) -> None:
        """5 başarısız denemeden sonra kilitleme / Lock after 5 failed attempts."""
        for _ in range(5):
            auth.login("locked@test.com", "wrong")

        success, msg, user = auth.login("locked@test.com", "wrong")
        assert success is False
        assert "5 dakika" in msg

    def test_rate_limit_resets_on_success(self, db_session, auth, registered_user) -> None:
        """Başarılı girişle reset / Reset on successful login."""
        for _ in range(3):
            auth.login("user@test.com", "wrong")

        # Doğru şifreyle giriş
        success, msg, user = auth.login("user@test.com", "Test1234")
        assert success is True

        # Rate limit sıfırlanmış olmalı
        assert not auth._is_rate_limited("user@test.com")


# ============================================================
# Change Password Testleri
# ============================================================


class TestChangePassword:
    """Şifre değiştirme testleri / Change password tests."""

    def test_change_password_success(self, db_session, auth, registered_user) -> None:
        """Başarılı şifre değiştirme / Successful password change."""
        success, msg = auth.change_password(
            registered_user.id, "Test1234", "NewPass1"
        )
        db_session.commit()

        assert success is True
        assert "başarıyla" in msg

        # Yeni şifreyle giriş
        ok, _, _ = auth.login("user@test.com", "NewPass1")
        assert ok is True

    def test_change_password_wrong_old(self, auth, registered_user) -> None:
        """Eski şifre yanlış / Wrong old password."""
        success, msg = auth.change_password(
            registered_user.id, "WrongOld1", "NewPass1"
        )
        assert success is False

    def test_change_password_weak_new(self, auth, registered_user) -> None:
        """Yeni şifre zayıf / New password too weak."""
        success, msg = auth.change_password(
            registered_user.id, "Test1234", "123"
        )
        assert success is False

    def test_change_password_same_as_old(self, auth, registered_user) -> None:
        """Yeni şifre eskiyle aynı / New password same as old."""
        success, msg = auth.change_password(
            registered_user.id, "Test1234", "Test1234"
        )
        assert success is False
        assert "aynı" in msg

    def test_change_password_user_not_found(self, auth) -> None:
        """Olmayan kullanıcı / User not found."""
        success, msg = auth.change_password(99999, "old", "New1234x")
        assert success is False


# ============================================================
# login_required Decorator Testleri
# ============================================================


class TestLoginRequired:
    """login_required decorator testleri."""

    def test_decorator_preserves_function_name(self) -> None:
        """Fonksiyon adı korunmalı / Function name should be preserved."""

        @login_required
        def my_page():
            return "content"

        assert my_page.__name__ == "my_page"

    def test_passes_when_authenticated(self) -> None:
        """Giriş yapılmışsa fonksiyon çalışmalı / Should run when authenticated."""
        import sys
        mock_st = MagicMock()
        mock_st.session_state = {"authenticated": True}
        sys.modules["streamlit"] = mock_st

        try:
            @login_required
            def my_page():
                return "ok"

            result = my_page()
            assert result == "ok"
        finally:
            sys.modules.pop("streamlit", None)
