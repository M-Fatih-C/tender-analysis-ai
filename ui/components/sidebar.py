"""
TenderAI Sidebar Bileşeni / Sidebar Component.

Uygulama genelinde kullanılan navigasyon sidebar'ı.
Application-wide navigation sidebar.

Bu modül Modül 5'te implement edilecektir.
This module will be implemented in Module 5.
"""

import streamlit as st


def render_sidebar() -> str:
    """
    Sidebar'ı render et / Render sidebar.

    Navigasyon menüsü, kullanıcı bilgileri ve ayarlar.
    Navigation menu, user info, and settings.

    Returns:
        Seçilen sayfa adı / Selected page name

    Raises:
        NotImplementedError: Modül 5'te implement edilecek (navigasyon mantığı)
    """
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60?text=TenderAI", use_container_width=True)
        st.markdown("---")

        # Navigasyon menüsü / Navigation menu
        selected_page = st.radio(
            "📌 Menü",
            options=[
                "📊 Dashboard",
                "🔍 Analiz",
                "📋 Geçmiş",
                "💳 Abonelik",
                "⚙️ Ayarlar",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Kullanıcı bilgileri / User info
        st.markdown("### 👤 Kullanıcı")
        st.markdown("**Giriş yapılmadı**")
        st.button("🔐 Giriş Yap", use_container_width=True)

        st.markdown("---")

        # Alt bilgi / Footer info
        st.markdown(
            "<div style='text-align: center; color: gray; font-size: 0.8em;'>"
            "TenderAI v0.1.0<br>"
            "© 2026 TenderAI"
            "</div>",
            unsafe_allow_html=True,
        )

    return selected_page
