"""
TenderAI Premium Dashboard v2.0.
"""

import json
import streamlit as st
import plotly.graph_objects as go

from ui.components.header import render_header
from src.database.db import DatabaseManager, get_user_analyses, get_analysis_stats
from src.utils.helpers import time_ago_turkish, risk_color_hex


def render_dashboard() -> None:
    """Premium dashboard."""
    # Onboarding check
    if not st.session_state.get("onboarding_completed", True):
        from ui.components.onboarding import render_onboarding
        render_onboarding()
        return

    user_name = st.session_state.get("user_name", "Kullanıcı")
    user_id = st.session_state.get("user_id", 0)
    render_header(f"Hoş Geldiniz, {user_name}!", "İhale analiz özetiniz", show_notifications=True)

    # ── Veri çek ──
    analyses = []
    stats = {}
    try:
        db_mgr = DatabaseManager()
        db_mgr.init_db()
        with db_mgr.get_db() as db:
            if user_id:
                raw = get_user_analyses(db, user_id, limit=20)
                for a in raw:
                    analyses.append({
                        "id": a.id, "file_name": a.file_name,
                        "risk_score": a.risk_score, "risk_level": a.risk_level,
                        "status": a.status, "created_at": a.created_at,
                        "total_pages": a.total_pages,
                    })
                stats = get_analysis_stats(db, user_id)
    except Exception:
        pass

    total = stats.get("total_analyses", 0)
    completed = stats.get("completed_analyses", 0)
    avg_risk = stats.get("average_risk_score")
    plan = st.session_state.get("user_plan", "free")
    limit_map = {"free": 3, "starter": 20, "pro": 9999}
    count = st.session_state.get("analysis_count", 0)
    limit = limit_map.get(plan, 3)
    remaining = max(0, limit - count) if limit < 9999 else 9999

    # ── 4 Metrik Kartı ──
    c1, c2, c3, c4 = st.columns(4)

    def _card(col, icon, label, value, color):
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-icon">{icon}</div>'
                f'<div class="metric-value" style="color:{color};">{value}</div>'
                f'<div class="metric-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    _card(c1, "📄", "Toplam Analiz", total, "#667eea")
    _card(c2, "✅", "Tamamlanan", completed, "#27ae60")
    _risk_c = risk_color_hex(int(avg_risk)) if avg_risk else "#8892b0"
    _card(c3, "⚠️", "Ort. Risk Skoru", f"{avg_risk:.0f}" if avg_risk else "—", _risk_c)
    _card(c4, "📊", "Kalan Hak", "♾️" if remaining >= 9999 else remaining, "#f39c12")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── İki kolon ──
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("#### 📋 Son Analizler")
        if not analyses:
            st.markdown(
                '<div class="onboarding-card">'
                '<div style="font-size:3rem;">🔍</div>'
                '<h4>İlk analizinizi yapın!</h4>'
                '<p style="color:#8892b0;">Şartname PDF\'inizi yükleyerek başlayın</p>'
                '</div>',
                unsafe_allow_html=True,
            )
            if st.button("🚀 Yeni Analiz Başlat", type="primary"):
                st.session_state["current_page"] = "analysis"
                st.session_state["analysis_state"] = "upload"
                st.rerun()
        else:
            for a in analyses[:5]:
                score = a["risk_score"]
                border_c = risk_color_hex(score) if score else "#555"
                time_str = time_ago_turkish(a["created_at"])
                status_icon = "✅" if a["status"] == "completed" else "⏳" if a["status"] == "pending" else "❌"
                pages = f" • {a['total_pages']} sayfa" if a.get("total_pages") else ""

                st.markdown(
                    f'<div class="analysis-card" style="border-left-color:{border_c};">'
                    f'<div class="card-header">'
                    f'<span class="card-title">📄 {(a["file_name"] or "—")[:35]}</span>'
                    f'<span class="card-score" style="color:{border_c};">{score if score is not None else "—"}</span>'
                    f'</div>'
                    f'<div class="card-date">{time_str}{pages} · {status_icon}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    with col_right:
        st.markdown("#### 📊 Risk Dağılımı")
        _render_risk_pie(analyses)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Hızlı İşlemler ──
    st.markdown("#### ⚡ Hızlı İşlemler")
    q1, q2, q3 = st.columns(3)

    with q1:
        st.markdown(
            '<div class="action-card">'
            '<div class="action-icon">🔍</div>'
            '<div class="action-title">Yeni Analiz</div>'
            '<div class="action-desc">PDF yükle, AI analiz et</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Başla →", key="qa_analysis", use_container_width=True):
            st.session_state["current_page"] = "analysis"
            st.session_state["analysis_state"] = "upload"
            st.rerun()

    with q2:
        st.markdown(
            '<div class="action-card">'
            '<div class="action-icon">⚖️</div>'
            '<div class="action-title">Karşılaştır</div>'
            '<div class="action-desc">İhaleleri yan yana incele</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Başla →", key="qa_compare", use_container_width=True):
            st.session_state["current_page"] = "comparison"
            st.rerun()

    with q3:
        st.markdown(
            '<div class="action-card">'
            '<div class="action-icon">🏢</div>'
            '<div class="action-title">Firma Profili</div>'
            '<div class="action-desc">Uygunluk skoru için doldurun</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Başla →", key="qa_profile", use_container_width=True):
            st.session_state["current_page"] = "company_profile"
            st.rerun()


def _render_risk_pie(analyses: list) -> None:
    """Risk dağılımı donut chart."""
    low = sum(1 for a in analyses if a["risk_score"] and a["risk_score"] <= 40)
    med = sum(1 for a in analyses if a["risk_score"] and 41 <= a["risk_score"] <= 70)
    high = sum(1 for a in analyses if a["risk_score"] and a["risk_score"] > 70)

    if low + med + high == 0:
        st.caption("Henüz veri yok")
        return

    fig = go.Figure(data=[go.Pie(
        labels=["Düşük", "Orta", "Yüksek"],
        values=[low, med, high],
        marker=dict(colors=["#27ae60", "#f39c12", "#e74c3c"]),
        hole=0.65, textinfo="value+percent", textfont_size=12,
    )])
    fig.update_layout(
        height=250, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(font=dict(color="#FAFAFA", size=11), orientation="h", y=-0.1),
        font=dict(color="#FAFAFA"),
    )
    st.plotly_chart(fig, use_container_width=True)
