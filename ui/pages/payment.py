"""
TenderAI Ödeme Sayfası / Payment Page.

Abonelik planları ve ödeme işlemleri arayüzü.
Subscription plans and payment processing interface.

Bu modül Modül 5'te implement edilecektir.
This module will be implemented in Module 5.
"""

import streamlit as st


def render_payment_page() -> None:
    """
    Ödeme sayfasını render et / Render payment page.

    Abonelik planları karşılaştırması ve ödeme formu.
    Subscription plan comparison and payment form.

    Raises:
        NotImplementedError: Modül 5'te implement edilecek
    """
    st.title("💳 Abonelik Planları")
    st.markdown("---")

    # Plan kartları / Plan cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("### 🆓 Ücretsiz")
        st.markdown("**₺0 / ay**")
        st.markdown("- 3 analiz/ay\n- Temel analiz\n- PDF yükleme")
        st.button("Mevcut Plan", disabled=True, key="free_btn")

    with col2:
        st.markdown("### 📘 Temel")
        st.markdown("**₺299 / ay**")
        st.markdown("- 20 analiz/ay\n- Risk skoru\n- PDF rapor")
        if st.button("Seç", key="basic_btn", use_container_width=True):
            st.warning("⚠️ Ödeme sistemi Modül 7'de implement edilecektir.")

    with col3:
        st.markdown("### 📗 Profesyonel")
        st.markdown("**₺599 / ay**")
        st.markdown("- 100 analiz/ay\n- Tam analiz\n- API erişimi")
        if st.button("Seç", key="pro_btn", use_container_width=True):
            st.warning("⚠️ Ödeme sistemi Modül 7'de implement edilecektir.")

    with col4:
        st.markdown("### 📕 Kurumsal")
        st.markdown("**₺999 / ay**")
        st.markdown("- Sınırsız analiz\n- Öncelikli destek\n- Özel entegrasyon")
        if st.button("İletişime Geç", key="ent_btn", use_container_width=True):
            st.warning("⚠️ Ödeme sistemi Modül 7'de implement edilecektir.")

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Tüm planlar KDV dahildir. İstediğiniz zaman iptal edebilirsiniz."
        "</div>",
        unsafe_allow_html=True,
    )
