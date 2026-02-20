"""
TenderAI Ana Streamlit Uygulaması / Main Streamlit Application.

Tüm modülleri birleştiren ana giriş noktası.
Main entry point that integrates all modules.

Çalıştırma / Run:
    streamlit run ui/app.py
"""

import sys
from pathlib import Path

# Proje kökünü sys.path'e ekle / Add project root to sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

# Sayfa yapılandırması — ilk Streamlit çağrısı olmalı
# Page config — must be first Streamlit call
st.set_page_config(
    page_title="TenderAI - İhale Analiz Platformu",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.components.sidebar import render_sidebar
from ui.pages.login import render_login_page
from ui.pages.dashboard import render_dashboard
from ui.pages.analysis import render_analysis_page
from ui.pages.history import render_history_page
from ui.pages.payment import render_payment_page

# ============================================================
# Custom CSS
# ============================================================

_CUSTOM_CSS = """
<style>
    /* Ana düzen / Main layout */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }

    /* Metrik kartları / Metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea11 0%, #764ba211 100%);
        border: 1px solid rgba(128,128,128,0.15);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetric"] label {
        font-size: 0.85rem;
        font-weight: 500;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
    }

    /* Buton stilleri / Button styles */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Tab stilleri / Tab styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1.2rem;
    }

    /* Alert/info kutuları / Alert boxes */
    .risk-high { border-left: 4px solid #e74c3c; padding: 0.8rem; border-radius: 6px; background: #e74c3c11; margin: 0.5rem 0; }
    .risk-medium { border-left: 4px solid #f39c12; padding: 0.8rem; border-radius: 6px; background: #f39c1211; margin: 0.5rem 0; }
    .risk-low { border-left: 4px solid #27ae60; padding: 0.8rem; border-radius: 6px; background: #27ae6011; margin: 0.5rem 0; }

    /* Progress bar */
    .stProgress > div > div {
        border-radius: 10px;
    }

    /* Divider */
    hr { margin: 1rem 0; opacity: 0.2; }
</style>
"""


# ============================================================
# Ana Uygulama / Main Application
# ============================================================


def main() -> None:
    """Ana uygulama fonksiyonu / Main application function."""

    # Custom CSS inject
    st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)

    # Session state başlat / Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "dashboard"

    # Routing
    if not st.session_state["authenticated"]:
        render_login_page()
    else:
        # Sidebar navigasyonu / Sidebar navigation
        selected_page = render_sidebar()

        # Sayfa render / Page rendering
        if selected_page == "📊 Dashboard":
            render_dashboard()
        elif selected_page == "🔍 Yeni Analiz":
            render_analysis_page()
        elif selected_page == "📁 Geçmiş Analizler":
            render_history_page()
        elif selected_page == "💳 Plan & Ödeme":
            render_payment_page()


if __name__ == "__main__":
    main()
