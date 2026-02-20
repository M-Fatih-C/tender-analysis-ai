"""
TenderAI İhale Karşılaştırma Sayfası v2.0.
"""

import json
import streamlit as st
import plotly.graph_objects as go

from ui.components.header import render_header
from src.utils.helpers import risk_color_hex, safe_json_parse


def render_comparison() -> None:
    """İhale karşılaştırma sayfası."""
    render_header("⚖️ İhale Karşılaştır", "Birden fazla ihaleyi yan yana inceleyin")

    user_id = st.session_state.get("user_id", 0)
    analyses = _get_completed_analyses(user_id)

    if len(analyses) < 2:
        st.markdown(
            '<div class="onboarding-card">'
            '<div style="font-size:3rem;">⚖️</div>'
            '<h4>Karşılaştırma için en az 2 analiz gerekli</h4>'
            '<p style="color:#8892b0;">Daha fazla analiz yaparak karşılaştırma özelliğini kullanabilirsiniz.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("🔍 Yeni Analiz Yap", type="primary"):
            st.session_state["current_page"] = "analysis"
            st.session_state["analysis_state"] = "upload"
            st.rerun()
        return

    # Analiz seçimi
    st.markdown("##### 📄 Karşılaştırılacak Analizleri Seçin (2-5)")
    options = {a["id"]: f'{a["file_name"][:30]} (Risk: {a["risk_score"] or "—"})' for a in analyses}
    selected_ids = st.multiselect(
        "Analizler", list(options.keys()), format_func=lambda x: options[x],
        max_selections=5, label_visibility="collapsed",
    )

    if len(selected_ids) < 2:
        st.caption("En az 2 analiz seçin")
        return

    if st.button("📊 Karşılaştır", type="primary", use_container_width=True):
        selected = [a for a in analyses if a["id"] in selected_ids]
        _show_comparison(selected)


def _show_comparison(analyses: list) -> None:
    """Karşılaştırma sonuçlarını göster."""
    from src.ai_engine.comparator import IhaleComparator
    comp = IhaleComparator()

    items = []
    for a in analyses:
        result = safe_json_parse(a.get("result_json", "{}"))
        result["file_name"] = a["file_name"]
        result["risk_score"] = a.get("risk_score", 0) or result.get("risk_score", 0)
        result["risk_level"] = a.get("risk_level", "") or result.get("risk_level", "")
        items.append(result)

    comparison = comp.compare(items)
    rows = comparison.get("rows", [])
    best = comparison.get("best_choice", "")

    # Tablo
    st.markdown("##### 📊 Karşılaştırma Tablosu")
    html = '<table class="styled-table"><tr><th>Kriter</th>'
    for r in rows:
        is_best = r["name"][:20] == best[:20]
        cls = ' class="comparison-best"' if is_best else ""
        html += f'<th{cls}>{r["name"][:20]} {"🏆" if is_best else ""}</th>'
    html += '</tr>'

    fields = [
        ("Risk Skoru", "risk_score"),
        ("Bedel", "bedel"),
        ("Teminat", "teminat"),
        ("İş Süresi", "sure"),
        ("Belge Sayısı", "belge_sayisi"),
        ("Ceza Sayısı", "ceza_sayisi"),
        ("Tavsiye", "tavsiye"),
    ]

    for label, key in fields:
        html += f'<tr><td><strong>{label}</strong></td>'
        vals = [r.get(key, "—") for r in rows]
        for v in vals:
            color = ""
            if key == "risk_score" and isinstance(v, (int, float)):
                color = f' style="color:{risk_color_hex(int(v))};font-weight:700;"'
            html += f'<td{color}>{v}</td>'
        html += '</tr>'

    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # En iyi seçim kartı
    st.markdown(
        f'<div class="advice-card advice-gir" style="margin-bottom:1rem;">'
        f'<div class="advice-icon">🏆</div>'
        f'<div class="advice-title">En İyi Seçim: {best}</div>'
        f'<div class="advice-text">{comparison.get("best_reason", "")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Radar chart
    if len(rows) >= 2:
        _render_radar(rows)

    # Export
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        try:
            from src.report.excel_exporter import ExcelExporter
            exp = ExcelExporter()
            xlsx = exp.export_comparison(comparison)
            st.download_button("📊 Excel İndir", data=xlsx, file_name="TenderAI_karsilastirma.xlsx",
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception:
            pass


def _render_radar(rows: list) -> None:
    """Radar chart."""
    categories = ["Risk", "Belge", "Ceza", "Maliyet"]
    fig = go.Figure()

    for r in rows:
        risk_n = min(100, r.get("risk_score", 0))
        belge_n = min(100, r.get("belge_sayisi", 0) * 7)
        ceza_n = min(100, r.get("ceza_sayisi", 0) * 20)
        fig.add_trace(go.Scatterpolar(
            r=[risk_n, belge_n, ceza_n, risk_n],
            theta=categories + [categories[0]],
            fill='toself', name=r.get("name", "")[:20],
        ))

    fig.update_layout(
        polar=dict(bgcolor="rgba(0,0,0,0)"),
        height=350, margin=dict(l=50, r=50, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(font=dict(color="#FAFAFA")),
        font=dict(color="#FAFAFA"),
    )
    st.plotly_chart(fig, use_container_width=True)


def _get_completed_analyses(user_id: int) -> list:
    try:
        from src.database.db import DatabaseManager, get_user_analyses
        db_mgr = DatabaseManager()
        db_mgr.init_db()
        with db_mgr.get_db() as db:
            raw = get_user_analyses(db, user_id, limit=30)
            return [
                {"id": a.id, "file_name": a.file_name, "risk_score": a.risk_score,
                 "risk_level": a.risk_level, "result_json": a.result_json}
                for a in raw if a.status == "completed"
            ]
    except Exception:
        return []
