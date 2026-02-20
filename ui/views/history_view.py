"""
TenderAI Geçmiş Analizler Sayfası / History Page.
"""

import json
import streamlit as st

from ui.components.header import render_header
from src.database.db import DatabaseManager, get_user_analyses, get_analysis_stats


def render_history() -> None:
    """Geçmiş analizler sayfasını render et / Render history page."""
    render_header("Geçmiş Analizler", "Tüm analiz geçmişinizi görüntüleyin")

    user_id = st.session_state.get("user_id", 0)
    if not user_id:
        st.info("Geçmiş analizler için giriş yapın.")
        return

    analyses = []
    try:
        db_mgr = DatabaseManager()
        db_mgr.init_db()
        with db_mgr.get_db() as db:
            raw = get_user_analyses(db, user_id, limit=50)
            for a in raw:
                analyses.append({
                    "id": a.id,
                    "file_name": a.file_name,
                    "risk_score": a.risk_score,
                    "risk_level": a.risk_level,
                    "status": a.status,
                    "created_at": a.created_at,
                    "executive_summary": a.executive_summary,
                    "analysis_duration_seconds": a.analysis_duration_seconds,
                    "result_json": a.result_json,
                })
    except Exception as e:
        st.error(f"Veriler yüklenemedi: {e}")
        return

    if not analyses:
        st.info("📭 Henüz analiz yapılmamış. **Yeni Analiz** sayfasından başlayın!")
        if st.button("🔍 Yeni Analiz'e Git", type="primary"):
            st.session_state["current_page"] = "analysis"
            st.session_state["analysis_state"] = "upload"
            st.rerun()
        return

    # ── Filtreler ──
    c1, c2, c3 = st.columns([3, 2, 2])
    with c1:
        search = st.text_input("🔍 Dosya adı ara", placeholder="Ara...", label_visibility="collapsed")
    with c2:
        risk_filter = st.multiselect(
            "Risk", ["🟢 Düşük", "🟡 Orta", "🔴 Yüksek"],
            placeholder="Risk seviyesi", label_visibility="collapsed",
        )
    with c3:
        status_filter = st.selectbox(
            "Durum", ["Tümü", "✅ Tamamlandı", "❌ Başarısız"],
            label_visibility="collapsed",
        )

    # Filtrele
    filtered = list(analyses)
    if search:
        filtered = [a for a in filtered if search.lower() in (a["file_name"] or "").lower()]
    if risk_filter:
        temp = []
        for a in filtered:
            s = a["risk_score"]
            if s is None:
                continue
            if "🟢 Düşük" in risk_filter and s <= 40:
                temp.append(a)
            elif "🟡 Orta" in risk_filter and 41 <= s <= 70:
                temp.append(a)
            elif "🔴 Yüksek" in risk_filter and s > 70:
                temp.append(a)
        filtered = temp
    if status_filter == "✅ Tamamlandı":
        filtered = [a for a in filtered if a["status"] == "completed"]
    elif status_filter == "❌ Başarısız":
        filtered = [a for a in filtered if a["status"] == "failed"]

    st.caption(f"**{len(filtered)}** analiz gösteriliyor")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # ── Analiz kartları ──
    for a in filtered:
        score = a["risk_score"]
        border = "#27ae60" if score and score <= 40 else "#f39c12" if score and score <= 70 else "#e74c3c" if score else "#555"
        date_str = a["created_at"].strftime("%d.%m.%Y %H:%M") if a["created_at"] else "—"
        status_icon = "✅" if a["status"] == "completed" else "⏳" if a["status"] == "pending" else "❌"

        st.markdown(
            f'<div class="analysis-card" style="border-left-color:{border};">'
            f'<div class="card-header">'
            f'<span class="card-title">📄 {(a["file_name"] or "—")[:40]}</span>'
            f'<span class="card-score" style="color:{border};">{score if score is not None else "—"}</span>'
            f'</div>'
            f'<div class="card-date">{date_str} · {status_icon}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if a["status"] == "completed":
            with st.expander(f"📋 Detaylar — {(a['file_name'] or '')[:25]}"):
                if a["executive_summary"]:
                    st.info(a["executive_summary"])

                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    st.metric("Risk", score or "—")
                with mc2:
                    st.metric("Seviye", a["risk_level"] or "—")
                with mc3:
                    dur = a["analysis_duration_seconds"]
                    st.metric("Süre", f"{dur:.0f}s" if dur else "—")

                # PDF indir
                if a["result_json"]:
                    try:
                        result_data = json.loads(a["result_json"]) if isinstance(a["result_json"], str) else a["result_json"]
                        result_for_pdf = {"risk_score": score, "risk_level": a["risk_level"], **result_data}
                        from src.report.generator import ReportGenerator
                        gen = ReportGenerator()
                        pdf_bytes = gen.generate(result_for_pdf, a["file_name"] or "rapor")
                        st.download_button(
                            "📥 PDF İndir", data=pdf_bytes,
                            file_name=f"TenderAI_{a['file_name']}.pdf",
                            mime="application/pdf",
                            key=f"dl_{a['id']}",
                        )
                    except Exception:
                        pass
