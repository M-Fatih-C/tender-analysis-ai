"""
TenderAI Premium Sidebar v2.0.
"""

import streamlit as st
from src.utils.helpers import generate_avatar_initials


def render_sidebar() -> str:
    """Premium sidebar render et. Aktif sayfa key döner."""
    with st.sidebar:
        # Logo
        st.markdown(
            '<div class="sidebar-logo">'
            '<div class="logo-icon">📋</div>'
            '<div class="logo-text">TenderAI</div>'
            '<div class="logo-sub">İhale Analiz Platformu</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # User card
        name = st.session_state.get("user_name", "Kullanıcı")
        company = st.session_state.get("user_company", "")
        plan = st.session_state.get("user_plan", "free")
        count = st.session_state.get("analysis_count", 0)
        limit_map = {"free": 3, "starter": 20, "pro": 9999}
        limit = limit_map.get(plan, 3)
        remaining = max(0, limit - count) if limit < 9999 else 9999

        initials = generate_avatar_initials(name)
        plan_names = {"free": "Ücretsiz", "starter": "Başlangıç", "pro": "Profesyonel"}
        plan_class = f"plan-{plan}"

        pct = min(100, int((count / max(limit, 1)) * 100)) if limit < 9999 else 5
        bar_color = "#27ae60" if pct < 60 else "#f39c12" if pct < 85 else "#e74c3c"
        quota_text = f"{remaining} hak kaldı" if limit < 9999 else "♾️ Sınırsız"

        st.markdown(
            f'<div class="user-card">'
            f'<span class="avatar">{initials}</span>'
            f'<span class="user-name">{name}</span><br>'
            f'<span class="user-company">{company}</span><br>'
            f'<span class="plan-badge {plan_class}">{plan_names.get(plan, plan)}</span>'
            f'<div style="font-size:0.7rem;color:#8892b0;margin-top:8px;">📊 {quota_text}</div>'
            f'<div class="quota-bar"><div class="quota-fill" style="width:{pct}%;background:{bar_color};"></div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # Navigation
        current = st.session_state.get("current_page", "dashboard")

        nav_items = [
            ("dashboard", "📊", "Dashboard"),
            ("analysis", "🔍", "Yeni Analiz"),
            ("comparison", "⚖️", "İhale Karşılaştır"),
            ("chatbot", "💬", "Şartnameye Sor"),
            ("history", "📁", "Geçmiş Analizler"),
            ("company_profile", "🏢", "Firma Profili"),
            ("payment", "💳", "Plan & Ödeme"),
        ]

        for key, icon, label in nav_items:
            btn_type = "primary" if current == key else "secondary"
            if st.button(f"{icon}  {label}", type=btn_type, key=f"nav_{key}", use_container_width=True):
                st.session_state["current_page"] = key
                if key == "analysis":
                    st.session_state["analysis_state"] = "upload"
                st.rerun()

        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # Settings + Logout
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⚙️ Ayarlar", key="nav_settings", use_container_width=True):
                st.session_state["current_page"] = "settings"
                st.rerun()
        with c2:
            if st.button("🚪 Çıkış", key="nav_logout", use_container_width=True):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()

        # Footer
        st.markdown(
            '<div class="sidebar-footer">TenderAI v2.0.0 | © 2025</div>',
            unsafe_allow_html=True,
        )

    return st.session_state.get("current_page", "dashboard")
