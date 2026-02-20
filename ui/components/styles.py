"""
TenderAI Profesyonel CSS Stilleri / Professional CSS Styles.

Tüm custom CSS bu dosyada yönetilir.
All custom CSS is managed in this file.
"""

import streamlit as st


def inject_custom_css() -> None:
    """Profesyonel CSS inject et / Inject professional CSS."""
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
/* ============================================================
   GENEL / GENERAL
   ============================================================ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

/* Streamlit branding gizle */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0E1117; }
::-webkit-scrollbar-thumb { background: #667eea; border-radius: 3px; }

/* fadeIn animasyonu */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ============================================================
   SIDEBAR
   ============================================================ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1724 0%, #141d2f 50%, #1a2540 100%) !important;
    border-right: 1px solid rgba(102,126,234,0.15);
    min-width: 280px !important;
    max-width: 280px !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    padding-top: 1rem;
}

/* Sidebar butonları */
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    padding: 0.6rem 1rem;
    border-radius: 10px;
    border: none;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.2s ease;
    margin-bottom: 4px;
}

[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateX(4px);
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(102,126,234,0.3);
}

[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.04) !important;
    color: #b0b8d1 !important;
}

/* ============================================================
   METRİK KARTLARI / METRIC CARDS
   ============================================================ */
.metric-card {
    background: linear-gradient(135deg, rgba(30,35,50,0.9), rgba(20,25,40,0.9));
    border: 1px solid rgba(102,126,234,0.15);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    transition: all 0.3s ease;
    animation: fadeIn 0.5s ease;
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(102,126,234,0.15);
    border-color: rgba(102,126,234,0.4);
}
.metric-card .metric-value {
    font-size: 2rem;
    font-weight: 700;
    margin: 0.3rem 0;
}
.metric-card .metric-label {
    font-size: 0.8rem;
    color: #8892b0;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.metric-card .metric-icon {
    font-size: 1.5rem;
    margin-bottom: 0.3rem;
}

/* ============================================================
   RİSK RENKLERİ / RISK COLORS
   ============================================================ */
.risk-low { color: #27ae60; }
.risk-medium { color: #f39c12; }
.risk-high { color: #e74c3c; }
.risk-critical { color: #c0392b; }

.risk-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.risk-badge-low { background: rgba(39,174,96,0.15); color: #27ae60; border: 1px solid rgba(39,174,96,0.3); }
.risk-badge-medium { background: rgba(243,156,18,0.15); color: #f39c12; border: 1px solid rgba(243,156,18,0.3); }
.risk-badge-high { background: rgba(231,76,60,0.15); color: #e74c3c; border: 1px solid rgba(231,76,60,0.3); }
.risk-badge-critical { background: rgba(192,57,43,0.15); color: #c0392b; border: 1px solid rgba(192,57,43,0.3); }

/* ============================================================
   RİSK SKORU DAİRESİ / RISK SCORE CIRCLE
   ============================================================ */
.risk-circle {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    border: 4px solid;
}
.risk-circle .score { font-size: 2.8rem; font-weight: 700; }
.risk-circle .label { font-size: 0.75rem; opacity: 0.8; }

/* ============================================================
   TAVSİYE KARTLARI / ADVICE CARDS
   ============================================================ */
.advice-card {
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
    border: 2px solid;
    animation: fadeIn 0.5s ease;
}
.advice-card .advice-icon { font-size: 2rem; }
.advice-card .advice-title { font-size: 1.2rem; font-weight: 700; margin: 0.5rem 0; }
.advice-card .advice-text { font-size: 0.85rem; opacity: 0.85; }

.advice-gir {
    border-color: #27ae60;
    background: rgba(39,174,96,0.08);
    color: #27ae60;
}
.advice-dikkatli {
    border-color: #f39c12;
    background: rgba(243,156,18,0.08);
    color: #f39c12;
}
.advice-girme {
    border-color: #e74c3c;
    background: rgba(231,76,60,0.08);
    color: #e74c3c;
}

/* ============================================================
   ANALİZ KARTLARI / ANALYSIS CARDS
   ============================================================ */
.analysis-card {
    background: rgba(30,35,50,0.7);
    border: 1px solid rgba(102,126,234,0.12);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    border-left: 4px solid;
    transition: all 0.25s ease;
    animation: fadeIn 0.4s ease;
}
.analysis-card:hover {
    transform: translateX(4px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.analysis-card .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.4rem;
}
.analysis-card .card-title { font-weight: 600; font-size: 0.95rem; }
.analysis-card .card-date { font-size: 0.8rem; color: #8892b0; }
.analysis-card .card-score { font-weight: 700; font-size: 1.1rem; }

/* ============================================================
   UPLOAD ALANI / UPLOAD AREA
   ============================================================ */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(102,126,234,0.3) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
    transition: all 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(102,126,234,0.6) !important;
    background: rgba(102,126,234,0.03) !important;
}

/* ============================================================
   TABLOLAR / TABLES
   ============================================================ */
.styled-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    animation: fadeIn 0.5s ease;
}
.styled-table thead th {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 0.8rem 1rem;
    font-size: 0.85rem;
    font-weight: 600;
    text-align: left;
}
.styled-table tbody tr { transition: background 0.2s; }
.styled-table tbody tr:hover { background: rgba(102,126,234,0.08); }
.styled-table tbody td {
    padding: 0.7rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 0.85rem;
}
.styled-table tbody tr:nth-child(even) { background: rgba(255,255,255,0.02); }

/* ============================================================
   KULLANICI KARTI / USER INFO CARD
   ============================================================ */
.user-card {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 0.8rem 1rem;
    border: 1px solid rgba(102,126,234,0.12);
    margin-bottom: 0.8rem;
}
.user-card .user-name { font-weight: 600; font-size: 0.95rem; }
.user-card .user-plan { font-size: 0.8rem; color: #667eea; }
.user-card .user-quota { font-size: 0.75rem; color: #8892b0; margin-top: 0.4rem; }

/* ============================================================
   GENEL BUTONLAR / GENERAL BUTTONS
   ============================================================ */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102,126,234,0.25);
}

/* ============================================================
   PLAN KARTLARI / PLAN CARDS
   ============================================================ */
.plan-card {
    border: 2px solid rgba(128,128,128,0.2);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    min-height: 380px;
    transition: all 0.3s ease;
    position: relative;
    background: rgba(30,35,50,0.6);
}
.plan-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}
.plan-card.highlighted {
    border-color: #667eea;
    background: rgba(102,126,234,0.05);
}
.plan-card .plan-badge {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 3px 14px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 0.5rem;
}
.plan-card .plan-name { font-size: 1.2rem; font-weight: 600; }
.plan-card .plan-price { font-size: 2rem; font-weight: 700; margin: 0.5rem 0; }
.plan-card .plan-period { font-size: 0.85rem; color: #8892b0; }
.plan-card .plan-features { text-align: left; padding: 0.5rem 0; }
.plan-card .plan-features li { padding: 0.2rem 0; font-size: 0.85rem; list-style: none; }

/* ============================================================
   LOGIN SAYFASI / LOGIN PAGE
   ============================================================ */
.login-container {
    max-width: 440px;
    margin: 0 auto;
    padding-top: 2rem;
}
.login-logo {
    text-align: center;
    margin-bottom: 1.5rem;
}
.login-logo h1 {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.login-logo p { color: #8892b0; font-size: 0.9rem; }

/* ============================================================
   RİSK ANALİZ KART / RISK ITEM CARD
   ============================================================ */
.risk-item-card {
    background: rgba(30,35,50,0.7);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    border-left: 4px solid;
    animation: fadeIn 0.4s ease;
}

/* ============================================================
   GRADIENT DIVIDER
   ============================================================ */
.gradient-divider {
    height: 2px;
    background: linear-gradient(90deg, #667eea, #764ba2, transparent);
    border: none;
    margin: 0.8rem 0 1.2rem 0;
}

/* Tab stili */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    padding: 8px 16px;
}

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, #667eea, #764ba2) !important;
}
</style>
"""
