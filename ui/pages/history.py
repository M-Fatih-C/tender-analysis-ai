"""
TenderAI Geçmiş Analizler Sayfası / Analysis History Page.

Daha önce yapılmış analizlerin listesi ve detayları.
List and details of previously performed analyses.

Bu modül Modül 5'te implement edilecektir.
This module will be implemented in Module 5.
"""

import streamlit as st


def render_history_page() -> None:
    """
    Geçmiş analizler sayfasını render et / Render analysis history page.

    Tüm geçmiş analizlerin tablo görünümü ve filtreleme.
    Table view and filtering of all past analyses.

    Raises:
        NotImplementedError: Modül 5'te implement edilecek
    """
    st.title("📋 Geçmiş Analizler")
    st.markdown("---")

    # Filtreleme / Filtering
    col1, col2, col3 = st.columns(3)

    with col1:
        st.date_input("Başlangıç Tarihi")
    with col2:
        st.date_input("Bitiş Tarihi")
    with col3:
        st.selectbox("Risk Seviyesi", ["Tümü", "Düşük", "Orta", "Yüksek", "Kritik"])

    st.markdown("---")

    # Analiz listesi (placeholder) / Analysis list (placeholder)
    st.info(
        "📭 Henüz analiz geçmişi bulunmuyor.\n\n"
        "Yeni bir analiz başlatmak için **Analiz** sayfasına gidin."
    )

    # Tablo placeholder / Table placeholder
    st.markdown("#### Analiz Tablosu")
    st.markdown(
        "| # | Dosya Adı | Tarih | Risk Skoru | Durum |\n"
        "|---|-----------|-------|------------|-------|\n"
        "| — | — | — | — | — |"
    )
