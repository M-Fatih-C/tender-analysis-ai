"""
TenderAI Kullanıcı Kimlik Doğrulama / User Authentication.

bcrypt ile şifre hashleme, Streamlit session state ile
oturum yönetimi, kullanıcı kayıt ve giriş işlemlerini sağlar.

Provides password hashing with bcrypt, session management
with Streamlit session state, user registration and login.
"""

import functools
import logging
import re
import time
from collections import defaultdict
from typing import Any, Callable

import bcrypt

from src.database.db import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user,
)
from src.database.models import User

logger = logging.getLogger(__name__)

# ============================================================
# E-posta regex / Email regex
# ============================================================

_EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

# ============================================================
# Rate Limiting Sabitleri / Rate Limiting Constants
# ============================================================

_MAX_LOGIN_ATTEMPTS = 5
_LOCKOUT_SECONDS = 300  # 5 dakika / 5 minutes


# ============================================================
# AuthManager Sınıfı / AuthManager Class
# ============================================================


class AuthManager:
    """
    Kullanıcı kimlik doğrulama yöneticisi / User authentication manager.

    Kullanıcı kayıt, giriş, şifre yönetimi ve
    Streamlit session state tabanlı oturum yönetimi sağlar.

    Manages user registration, login, password management,
    and Streamlit session state-based session management.
    """

    def __init__(self, db_session: Any) -> None:
        """
        AuthManager başlat / Initialize AuthManager.

        Args:
            db_session: SQLAlchemy Session nesnesi / SQLAlchemy Session object
        """
        self.db = db_session

        # Rate limiting: email -> (attempt_count, first_attempt_time)
        self._login_attempts: dict[str, list[float]] = defaultdict(list)

        logger.info("AuthManager başlatıldı / initialized")

    # ----------------------------------------------------------
    # Şifre Yönetimi / Password Management
    # ----------------------------------------------------------

    @staticmethod
    def hash_password(password: str) -> str:
        """
        bcrypt ile şifre hashle / Hash password with bcrypt.

        Args:
            password: Düz metin şifre / Plain text password

        Returns:
            Hashlenmiş şifre / Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Şifre doğrula / Verify password against hash.

        Args:
            password: Düz metin şifre / Plain text password
            hashed: Hashlenmiş şifre / Hashed password

        Returns:
            Şifre doğru mu / Is password correct
        """
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                hashed.encode("utf-8"),
            )
        except Exception as e:
            logger.error(f"Şifre doğrulama hatası / Password verification error: {e}")
            return False

    # ----------------------------------------------------------
    # Validasyon / Validation
    # ----------------------------------------------------------

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        E-posta format validasyonu / Email format validation.

        Args:
            email: E-posta adresi / Email address

        Returns:
            Geçerli mi / Is valid
        """
        if not email or not isinstance(email, str):
            return False
        return bool(_EMAIL_PATTERN.match(email.strip()))

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Şifre güçlülük kontrolü / Password strength validation.

        Kurallar / Rules:
            - En az 8 karakter / At least 8 characters
            - En az 1 büyük harf / At least 1 uppercase
            - En az 1 küçük harf / At least 1 lowercase
            - En az 1 rakam / At least 1 digit

        Args:
            password: Şifre / Password

        Returns:
            (geçerli_mi, hata_mesajı) / (is_valid, error_message)
        """
        if not password:
            return False, "Şifre boş olamaz / Password cannot be empty"

        if len(password) < 8:
            return False, "Şifre en az 8 karakter olmalı / Password must be at least 8 characters"

        if not re.search(r"[A-Z]", password):
            return False, "Şifre en az 1 büyük harf içermeli / Password must contain at least 1 uppercase letter"

        if not re.search(r"[a-z]", password):
            return False, "Şifre en az 1 küçük harf içermeli / Password must contain at least 1 lowercase letter"

        if not re.search(r"\d", password):
            return False, "Şifre en az 1 rakam içermeli / Password must contain at least 1 digit"

        return True, ""

    # ----------------------------------------------------------
    # Kayıt / Registration
    # ----------------------------------------------------------

    def register(
        self,
        email: str,
        password: str,
        full_name: str,
        company_name: str | None = None,
    ) -> tuple[bool, str, User | None]:
        """
        Yeni kullanıcı kaydı / Register new user.

        Args:
            email: E-posta adresi / Email address
            password: Şifre / Password
            full_name: Tam isim / Full name
            company_name: Şirket adı (opsiyonel) / Company name

        Returns:
            (başarılı_mı, mesaj, user_objesi) / (success, message, user_object)
        """
        try:
            # E-posta validasyonu / Email validation
            email = email.strip().lower()
            if not self.validate_email(email):
                return False, "Geçersiz e-posta formatı / Invalid email format", None

            # E-posta zaten kayıtlı mı / Is email already registered?
            existing = get_user_by_email(self.db, email)
            if existing:
                return False, "Bu e-posta adresi zaten kayıtlı / This email is already registered", None

            # Şifre validasyonu / Password validation
            is_valid, msg = self.validate_password(password)
            if not is_valid:
                return False, msg, None

            # İsim validasyonu / Name validation
            if not full_name or not full_name.strip():
                return False, "İsim boş olamaz / Name cannot be empty", None

            # Kullanıcı oluştur / Create user
            password_hash = self.hash_password(password)
            user = create_user(
                self.db,
                email=email,
                password_hash=password_hash,
                full_name=full_name.strip(),
                company_name=company_name.strip() if company_name else None,
            )

            logger.info(f"Yeni kullanıcı kaydedildi / New user registered: {email}")
            return True, "Kayıt başarılı / Registration successful", user

        except Exception as e:
            logger.error(f"Kayıt hatası / Registration error: {e}", exc_info=True)
            return False, f"Kayıt sırasında hata oluştu / Error during registration: {e}", None

    # ----------------------------------------------------------
    # Giriş / Login
    # ----------------------------------------------------------

    def login(self, email: str, password: str) -> tuple[bool, str, User | None]:
        """
        Kullanıcı girişi / User login.

        Rate limiting: 5 başarısız denemeden sonra 5 dakika kilitleme.
        Rate limiting: locks for 5 minutes after 5 failed attempts.

        Args:
            email: E-posta adresi / Email address
            password: Şifre / Password

        Returns:
            (başarılı_mı, mesaj, user_objesi) / (success, message, user_object)
        """
        try:
            email = email.strip().lower()

            # Rate limiting kontrolü / Rate limiting check
            if self._is_rate_limited(email):
                return (
                    False,
                    "Çok fazla başarısız deneme. 5 dakika sonra tekrar deneyin / "
                    "Too many failed attempts. Try again in 5 minutes",
                    None,
                )

            # Kullanıcıyı bul / Find user
            user = get_user_by_email(self.db, email)
            if not user:
                self._record_failed_attempt(email)
                return False, "E-posta veya şifre hatalı / Invalid email or password", None

            # Aktif mi kontrol et / Check if active
            if not user.is_active:
                return False, "Hesap devre dışı / Account is deactivated", None

            # Şifre doğrula / Verify password
            if not self.verify_password(password, user.password_hash):
                self._record_failed_attempt(email)
                return False, "E-posta veya şifre hatalı / Invalid email or password", None

            # Başarılı — rate limit sıfırla / Success — reset rate limit
            self._clear_attempts(email)

            logger.info(f"Kullanıcı giriş yaptı / User logged in: {email}")
            return True, "Giriş başarılı / Login successful", user

        except Exception as e:
            logger.error(f"Giriş hatası / Login error: {e}", exc_info=True)
            return False, f"Giriş sırasında hata oluştu / Error during login: {e}", None

    # ----------------------------------------------------------
    # Streamlit Session Yönetimi / Session Management
    # ----------------------------------------------------------

    @staticmethod
    def set_session(user: User) -> None:
        """
        Streamlit session state'e kullanıcı bilgilerini yaz.
        Write user info to Streamlit session state.

        Args:
            user: User nesnesi / User object
        """
        try:
            import streamlit as st
            st.session_state["authenticated"] = True
            st.session_state["user_id"] = user.id
            st.session_state["user_email"] = user.email
            st.session_state["user_name"] = user.full_name
            st.session_state["user_plan"] = user.plan
        except ImportError:
            logger.warning("Streamlit yüklü değil / Streamlit not installed")

    @staticmethod
    def get_current_user_id() -> int | None:
        """
        Streamlit session'dan aktif kullanıcı ID'sini al.
        Get active user ID from Streamlit session.

        Returns:
            Kullanıcı ID veya None / User ID or None
        """
        try:
            import streamlit as st
            if st.session_state.get("authenticated"):
                return st.session_state.get("user_id")
        except ImportError:
            pass
        return None

    def get_current_user(self) -> User | None:
        """
        Streamlit session'dan aktif kullanıcıyı al.
        Get active user from Streamlit session.

        Returns:
            User nesnesi veya None / User object or None
        """
        user_id = self.get_current_user_id()
        if user_id:
            return get_user_by_id(self.db, user_id)
        return None

    @staticmethod
    def logout() -> None:
        """
        Oturumu kapat, session temizle.
        Logout, clear session state.
        """
        try:
            import streamlit as st
            keys = [
                "authenticated", "user_id", "user_email",
                "user_name", "user_plan",
            ]
            for key in keys:
                st.session_state.pop(key, None)
            logger.info("Kullanıcı çıkış yaptı / User logged out")
        except ImportError:
            logger.warning("Streamlit yüklü değil / Streamlit not installed")

    @staticmethod
    def is_authenticated() -> bool:
        """
        Kullanıcı giriş yapmış mı kontrol et.
        Check if user is authenticated.

        Returns:
            Giriş yapmış mı / Is authenticated
        """
        try:
            import streamlit as st
            return st.session_state.get("authenticated", False)
        except ImportError:
            return False

    # ----------------------------------------------------------
    # Şifre Değiştirme / Change Password
    # ----------------------------------------------------------

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
    ) -> tuple[bool, str]:
        """
        Şifre değiştir / Change password.

        Args:
            user_id: Kullanıcı ID
            old_password: Mevcut şifre / Current password
            new_password: Yeni şifre / New password

        Returns:
            (başarılı_mı, mesaj) / (success, message)
        """
        try:
            user = get_user_by_id(self.db, user_id)
            if not user:
                return False, "Kullanıcı bulunamadı / User not found"

            # Eski şifreyi doğrula / Verify old password
            if not self.verify_password(old_password, user.password_hash):
                return False, "Mevcut şifre hatalı / Current password is incorrect"

            # Yeni şifre validasyonu / New password validation
            is_valid, msg = self.validate_password(new_password)
            if not is_valid:
                return False, msg

            # Eski ve yeni şifre aynı mı / Is old and new password same?
            if old_password == new_password:
                return False, "Yeni şifre eskisiyle aynı olamaz / New password cannot be the same as old"

            # Şifreyi güncelle / Update password
            new_hash = self.hash_password(new_password)
            update_user(self.db, user_id, password_hash=new_hash)

            logger.info(f"Şifre değiştirildi / Password changed: user_id={user_id}")
            return True, "Şifre başarıyla değiştirildi / Password changed successfully"

        except Exception as e:
            logger.error(f"Şifre değiştirme hatası / Password change error: {e}", exc_info=True)
            return False, f"Şifre değiştirme sırasında hata / Error during password change: {e}"

    # ----------------------------------------------------------
    # Rate Limiting
    # ----------------------------------------------------------

    def _is_rate_limited(self, email: str) -> bool:
        """Son 5 dakikada 5'ten fazla başarısız deneme var mı / Check rate limit."""
        now = time.time()
        attempts = self._login_attempts.get(email, [])
        # Eski denemeleri temizle / Clean old attempts
        recent = [t for t in attempts if now - t < _LOCKOUT_SECONDS]
        self._login_attempts[email] = recent
        return len(recent) >= _MAX_LOGIN_ATTEMPTS

    def _record_failed_attempt(self, email: str) -> None:
        """Başarısız denemeyi kaydet / Record failed attempt."""
        self._login_attempts[email].append(time.time())

    def _clear_attempts(self, email: str) -> None:
        """Denemeleri sıfırla / Clear attempts."""
        self._login_attempts.pop(email, None)


# ============================================================
# login_required Decorator
# ============================================================


def login_required(func: Callable) -> Callable:
    """
    Streamlit sayfalarını korumak için decorator.
    Decorator for protecting Streamlit pages.

    Giriş yapmamış kullanıcıyı login sayfasına yönlendirir.
    Redirects unauthenticated users to the login page.

    Examples:
        @login_required
        def dashboard_page():
            st.write("Hoş geldiniz!")
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            import streamlit as st
            if not st.session_state.get("authenticated", False):
                st.warning("Bu sayfaya erişmek için giriş yapmalısınız / You must log in to access this page")
                st.stop()
                return None
        except ImportError:
            pass
        return func(*args, **kwargs)

    return wrapper
