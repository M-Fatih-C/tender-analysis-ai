"""
TenderAI Premium Dashboard v3.0.

Gelişmiş Plotly grafikler: gauge chart, zaman serisi, trend analizi,
risk breakdown, uygunluk skoru entegrasyonu.
"""

import json
from datetime import datetime, timedelta
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from ui.components.header import render_header
from src.database.db import DatabaseManager, get_user_analyses, get_analysis_stats
from src.utils.helpers import time_ago_turkish, risk_color_hex, risk_level_text, safe_json_parse


def render_dashboard() -> None:
    """Premium dashboard."""
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
                raw = get_user_analyses(db, user_id, limit=50)
                for a in raw:
                    result = {}
                    if a.result_json:
                        result = safe_json_parse(a.result_json)
                    analyses.append({
                        "id": a.id, "file_name": a.file_name,
                        "risk_score": a.risk_score, "risk_level": a.risk_level,
                        "status": a.status, "created_at": a.created_at,
                        "total_pages": a.total_pages,
                        "executive_summary": a.executive_summary,
                        "result": result,
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

    # ── BÖLÜM 1: 4 Metrik Kartı ──
    c1, c2, c3, c4 = st.columns(4)
    _card(c1, "📄", "Toplam Analiz", total, "#667eea")
    _card(c2, "✅", "Tamamlanan", completed, "#27ae60")
    _risk_c = risk_color_hex(int(avg_risk)) if avg_risk else "#8892b0"
    _card(c3, "⚠️", "Ort. Risk Skoru", f"{avg_risk:.0f}" if avg_risk else "—", _risk_c)
    _card(c4, "📊", "Kalan Hak", "♾️" if remaining >= 9999 else remaining, "#f39c12")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Boş durum — İlk kullanıcı ──
    if not analyses:
        _render_empty_state()
        return

    # ── BÖLÜM 2: Gauge + Trend satırı ──
    gauge_col, trend_col = st.columns([1, 2])

    with gauge_col:
        st.markdown("#### 🎯 Ortalama Risk")
        _render_gauge(avg_risk or 0)

    with trend_col:
        st.markdown("#### 📈 Risk Trendi")
        _render_risk_trend(analyses)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── BÖLÜM 3: 3-kolon grafikler ──
    g1, g2, g3 = st.columns(3)

    with g1:
        st.markdown("#### 🥧 Risk Dağılımı")
        _render_risk_donut(analyses)

    with g2:
        st.markdown("#### 📊 Analiz Aktivitesi")
        _render_activity_chart(analyses)

    with g3:
        st.markdown("#### 🏆 En Son Analizler")
        _render_recent_scores(analyses)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── BÖLÜM 4: Son Analizler tablosu ──
    st.markdown("#### 📋 Son Analizler")
    _render_analysis_table(analyses[:8])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── BÖLÜM 5: Hızlı İşlemler ──
    st.markdown("#### ⚡ Hızlı İşlemler")
    q1, q2, q3, q4 = st.columns(4)

    _action(q1, "🔍", "Yeni Analiz", "PDF yükle, AI analiz et", "qa_analysis", "analysis")
    _action(q2, "⚖️", "Karşılaştır", "İhaleleri yan yana incele", "qa_compare", "comparison")
    _action(q3, "🏢", "Firma Profili", "Uygunluk skoru için doldurun", "qa_profile", "company_profile")
    _action(q4, "💬", "Şartnameye Sor", "AI chatbot ile soru sorun", "qa_chat", "chatbot")


# ==============================================================
# COMPONENTS
# ==============================================================

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


def _action(col, icon, title, desc, key, page):
    with col:
        st.markdown(
            f'<div class="action-card">'
            f'<div class="action-icon">{icon}</div>'
            f'<div class="action-title">{title}</div>'
            f'<div class="action-desc">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button("Başla →", key=key, use_container_width=True):
            st.session_state["current_page"] = page
            if page == "analysis":
                st.session_state["analysis_state"] = "upload"
            st.rerun()


def _render_empty_state():
    """Hiç analiz yok — güzel onboarding."""
    st.markdown(
        '<div class="onboarding-card">'
        '<div style="font-size:3rem;">🔍</div>'
        '<h3>İlk analizinizi yapın!</h3>'
        '<p style="color:#8892b0;">Şartname PDF\'inizi yükleyerek başlayın.<br>'
        'AI motorumuz risk analizi, belge kontrolü ve mali tarama yapacak.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    steps = [
        (c1, "📤", "Adım 1", "Şartname PDF yükleyin"),
        (c2, "🤖", "Adım 2", "AI analiz eder (30 sn)"),
        (c3, "📊", "Adım 3", "Detaylı rapor alın"),
    ]
    for col, icon, title, desc in steps:
        with col:
            st.markdown(
                f'<div class="action-card" style="border:1px dashed rgba(102,126,234,0.3);">'
                f'<div class="action-icon">{icon}</div>'
                f'<div class="action-title">{title}</div>'
                f'<div class="action-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Yeni Analiz Başlat", type="primary", use_container_width=True):
        st.session_state["current_page"] = "analysis"
        st.session_state["analysis_state"] = "upload"
        st.rerun()


# ==============================================================
# CHARTS
# ==============================================================

_PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#FAFAFA", family="Inter"),
    margin=dict(l=10, r=10, t=10, b=10),
)


def _render_gauge(score: float) -> None:
    """Risk skoru gauge chart."""
    score = int(score) if score else 0
    color = risk_color_hex(score)
    level = risk_level_text(score)

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        number=dict(font=dict(size=42, color=color)),
        title=dict(text=level, font=dict(size=14, color=color)),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1, tickcolor="#333", dtick=25),
            bar=dict(color=color, thickness=0.7),
            bgcolor="rgba(255,255,255,0.03)",
            borderwidth=0,
            steps=[
                dict(range=[0, 30], color="rgba(39,174,96,0.12)"),
                dict(range=[30, 50], color="rgba(46,204,113,0.08)"),
                dict(range=[50, 70], color="rgba(243,156,18,0.12)"),
                dict(range=[70, 85], color="rgba(231,76,60,0.12)"),
                dict(range=[85, 100], color="rgba(192,57,43,0.15)"),
            ],
            threshold=dict(
                line=dict(color="#f093fb", width=3),
                thickness=0.8,
                value=score,
            ),
        ),
    ))
    fig.update_layout(height=220, **_PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)


def _render_risk_trend(analyses: list) -> None:
    """Risk skorları zaman serisi."""
    completed = [a for a in analyses if a["risk_score"] is not None and a["created_at"]]
    completed.sort(key=lambda x: x["created_at"])

    if len(completed) < 2:
        st.caption("Trend için en az 2 analiz gerekli")
        return

    dates = [a["created_at"] for a in completed]
    scores = [a["risk_score"] for a in completed]
    names = [(a["file_name"] or "")[:20] for a in completed]
    colors = [risk_color_hex(s) for s in scores]

    fig = go.Figure()

    # Arka plan bölgeleri
    fig.add_hrect(y0=0, y1=40, fillcolor="rgba(39,174,96,0.05)", line_width=0)
    fig.add_hrect(y0=40, y1=70, fillcolor="rgba(243,156,18,0.05)", line_width=0)
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(231,76,60,0.05)", line_width=0)

    # Trend çizgisi
    fig.add_trace(go.Scatter(
        x=dates, y=scores, mode="lines+markers",
        line=dict(color="#667eea", width=2.5, shape="spline"),
        marker=dict(size=8, color=colors, line=dict(width=2, color="#0a0a1a")),
        text=names, hovertemplate="<b>%{text}</b><br>Risk: %{y}<br>%{x|%d %b %Y}<extra></extra>",
        fill="tozeroy", fillcolor="rgba(102,126,234,0.06)",
    ))

    # Ortalama çizgisi
    avg = sum(scores) / len(scores)
    fig.add_hline(y=avg, line=dict(color="#f093fb", width=1, dash="dot"),
                  annotation_text=f"Ort: {avg:.0f}", annotation_position="top right",
                  annotation_font_color="#f093fb", annotation_font_size=10)

    fig.update_layout(
        height=220,
        xaxis=dict(showgrid=False, showline=False),
        yaxis=dict(range=[0, 100], showgrid=True, gridcolor="rgba(255,255,255,0.04)", showline=False),
        showlegend=False,
        **_PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_risk_donut(analyses: list) -> None:
    """Risk dağılımı donut chart."""
    low = sum(1 for a in analyses if a["risk_score"] and a["risk_score"] <= 40)
    med = sum(1 for a in analyses if a["risk_score"] and 41 <= a["risk_score"] <= 70)
    high = sum(1 for a in analyses if a["risk_score"] and a["risk_score"] > 70)

    if low + med + high == 0:
        st.caption("Henüz risk verisi yok")
        return

    fig = go.Figure(data=[go.Pie(
        labels=["Düşük", "Orta", "Yüksek"],
        values=[low, med, high],
        marker=dict(
            colors=["#27ae60", "#f39c12", "#e74c3c"],
            line=dict(color="#0a0a1a", width=2),
        ),
        hole=0.7,
        textinfo="value+percent",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>%{value} analiz (%{percent})<extra></extra>",
    )])

    # Ortadaki sayı
    fig.add_annotation(
        text=f"<b>{low + med + high}</b><br><span style='font-size:10px;color:#8892b0;'>Toplam</span>",
        showarrow=False, font=dict(size=18, color="#FAFAFA"),
    )

    fig.update_layout(
        height=220, showlegend=True,
        legend=dict(font=dict(color="#FAFAFA", size=10), orientation="h", y=-0.05, x=0.1),
        **_PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_activity_chart(analyses: list) -> None:
    """Haftalık analiz aktivitesi bar chart."""
    now = datetime.now()
    weeks = {}
    for i in range(6, -1, -1):
        d = now - timedelta(days=i)
        key = d.strftime("%a")
        weeks[key] = 0

    for a in analyses:
        if a["created_at"]:
            diff = (now - a["created_at"]).days
            if 0 <= diff < 7:
                key = a["created_at"].strftime("%a")
                if key in weeks:
                    weeks[key] += 1

    days = list(weeks.keys())
    counts = list(weeks.values())

    fig = go.Figure(data=[go.Bar(
        x=days, y=counts,
        marker=dict(
            color=["#667eea" if c > 0 else "rgba(102,126,234,0.15)" for c in counts],
            cornerradius=6,
        ),
        hovertemplate="<b>%{x}</b><br>%{y} analiz<extra></extra>",
    )])

    fig.update_layout(
        height=220,
        xaxis=dict(showgrid=False, showline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", showline=False, dtick=1),
        showlegend=False, bargap=0.4,
        **_PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_recent_scores(analyses: list) -> None:
    """Son analizlerin horizontal bar chart."""
    recent = [a for a in analyses if a["risk_score"] is not None][:5]
    if not recent:
        st.caption("Henüz skor yok")
        return

    recent.reverse()
    names = [(a["file_name"] or "—")[:18] for a in recent]
    scores = [a["risk_score"] for a in recent]
    colors = [risk_color_hex(s) for s in scores]

    fig = go.Figure(data=[go.Bar(
        y=names, x=scores, orientation="h",
        marker=dict(color=colors, cornerradius=4),
        text=[str(s) for s in scores],
        textposition="outside", textfont=dict(color="#FAFAFA", size=11),
        hovertemplate="<b>%{y}</b><br>Risk: %{x}<extra></extra>",
    )])

    fig.update_layout(
        height=220,
        xaxis=dict(range=[0, 110], showgrid=False, showline=False, showticklabels=False),
        yaxis=dict(showgrid=False, showline=False, tickfont=dict(size=10)),
        showlegend=False,
        **_PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_analysis_table(analyses: list) -> None:
    """Son analizler tablosu."""
    if not analyses:
        return

    html = '<table class="styled-table"><tr>'
    html += '<th>Dosya</th><th>Risk</th><th>Seviye</th><th>Durum</th><th>Tarih</th><th>İşlem</th>'
    html += '</tr>'

    for a in analyses:
        score = a["risk_score"]
        color = risk_color_hex(score) if score else "#555"
        badge_cls = "risk-badge-low"
        if score and score > 70:
            badge_cls = "risk-badge-high"
        elif score and score > 40:
            badge_cls = "risk-badge-medium"

        level = a.get("risk_level", "—") or "—"
        status = "✅" if a["status"] == "completed" else "⏳" if a["status"] == "pending" else "❌"
        time_str = time_ago_turkish(a["created_at"])

        html += (
            f'<tr>'
            f'<td>📄 {(a["file_name"] or "—")[:25]}</td>'
            f'<td style="color:{color};font-weight:700;">{score if score is not None else "—"}</td>'
            f'<td><span class="risk-badge {badge_cls}">{level}</span></td>'
            f'<td>{status}</td>'
            f'<td>{time_str}</td>'
            f'<td style="font-size:0.8rem;">💬 📥</td>'
            f'</tr>'
        )

    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)
