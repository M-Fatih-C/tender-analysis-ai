"""
TenderAI v2.0 — Ana Uygulama / Main Application.

Routing, session state, CSS enjeksiyonu.
"""

import sys
from pathlib import Path

# Path setup
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="TenderAI — İhale Analiz Platformu",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.components.styles import inject_custom_css
from ui.components.sidebar import render_sidebar

# CSS
inject_custom_css()

# DB init (cached)
@st.cache_resource
def _init_db():
    from src.database.db import DatabaseManager
    db = DatabaseManager()
    db.init_db()
    return True

_init_db()

# Session defaults
_defaults = {
    "authenticated": False,
    "current_page": "dashboard",
    "user_id": None,
    "user_name": "",
    "user_email": "",
    "user_plan": "free",
    "user_company": "",
    "analysis_count": 0,
    "analysis_state": "upload",
    "demo_mode": False,
    "onboarding_completed": False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Routing ──
if not st.session_state["authenticated"]:
    from ui.views.login_view import render_login
    render_login()
else:
    page = render_sidebar()

    # Lazy imports
    _routes = {
        "dashboard": ("ui.views.dashboard_view", "render_dashboard"),
        "analysis": ("ui.views.analysis_view", "render_analysis"),
        "comparison": ("ui.views.comparison_view", "render_comparison"),
        "chatbot": ("ui.views.chatbot_view", "render_chatbot"),
        "history": ("ui.views.history_view", "render_history"),
        "company_profile": ("ui.views.company_profile_view", "render_company_profile"),
        "payment": ("ui.views.payment_view", "render_payment"),
        "settings": ("ui.views.settings_view", "render_settings"),
    }

    route = _routes.get(page)
    if route:
        import importlib
        mod = importlib.import_module(route[0])
        render_fn = getattr(mod, route[1])
        render_fn()
    else:
        st.error(f"Sayfa bulunamadı: {page}")
