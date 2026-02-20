"""
TenderAI Sayfa Başlık Bileşeni / Page Header Component.
"""

import streamlit as st
from datetime import datetime

_TURKISH_MONTHS = [
    "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
]


def render_header(title: str, subtitle: str = "", show_date: bool = True) -> None:
    """Sayfa başlığı render et / Render page header."""
    now = datetime.now()
    date_str = f"{now.day} {_TURKISH_MONTHS[now.month]} {now.year}"

    cols = st.columns([5, 2])
    with cols[0]:
        st.markdown(f"### {title}")
        if subtitle:
            st.caption(subtitle)
    with cols[1]:
        if show_date:
            st.markdown(
                f"<div style='text-align:right;padding-top:8px;color:#8892b0;font-size:0.85rem;'>"
                f"📅 {date_str}</div>",
                unsafe_allow_html=True,
            )

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
