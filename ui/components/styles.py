"""
TenderAI Premium CSS Sistemi / Premium CSS System v2.0.

Glassmorphism, animasyonlar, dark tema, responsive.
"""

import streamlit as st


def inject_custom_css() -> None:
    """Premium CSS enjekte et."""
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """<style>
/* ============================================================
   GENEL / GENERAL
   ============================================================ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }
html { scroll-behavior: smooth; }

/* Hide Streamlit branding */
#MainMenu, header[data-testid="stHeader"], footer,
div[data-testid="stToolbar"], .stDeployButton,
div[data-testid="stSidebarNavItems"] { display: none !important; }

.block-container { padding: 1rem 2rem 2rem 2rem; }

/* ============================================================
   SCROLLBAR
   ============================================================ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #555; }

/* ============================================================
   ANIMATIONS
   ============================================================ */
@keyframes fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
@keyframes slideUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes slideInLeft { from{opacity:0;transform:translateX(-20px)} to{opacity:1;transform:translateX(0)} }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.6} }
@keyframes bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)} }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-3px)} 75%{transform:translateX(3px)} }
@keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
@keyframes gradientShift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }

/* ============================================================
   SIDEBAR
   ============================================================ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a1a 0%, #1a1a3e 50%, #0f1b3d 100%);
    width: 280px !important;
    min-width: 280px !important;
}
section[data-testid="stSidebar"] .block-container { padding: 1rem 1rem; }

.sidebar-logo {
    text-align: center; padding: 1.5rem 0 0.5rem 0;
    animation: fadeIn 0.6s ease;
}
.sidebar-logo .logo-icon { font-size: 2.5rem; }
.sidebar-logo .logo-text {
    font-size: 1.6rem; font-weight: 800;
    background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.sidebar-logo .logo-sub {
    font-size: 0.7rem; color: #8892b0; margin-top: 2px;
    letter-spacing: 1px; text-transform: uppercase;
}

/* User card */
.user-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 1rem; margin: 1rem 0;
    animation: slideUp 0.5s ease;
}
.user-card .avatar {
    width: 42px; height: 42px; border-radius: 50%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    display: inline-flex; align-items: center; justify-content: center;
    color: #fff; font-weight: 700; font-size: 1rem;
    margin-right: 10px; vertical-align: middle;
}
.user-card .user-name { font-weight: 600; color: #f1f5f9; font-size: 0.95rem; }
.user-card .user-company { font-size: 0.75rem; color: #8892b0; }
.plan-badge {
    display: inline-block; padding: 2px 10px; border-radius: 12px;
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.5px; margin-top: 4px;
}
.plan-free { background: rgba(102,126,234,0.15); color: #667eea; }
.plan-starter { background: rgba(243,156,18,0.15); color: #f39c12; }
.plan-pro { background: rgba(155,89,182,0.15); color: #9b59b6; }

.quota-bar {
    height: 4px; background: #1a1a2e; border-radius: 2px; margin-top: 8px; overflow: hidden;
}
.quota-fill {
    height: 100%; border-radius: 2px;
    transition: width 0.8s ease;
}

/* Nav buttons */
section[data-testid="stSidebar"] button[kind="secondary"],
section[data-testid="stSidebar"] button[kind="primary"] {
    width: 100%; text-align: left !important; justify-content: flex-start !important;
    border: none; border-radius: 8px; padding: 0.6rem 1rem;
    font-size: 0.85rem; font-weight: 500;
    transition: all 0.3s ease; margin-bottom: 2px;
}
section[data-testid="stSidebar"] button[kind="secondary"] {
    background: transparent; color: #8892b0;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: rgba(102,126,234,0.1); color: #f1f5f9;
    transform: translateX(4px);
}
section[data-testid="stSidebar"] button[kind="primary"] {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: #fff; border-left: 3px solid #f093fb;
}

.sidebar-footer {
    position: fixed; bottom: 0; width: 260px;
    padding: 0.8rem 1rem; text-align: center;
    font-size: 0.65rem; color: #555; border-top: 1px solid rgba(255,255,255,0.05);
    background: #0a0a1a;
}

/* ============================================================
   METRIC CARDS (glassmorphism)
   ============================================================ */
.metric-card {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
    animation: slideUp 0.5s ease;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(102,126,234,0.15);
    border-color: rgba(102,126,234,0.2);
}
.metric-icon { font-size: 1.8rem; margin-bottom: 6px; }
.metric-value { font-size: 1.8rem; font-weight: 800; color: #f1f5f9; }
.metric-label { font-size: 0.75rem; color: #8892b0; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }

/* ============================================================
   RISK SCORE CIRCLE
   ============================================================ */
.risk-circle {
    width: 160px; height: 160px; border-radius: 50%;
    border: 6px solid; display: flex; flex-direction: column;
    align-items: center; justify-content: center; margin: 0 auto;
    animation: fadeIn 0.8s ease;
    position: relative;
}
.risk-circle .score { font-size: 3rem; font-weight: 800; line-height: 1; }
.risk-circle .label { font-size: 0.8rem; font-weight: 600; margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }

/* ============================================================
   ADVICE CARDS
   ============================================================ */
.advice-card {
    border-radius: 14px; padding: 1.5rem; text-align: center;
    border: 2px solid; animation: slideUp 0.6s ease;
}
.advice-icon { font-size: 2.5rem; margin-bottom: 8px; }
.advice-title { font-size: 1.4rem; font-weight: 800; }
.advice-text { font-size: 0.85rem; color: #b0b8d1; margin-top: 6px; }
.advice-gir { border-color: #27ae60; background: rgba(39,174,96,0.08); }
.advice-gir .advice-title { color: #27ae60; }
.advice-dikkatli { border-color: #f39c12; background: rgba(243,156,18,0.08); }
.advice-dikkatli .advice-title { color: #f39c12; }
.advice-girme { border-color: #e74c3c; background: rgba(231,76,60,0.08); animation: shake 0.5s ease; }
.advice-girme .advice-title { color: #e74c3c; }

/* ============================================================
   RISK BADGES
   ============================================================ */
.risk-badge {
    display: inline-block; padding: 3px 10px; border-radius: 12px;
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.5px;
}
.risk-badge-critical { background: rgba(192,57,43,0.2); color: #e74c3c; animation: pulse 2s infinite; }
.risk-badge-high { background: rgba(231,76,60,0.15); color: #e67e22; }
.risk-badge-medium { background: rgba(243,156,18,0.15); color: #f39c12; }
.risk-badge-low { background: rgba(39,174,96,0.15); color: #27ae60; }

/* ============================================================
   ANALYSIS / RISK ITEM CARDS
   ============================================================ */
.analysis-card, .risk-item-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-left: 4px solid #555;
    border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 10px;
    transition: all 0.3s ease; animation: fadeIn 0.4s ease;
}
.analysis-card:hover, .risk-item-card:hover {
    background: rgba(255,255,255,0.04);
    transform: translateX(4px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-weight: 600; color: #f1f5f9; font-size: 0.9rem; }
.card-score { font-weight: 800; font-size: 1.2rem; }
.card-date { font-size: 0.75rem; color: #8892b0; margin-top: 4px; }

/* ============================================================
   TABLES
   ============================================================ */
.styled-table { width: 100%; border-collapse: collapse; border-radius: 10px; overflow: hidden; }
.styled-table th {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: #fff; padding: 10px 14px; font-size: 0.8rem; font-weight: 600;
    text-align: left; text-transform: uppercase; letter-spacing: 0.5px;
}
.styled-table td {
    padding: 10px 14px; font-size: 0.85rem; color: #c4c9d8;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.styled-table tr:nth-child(even) { background: rgba(255,255,255,0.015); }
.styled-table tr:hover { background: rgba(102,126,234,0.06); }

/* ============================================================
   UPLOAD AREA
   ============================================================ */
div[data-testid="stFileUploader"] {
    border: 2px dashed rgba(102,126,234,0.3);
    border-radius: 14px; padding: 1rem;
    transition: all 0.3s ease;
}
div[data-testid="stFileUploader"]:hover {
    border-color: #667eea;
    background: rgba(102,126,234,0.03);
}

/* ============================================================
   CHATBOT
   ============================================================ */
.chat-msg {
    padding: 0.8rem 1rem; border-radius: 14px; margin-bottom: 10px;
    max-width: 85%; animation: fadeIn 0.3s ease; font-size: 0.9rem;
    line-height: 1.5;
}
.chat-user {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: #fff; margin-left: auto; border-bottom-right-radius: 4px;
}
.chat-ai {
    background: rgba(255,255,255,0.05); color: #e2e8f0;
    border-bottom-left-radius: 4px;
}
.chat-time { font-size: 0.65rem; color: #666; margin-top: 4px; }
.chat-ref { font-size: 0.75rem; color: #667eea; margin-top: 4px; }

.chip {
    display: inline-block; padding: 6px 14px; border-radius: 20px;
    background: rgba(102,126,234,0.1); color: #667eea;
    font-size: 0.78rem; margin: 3px; cursor: pointer;
    border: 1px solid rgba(102,126,234,0.2);
    transition: all 0.2s ease;
}
.chip:hover { background: rgba(102,126,234,0.2); transform: scale(1.03); }

/* ============================================================
   GRADIENT DIVIDER
   ============================================================ */
.gradient-divider {
    height: 2px; border-radius: 1px; margin: 1rem 0;
    background: linear-gradient(90deg, #667eea, #764ba2, transparent);
}

/* ============================================================
   LOGIN PAGE
   ============================================================ */
.login-container {
    max-width: 440px; margin: 0 auto; padding: 2rem 0;
    animation: fadeIn 0.7s ease;
}
.login-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 2.5rem 2rem;
}
.login-logo {
    text-align: center; margin-bottom: 1.5rem;
}
.login-logo .icon { font-size: 3rem; }
.login-logo .title {
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.login-logo .subtitle { font-size: 0.8rem; color: #8892b0; margin-top: 4px; }

.strength-bar { height: 4px; border-radius: 2px; background: #1a1a2e; margin-top: 4px; }
.strength-fill { height: 100%; border-radius: 2px; transition: width 0.3s ease; }

/* ============================================================
   NOTIFICATION BADGE
   ============================================================ */
.notif-badge {
    display: inline-flex; align-items: center; justify-content: center;
    background: #e74c3c; color: #fff; font-size: 0.6rem; font-weight: 700;
    width: 18px; height: 18px; border-radius: 50%;
    position: relative; top: -8px; left: -4px;
    animation: pulse 2s infinite;
}

/* ============================================================
   COMPARISON TABLE
   ============================================================ */
.comparison-best {
    border: 2px solid #27ae60 !important;
    background: rgba(39,174,96,0.05) !important;
    box-shadow: 0 0 20px rgba(39,174,96,0.1);
}

/* ============================================================
   PROFILE FORM
   ============================================================ */
.form-section {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem;
}
.form-section-title {
    font-size: 0.9rem; font-weight: 700; color: #667eea;
    margin-bottom: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;
}

/* ============================================================
   ONBOARDING
   ============================================================ */
.onboarding-card {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px; padding: 2rem;
    text-align: center; animation: slideUp 0.6s ease;
}
.onboarding-step {
    display: inline-flex; align-items: center; justify-content: center;
    width: 32px; height: 32px; border-radius: 50%;
    font-weight: 700; font-size: 0.85rem; margin: 0 4px;
}
.step-active { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
.step-inactive { background: rgba(255,255,255,0.05); color: #555; }
.step-done { background: #27ae60; color: #fff; }

/* ============================================================
   PROGRESS BAR
   ============================================================ */
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #667eea, #764ba2) !important;
    border-radius: 4px;
}

/* ============================================================
   QUICK ACTION CARDS
   ============================================================ */
.action-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 1.5rem; text-align: center;
    transition: all 0.3s ease; cursor: pointer;
}
.action-card:hover {
    background: rgba(102,126,234,0.06);
    border-color: rgba(102,126,234,0.2);
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(102,126,234,0.1);
}
.action-icon { font-size: 2rem; margin-bottom: 8px; }
.action-title { font-weight: 600; color: #f1f5f9; font-size: 0.9rem; }
.action-desc { font-size: 0.75rem; color: #8892b0; margin-top: 4px; }

/* ============================================================
   RESPONSIVE
   ============================================================ */
@media (max-width: 768px) {
    .block-container { padding: 0.5rem 1rem; }
    .metric-card { padding: 0.8rem; }
    .metric-value { font-size: 1.3rem; }
    .risk-circle { width: 120px; height: 120px; }
    .risk-circle .score { font-size: 2rem; }
}

/* ============================================================
   SKELETON LOADING (shimmer)
   ============================================================ */
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
.skeleton {
    background: linear-gradient(90deg, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.03) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.8s ease-in-out infinite;
    border-radius: 8px;
}
.skeleton-card { height: 90px; margin-bottom: 10px; border-radius: 12px; }
.skeleton-chart { height: 220px; border-radius: 14px; }
.skeleton-text { height: 14px; width: 60%; margin: 6px 0; border-radius: 4px; }
.skeleton-text-sm { height: 10px; width: 40%; margin: 4px 0; border-radius: 3px; }

/* ============================================================
   TOAST NOTIFICATIONS
   ============================================================ */
@keyframes toastSlide { from{transform:translateX(120%);opacity:0} to{transform:translateX(0);opacity:1} }
@keyframes toastFade { from{opacity:1} to{opacity:0} }
.toast {
    position: fixed; top: 80px; right: 20px; z-index: 9999;
    min-width: 280px; max-width: 400px;
    padding: 14px 20px; border-radius: 12px;
    backdrop-filter: blur(15px);
    box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    animation: toastSlide 0.4s ease, toastFade 0.3s ease 4.7s forwards;
    display: flex; align-items: center; gap: 10px;
    font-size: 0.85rem; font-weight: 500;
}
.toast-success { background: rgba(39,174,96,0.9); color: #fff; border: 1px solid #27ae60; }
.toast-error { background: rgba(231,76,60,0.9); color: #fff; border: 1px solid #e74c3c; }
.toast-info { background: rgba(102,126,234,0.9); color: #fff; border: 1px solid #667eea; }
.toast-warning { background: rgba(243,156,18,0.9); color: #fff; border: 1px solid #f39c12; }
.toast-icon { font-size: 1.3rem; }

/* ============================================================
   PAGE TRANSITIONS
   ============================================================ */
@keyframes pageFadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
.main .block-container {
    animation: pageFadeIn 0.35s ease-out;
}

/* ============================================================
   STAGGERED CARD ANIMATIONS
   ============================================================ */
.metric-card:nth-child(1) { animation-delay: 0.05s; }
.metric-card:nth-child(2) { animation-delay: 0.1s; }
.metric-card:nth-child(3) { animation-delay: 0.15s; }
.metric-card:nth-child(4) { animation-delay: 0.2s; }

.action-card:nth-child(1) { animation-delay: 0.1s; }
.action-card:nth-child(2) { animation-delay: 0.2s; }
.action-card:nth-child(3) { animation-delay: 0.3s; }
.action-card:nth-child(4) { animation-delay: 0.4s; }

.analysis-card { animation: slideInLeft 0.3s ease; }
.analysis-card:nth-child(1) { animation-delay: 0s; }
.analysis-card:nth-child(2) { animation-delay: 0.05s; }
.analysis-card:nth-child(3) { animation-delay: 0.1s; }
.analysis-card:nth-child(4) { animation-delay: 0.15s; }
.analysis-card:nth-child(5) { animation-delay: 0.2s; }

/* ============================================================
   STAT MINI LABEL  
   ============================================================ */
.stat-delta {
    display: inline-block; padding: 2px 8px; border-radius: 10px;
    font-size: 0.65rem; font-weight: 700;
}
.delta-up { background: rgba(39,174,96,0.15); color: #27ae60; }
.delta-down { background: rgba(231,76,60,0.15); color: #e74c3c; }
.delta-neutral { background: rgba(255,255,255,0.06); color: #8892b0; }

/* ============================================================
   PLOTLY CHART CONTAINERS
   ============================================================ */
.js-plotly-plot, .plotly {
    border-radius: 12px !important;
    overflow: hidden;
}
div[data-testid="stPlotlyChart"] {
    background: rgba(255,255,255,0.01);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 4px;
}
</style>"""
