"""
TenderAI Profesyonel Sidebar / Professional Sidebar Component.
"""

import streamlit as st


_NAV_ITEMS = [
    ("📊", "Dashboard", "dashboard"),
    ("🔍", "Yeni Analiz", "analysis"),
    ("📁", "Geçmiş Analizler", "history"),
    ("💳", "Plan & Ödeme", "payment"),
]


def render_sidebar() -> str:
    """
    Profesyonel sidebar render et, aktif sayfa adını döndür.
    Render professional sidebar, return active page name.
    """
    with st.sidebar:
        # Logo
        st.markdown(
            '<div class="login-logo">'
            '<h1 style="font-size:1.8rem;margin:0;">📋 TenderAI</h1>'
            '<p style="margin:0;">İhale Analiz Platformu</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Kullanıcı bilgi kartı
        user_name = st.session_state.get("user_name", "Kullanıcı")
        plan = st.session_state.get("user_plan", "free")
        plan_names = {"free": "🆓 Ücretsiz", "starter": "⭐ Başlangıç", "pro": "💎 Pro"}
        plan_limits = {"free": 3, "starter": 20, "pro": 9999}
        count = st.session_state.get("analysis_count", 0)
        limit = plan_limits.get(plan, 3)
        remaining = max(0, limit - count) if limit < 9999 else 9999

        st.markdown(
            f'<div class="user-card">'
            f'<div class="user-name">👤 {user_name}</div>'
            f'<div class="user-plan">{plan_names.get(plan, plan)}</div>'
            f'<div class="user-quota">Kalan: {"♾️ Sınırsız" if remaining >= 9999 else f"{remaining}/{limit}"}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if remaining < 9999:
            st.progress(min(1.0, count / max(limit, 1)))

        st.markdown("---")

        # Navigasyon
        current = st.session_state.get("current_page", "dashboard")

        for icon, label, key in _NAV_ITEMS:
            btn_type = "primary" if current == key else "secondary"
            if st.button(f"{icon}  {label}", key=f"nav_{key}", type=btn_type, use_container_width=True):
                st.session_state["current_page"] = key
                # Analiz sayfasına dönünce upload durumuna resetle
                if key == "analysis":
                    st.session_state["analysis_state"] = "upload"
                st.rerun()

        st.markdown("---")

        # Çıkış
        if st.button("🚪  Çıkış Yap", key="logout_btn", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

        # Footer
        st.markdown(
            "<div style='text-align:center;font-size:0.7rem;color:#555;margin-top:1rem;'>"
            "TenderAI v1.0.0<br>© 2025</div>",
            unsafe_allow_html=True,
        )

    return st.session_state.get("current_page", "dashboard")
