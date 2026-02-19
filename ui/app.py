"""
TenderAI Ana Streamlit Uygulaması / Main Streamlit Application.

Uygulamanın giriş noktası ve sayfa yönlendirmesi.
Application entry point and page routing.

Bu modül Modül 5'te implement edilecektir.
This module will be implemented in Module 5.
"""

import streamlit as st


def configure_page() -> None:
    """Streamlit sayfa yapılandırması / Configure Streamlit page."""
    st.set_page_config(
        page_title="TenderAI - İhale Analiz Platformu",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def main() -> None:
    """
    Ana uygulama fonksiyonu / Main application function.

    Sayfa yönlendirmesi ve genel uygulama akışını yönetir.
    Manages page routing and overall application flow.
    """
    configure_page()

    st.title("🏗️ TenderAI")
    st.subheader("İhale Teknik Şartname Analiz Platformu")
    st.markdown("---")

    st.info(
        "🚧 **Geliştirme Aşamasında**\n\n"
        "TenderAI şu anda geliştirme aşamasındadır. "
        "Modül 5'te tam arayüz implement edilecektir."
    )

    # Özellik tanıtımı / Feature showcase
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🔍 Risk Analizi")
        st.markdown("Şartnamedeki riskleri otomatik tespit edin")

    with col2:
        st.markdown("### 📄 Belge Kontrolü")
        st.markdown("Gerekli belgelerin listesini çıkarın")

    with col3:
        st.markdown("### 💰 Mali Özet")
        st.markdown("Teminat ve ödeme koşullarını analiz edin")

    st.markdown("---")

    col4, col5 = st.columns(2)

    with col4:
        st.markdown("### ⚖️ Ceza Maddeleri")
        st.markdown("Ceza koşullarını hızlıca belirleyin")

    with col5:
        st.markdown("### ⏱️ Süre Analizi")
        st.markdown("Proje takvimini ve kritik tarihleri çıkarın")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "TenderAI v0.1.0 | © 2026 TenderAI Team"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
