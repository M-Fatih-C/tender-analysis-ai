"""
TenderAI Giriş/Kayıt Sayfası / Login & Register Page.
"""

import streamlit as st
from src.database.db import DatabaseManager
from src.auth.auth import AuthManager


def render_login() -> None:
    """Giriş ve kayıt sayfasını render et / Render login & register page."""

    # Sidebar gizle
    st.markdown(
        "<style>[data-testid='stSidebar']{display:none !important;}</style>",
        unsafe_allow_html=True,
    )

    # Ortalanmış container
    _, center, _ = st.columns([1.2, 2, 1.2])

    with center:
        st.markdown(
            '<div class="login-logo">'
            "<h1>📋 TenderAI</h1>"
            "<p>Yapay Zeka Destekli İhale Analiz Platformu</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])

        # ── Giriş ──
        with tab_login:
            with st.form("login_form"):
                email = st.text_input("📧 E-posta", placeholder="ornek@firma.com")
                password = st.text_input("🔒 Şifre", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Giriş Yap", use_container_width=True, type="primary")

                if submitted:
                    if not email or not password:
                        st.error("E-posta ve şifre gereklidir.")
                    else:
                        _do_login(email, password)

        # ── Kayıt ──
        with tab_register:
            with st.form("register_form"):
                reg_name = st.text_input("👤 Ad Soyad", placeholder="Ahmet Yılmaz")
                reg_company = st.text_input("🏢 Firma (opsiyonel)", placeholder="ABC İnşaat")
                reg_email = st.text_input("📧 E-posta", placeholder="ornek@firma.com", key="reg_email")
                reg_pass = st.text_input("🔒 Şifre", type="password", placeholder="En az 8 karakter", key="reg_pass")
                reg_pass2 = st.text_input("🔒 Şifre Tekrar", type="password", placeholder="Şifreyi tekrarlayın")
                reg_submitted = st.form_submit_button("Kayıt Ol", use_container_width=True, type="primary")

                if reg_submitted:
                    if not reg_name or not reg_email or not reg_pass:
                        st.error("Ad, e-posta ve şifre gereklidir.")
                    elif reg_pass != reg_pass2:
                        st.error("Şifreler eşleşmiyor.")
                    else:
                        _do_register(reg_email, reg_pass, reg_name, reg_company)

        st.markdown("---")

        # Demo modu
        demo_mode = st.session_state.get("demo_mode", False)
        if demo_mode:
            if st.button("🎭 Demo Modu ile Giriş", use_container_width=True):
                _set_session_demo()
                st.rerun()

        st.markdown(
            "<div style='text-align:center;color:#555;font-size:0.75rem;margin-top:1rem;'>"
            "TenderAI v1.0.0 · © 2025</div>",
            unsafe_allow_html=True,
        )


def _do_login(email: str, password: str) -> None:
    """Giriş işlemi / Login process."""
    try:
        db_mgr = DatabaseManager()
        db_mgr.init_db()
        with db_mgr.get_db() as db:
            auth = AuthManager(db)
            ok, msg, user = auth.login(email.strip(), password)
            if ok and user:
                _set_session(user)
                st.rerun()
            else:
                st.error(msg)
    except Exception as e:
        st.error(f"Giriş hatası: {e}")


def _do_register(email: str, password: str, name: str, company: str) -> None:
    """Kayıt işlemi / Register process."""
    try:
        db_mgr = DatabaseManager()
        db_mgr.init_db()
        with db_mgr.get_db() as db:
            auth = AuthManager(db)
            ok, msg, user = auth.register(email.strip(), password, name.strip(), company.strip() or None)
            if ok and user:
                st.success("✅ Kayıt başarılı! Giriş yapabilirsiniz.")
            else:
                st.error(msg)
    except Exception as e:
        st.error(f"Kayıt hatası: {e}")


def _set_session(user) -> None:
    """Kullanıcı bilgilerini session'a yaz / Write user info to session."""
    st.session_state["authenticated"] = True
    st.session_state["user_id"] = user.id
    st.session_state["user_email"] = user.email
    st.session_state["user_name"] = user.full_name
    st.session_state["user_plan"] = user.plan or "free"
    st.session_state["analysis_count"] = user.analysis_count or 0
    st.session_state["current_page"] = "dashboard"


def _set_session_demo() -> None:
    """Demo oturumu / Demo session."""
    st.session_state["authenticated"] = True
    st.session_state["user_id"] = 0
    st.session_state["user_email"] = "demo@tenderai.com"
    st.session_state["user_name"] = "Demo Kullanıcı"
    st.session_state["user_plan"] = "pro"
    st.session_state["analysis_count"] = 0
    st.session_state["current_page"] = "dashboard"
