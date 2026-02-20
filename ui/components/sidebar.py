"""
TenderAI Sidebar Bileşeni / Sidebar Component.

Navigasyon menüsü, kullanıcı bilgisi ve plan gösterimi.
Navigation menu, user info, and plan display.
"""

import streamlit as st


# Plan limitleri / Plan limits
_PLAN_LABELS = {
    "free": "🆓 Ücretsiz",
    "starter": "⭐ Başlangıç",
    "pro": "💎 Profesyonel",
    "enterprise": "🏢 Kurumsal",
}

_PLAN_LIMITS = {
    "free": 3,
    "starter": 20,
    "pro": 999,
    "enterprise": 999,
}


def render_sidebar() -> str:
    """
    Sidebar'ı render et / Render sidebar.

    Returns:
        Seçilen sayfa adı / Selected page name
    """
    with st.sidebar:
        # Logo ve başlık / Logo and title
        st.markdown(
            """
            <div style="text-align:center; padding: 0.5rem 0 1rem;">
                <h1 style="margin:0; font-size:1.8rem;">📋 TenderAI</h1>
                <p style="margin:0; font-size:0.85rem; opacity:0.7;">
                    İhale Şartname Analiz Platformu
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Kullanıcı bilgileri / User info
        user_name = st.session_state.get("user_name", "Kullanıcı")
        user_plan = st.session_state.get("user_plan", "free")
        plan_label = _PLAN_LABELS.get(user_plan, "🆓 Ücretsiz")

        st.markdown(f"**👤 {user_name}**")
        st.caption(f"Plan: {plan_label}")

        # Kalan analiz hakkı / Remaining analysis quota
        analysis_count = st.session_state.get("analysis_count", 0)
        max_analysis = _PLAN_LIMITS.get(user_plan, 3)

        if max_analysis < 999:
            remaining = max(0, max_analysis - analysis_count)
            st.progress(
                min(1.0, analysis_count / max_analysis) if max_analysis > 0 else 0,
                text=f"Kalan hak: {remaining}/{max_analysis}",
            )
        else:
            st.caption("♾️ Sınırsız analiz hakkı")

        st.divider()

        # Navigasyon menüsü / Navigation menu
        selected = st.radio(
            "Navigasyon",
            options=[
                "📊 Dashboard",
                "🔍 Yeni Analiz",
                "📁 Geçmiş Analizler",
                "💳 Plan & Ödeme",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        # Çıkış butonu / Logout button
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        # Versiyon bilgisi / Version info
        st.markdown(
            """
            <div style="text-align:center; padding-top:2rem; opacity:0.4; font-size:0.75rem;">
                TenderAI v1.0.0<br>
                © 2025 Tüm hakları saklıdır
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected
