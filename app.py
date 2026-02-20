"""
TenderAI — Ana Giriş Noktası / Main Entry Point.

Kullanım / Usage:
    streamlit run app.py
"""

import os
import sys

# Proje kökünü Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from ui.components.styles import inject_custom_css
from ui.components.sidebar import render_sidebar
from ui.views.login_view import render_login
from ui.views.dashboard_view import render_dashboard
from ui.views.analysis_view import render_analysis
from ui.views.history_view import render_history
from ui.views.payment_view import render_payment
from src.database.db import DatabaseManager


# ============================================================
# Sayfa Konfigürasyonu (EN BAŞTA olmalı)
# ============================================================
st.set_page_config(
    page_title="TenderAI — İhale Analiz Platformu",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS Inject
# ============================================================
inject_custom_css()

# ============================================================
# Veritabanı başlat
# ============================================================

@st.cache_resource
def _init_db():
    db = DatabaseManager()
    db.init_db()
    return True

_init_db()

# ============================================================
# Session State Varsayılanları
# ============================================================
_defaults = {
    "authenticated": False,
    "current_page": "dashboard",
    "user_id": None,
    "user_email": None,
    "user_name": None,
    "user_plan": "free",
    "analysis_count": 0,
    "analysis_state": "upload",
    "demo_mode": os.environ.get("DEMO_MODE", "false").lower() == "true",
}
for key, val in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ============================================================
# ROUTING
# ============================================================
if not st.session_state["authenticated"]:
    render_login()
else:
    page = render_sidebar()

    _pages = {
        "dashboard": render_dashboard,
        "analysis": render_analysis,
        "history": render_history,
        "payment": render_payment,
    }

    render_fn = _pages.get(page, render_dashboard)
    render_fn()
