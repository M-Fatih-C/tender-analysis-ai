"""
TenderAI Premium Login / Kayıt Sayfası v2.0.
"""

import streamlit as st
from src.utils.helpers import calculate_password_strength


def render_login() -> None:
    """Premium login sayfası."""
    # Sidebar gizle
    st.markdown("<style>section[data-testid='stSidebar']{display:none}</style>", unsafe_allow_html=True)

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown(
        '<div class="login-card">'
        '<div class="login-logo">'
        '<div class="icon">📋</div>'
        '<div class="title">TenderAI</div>'
        '<div class="subtitle">Yapay Zeka ile İhale Analizi</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    tab_login, tab_register = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])

    # ── GİRİŞ ──
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="ornek@firma.com")
            password = st.text_input("🔒 Şifre", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Giriş Yap", use_container_width=True, type="primary")

        if submitted:
            if not email or not password:
                st.error("Email ve şifre gereklidir.")
            else:
                try:
                    from src.database.db import DatabaseManager
                    from src.auth.auth import AuthManager
                    db_mgr = DatabaseManager()
                    db_mgr.init_db()
                    with db_mgr.get_db() as db:
                        auth = AuthManager(db)
                        success, msg, user = auth.login(email, password)
                        if success and user:
                            st.session_state.update({
                                "authenticated": True,
                                "user_id": user.id,
                                "user_name": user.full_name or email.split("@")[0],
                                "user_email": user.email,
                                "user_plan": user.plan or "free",
                                "user_company": user.company_name or "",
                                "analysis_count": user.analysis_count or 0,
                                "current_page": "dashboard",
                            })
                            st.success("✅ Giriş başarılı!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                except Exception as e:
                    st.error(f"❌ Giriş hatası: {e}")

    # ── KAYIT ──
    with tab_register:
        with st.form("register_form"):
            full_name = st.text_input("👤 Ad Soyad")
            company = st.text_input("🏢 Firma Adı (opsiyonel)")
            reg_email = st.text_input("📧 Email", key="reg_email", placeholder="ornek@firma.com")
            reg_pass = st.text_input("🔒 Şifre", type="password", key="reg_pass", placeholder="En az 8 karakter")

            # Şifre güçlülük göstergesi
            if reg_pass:
                strength = calculate_password_strength(reg_pass)
                pct = min(100, strength["score"] * 25)
                st.markdown(
                    f'<div class="strength-bar"><div class="strength-fill" '
                    f'style="width:{pct}%;background:{strength["color"]};"></div></div>'
                    f'<div style="font-size:0.7rem;color:{strength["color"]};margin-top:2px;">'
                    f'{strength["label"]}</div>',
                    unsafe_allow_html=True,
                )

            reg_pass2 = st.text_input("🔒 Şifre Tekrar", type="password", key="reg_pass2")
            reg_submit = st.form_submit_button("Kayıt Ol", use_container_width=True, type="primary")

        if reg_submit:
            if not full_name or not reg_email or not reg_pass:
                st.error("Ad, email ve şifre zorunludur.")
            elif len(reg_pass) < 8:
                st.error("Şifre en az 8 karakter olmalıdır.")
            elif reg_pass != reg_pass2:
                st.error("Şifreler eşleşmiyor.")
            else:
                try:
                    from src.database.db import DatabaseManager
                    from src.auth.auth import AuthManager
                    db_mgr = DatabaseManager()
                    db_mgr.init_db()
                    with db_mgr.get_db() as db:
                        auth = AuthManager(db)
                        success, msg, user = auth.register(
                            email=reg_email, password=reg_pass,
                            full_name=full_name, company_name=company or None,
                        )
                        if success and user:
                            # Hoşgeldin bildirimi
                            try:
                                from src.utils.notifications import NotificationManager
                                nm = NotificationManager(db)
                                nm.notify_welcome(user.id)
                                db.commit()
                            except Exception:
                                pass

                            st.session_state.update({
                                "authenticated": True,
                                "user_id": user.id,
                                "user_name": user.full_name or reg_email.split("@")[0],
                                "user_email": user.email,
                                "user_plan": "free",
                                "user_company": company or "",
                                "analysis_count": 0,
                                "current_page": "dashboard",
                                "onboarding_completed": False,
                            })
                            st.success("✅ Kayıt başarılı!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")
                except Exception as e:
                    st.error(f"❌ Kayıt hatası: {e}")

    # Divider
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Demo modu
    if st.button("🎮 Demo Modu ile Dene", use_container_width=True):
        st.session_state.update({
            "authenticated": True,
            "user_id": 0,
            "user_name": "Demo Kullanıcı",
            "user_email": "demo@tenderai.com",
            "user_plan": "pro",
            "user_company": "Demo Firma A.Ş.",
            "analysis_count": 0,
            "demo_mode": True,
            "current_page": "dashboard",
        })
        st.rerun()

    st.markdown(
        '<div style="text-align:center;margin-top:1rem;font-size:0.7rem;color:#555;">'
        '© 2025 TenderAI | Tüm hakları saklıdır | v2.0.0</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)
