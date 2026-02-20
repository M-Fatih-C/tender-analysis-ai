"""
TenderAI Giriş / Kayıt Sayfası / Login / Registration Page.

E-posta + şifre tabanlı kimlik doğrulama arayüzü.
Email + password based authentication interface.
"""

import streamlit as st

from src.database.db import DatabaseManager
from src.auth.auth import AuthManager


def render_login_page() -> None:
    """Giriş/Kayıt sayfasını render et / Render login/registration page."""

    # Ortalanmış düzen / Centered layout
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        # Logo ve başlık / Logo and title
        st.markdown(
            """
            <div style="text-align:center; padding: 2rem 0 1.5rem;">
                <h1 style="font-size: 2.5rem; margin-bottom: 0.2rem;">📋 TenderAI</h1>
                <p style="font-size: 1.1rem; opacity: 0.7; margin-top: 0;">
                    İhale Şartname Analiz Platformu
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Tab'lar / Tabs
        tab_login, tab_register = st.tabs(["🔐 Giriş Yap", "📝 Kayıt Ol"])

        # ── Giriş Tab'ı / Login Tab ──

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("#### Hesabınıza giriş yapın")

                login_email = st.text_input(
                    "E-posta", placeholder="ornek@firma.com", key="login_email"
                )
                login_password = st.text_input(
                    "Şifre", type="password", placeholder="••••••••", key="login_password"
                )
                remember_me = st.checkbox("Beni hatırla", key="remember_me")

                login_submitted = st.form_submit_button(
                    "Giriş Yap", use_container_width=True, type="primary"
                )

            if login_submitted:
                if not login_email or not login_password:
                    st.error("E-posta ve şifre alanları zorunludur.")
                    return

                _handle_login(login_email, login_password)

        # ── Kayıt Tab'ı / Register Tab ──

        with tab_register:
            with st.form("register_form", clear_on_submit=False):
                st.markdown("#### Yeni hesap oluşturun")

                reg_name = st.text_input(
                    "Ad Soyad", placeholder="Ahmet Yılmaz", key="reg_name"
                )
                reg_email = st.text_input(
                    "E-posta", placeholder="ornek@firma.com", key="reg_email"
                )
                reg_company = st.text_input(
                    "Şirket Adı (Opsiyonel)", placeholder="ABC İnşaat Ltd.", key="reg_company"
                )
                reg_password = st.text_input(
                    "Şifre", type="password", placeholder="En az 8 karakter", key="reg_password"
                )
                reg_password2 = st.text_input(
                    "Şifre Tekrar", type="password", placeholder="Şifreyi tekrar girin", key="reg_password2"
                )

                reg_submitted = st.form_submit_button(
                    "Kayıt Ol", use_container_width=True, type="primary"
                )

            if reg_submitted:
                _handle_register(reg_name, reg_email, reg_company, reg_password, reg_password2)

        # Alt bilgi / Footer
        st.markdown(
            """
            <div style="text-align:center; padding-top: 2rem; opacity: 0.5; font-size: 0.85rem;">
                TenderAI - Yapay Zeka Destekli İhale Şartname Analiz Platformu<br>
                Tüm ihale dokümanlarınızı saniyeler içinde analiz edin.
            </div>
            """,
            unsafe_allow_html=True,
        )


def _handle_login(email: str, password: str) -> None:
    """Giriş işlemini yönet / Handle login."""
    try:
        db_manager = DatabaseManager()
        db_manager.init_db()

        with db_manager.get_db() as db:
            auth = AuthManager(db)
            success, msg, user = auth.login(email, password)

            if success and user:
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = user.id
                st.session_state["user_email"] = user.email
                st.session_state["user_name"] = user.full_name
                st.session_state["user_plan"] = user.plan
                st.session_state["analysis_count"] = user.analysis_count or 0

                st.success(f"Hoş geldiniz, {user.full_name}! 🎉")
                st.rerun()
            else:
                st.error(f"⚠️ {msg}")

    except Exception as e:
        st.error(f"Giriş sırasında hata oluştu: {e}")


def _handle_register(
    name: str, email: str, company: str, password: str, password2: str
) -> None:
    """Kayıt işlemini yönet / Handle registration."""
    try:
        if not name or not email or not password:
            st.error("Ad Soyad, E-posta ve Şifre alanları zorunludur.")
            return

        if password != password2:
            st.error("Şifreler eşleşmiyor.")
            return

        db_manager = DatabaseManager()
        db_manager.init_db()

        with db_manager.get_db() as db:
            auth = AuthManager(db)
            success, msg, user = auth.register(
                email=email,
                password=password,
                full_name=name,
                company_name=company if company else None,
            )

            if success:
                st.success("✅ Kayıt başarılı! Şimdi giriş yapabilirsiniz.")
                st.balloons()
            else:
                st.error(f"⚠️ {msg}")

    except Exception as e:
        st.error(f"Kayıt sırasında hata oluştu: {e}")
