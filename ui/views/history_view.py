"""
TenderAI Premium Geçmiş Analizler v2.0.
"""

import json
import streamlit as st
from ui.components.header import render_header
from src.database.db import DatabaseManager, get_user_analyses
from src.utils.helpers import (
    time_ago_turkish, risk_color_hex, safe_json_parse,
    format_date_turkish,
)


def render_history() -> None:
    """Geçmiş analizler sayfası."""
    render_header("📁 Geçmiş Analizler", "Tüm analizlerinize göz atın")
    user_id = st.session_state.get("user_id", 0)

    # Veri çek
    analyses = _load_analyses(user_id)

    # ── İstatistik şeridi ──
    total = len(analyses)
    completed = sum(1 for a in analyses if a["status"] == "completed")
    avg_risk = 0
    risk_scores = [a["risk_score"] for a in analyses if a["risk_score"]]
    if risk_scores:
        avg_risk = sum(risk_scores) / len(risk_scores)
    max_risk = max(risk_scores) if risk_scores else 0

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("📄 Toplam", total)
    with s2:
        st.metric("✅ Tamamlanan", completed)
    with s3:
        st.metric("⚠️ Ort. Risk", f"{avg_risk:.0f}" if avg_risk else "—")
    with s4:
        st.metric("🔴 En Yüksek Risk", max_risk if max_risk else "—")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    if not analyses:
        st.markdown(
            '<div class="onboarding-card">'
            '<div style="font-size:3rem;">📭</div>'
            '<h4>Henüz analiz yapılmamış</h4>'
            '<p style="color:#8892b0;">İlk analizinizi yaparak başlayın!</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("🔍 Yeni Analiz", type="primary"):
            st.session_state["current_page"] = "analysis"
            st.session_state["analysis_state"] = "upload"
            st.rerun()
        return

    # ── Filtreler ──
    f1, f2, f3, f4 = st.columns([3, 2, 2, 2])
    with f1:
        search = st.text_input("🔍 Dosya adı ara", placeholder="Ara...", label_visibility="collapsed")
    with f2:
        risk_filter = st.multiselect("Risk", ["🟢 Düşük", "🟡 Orta", "🔴 Yüksek"], label_visibility="collapsed")
    with f3:
        status_filter = st.selectbox("Durum", ["Tümü", "✅ Tamamlandı", "❌ Başarısız"], label_visibility="collapsed")
    with f4:
        sort_by = st.selectbox("Sırala", ["Tarih ↓", "Tarih ↑", "Risk ↓", "Risk ↑"], label_visibility="collapsed")

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

    # Sırala
    if sort_by == "Tarih ↑":
        filtered.sort(key=lambda x: x.get("created_at") or "", reverse=False)
    elif sort_by == "Risk ↓":
        filtered.sort(key=lambda x: x.get("risk_score") or 0, reverse=True)
    elif sort_by == "Risk ↑":
        filtered.sort(key=lambda x: x.get("risk_score") or 0, reverse=False)

    st.caption(f"**{len(filtered)}** analiz gösteriliyor")

    # ── Kartlar ──
    for a in filtered:
        score = a["risk_score"]
        border = risk_color_hex(score) if score else "#555"
        time_str = time_ago_turkish(a["created_at"])
        status_icon = "✅" if a["status"] == "completed" else "⏳" if a["status"] == "pending" else "❌"

        st.markdown(
            f'<div class="analysis-card" style="border-left-color:{border};">'
            f'<div class="card-header">'
            f'<span class="card-title">📄 {(a["file_name"] or "—")[:40]}</span>'
            f'<span class="card-score" style="color:{border};">{score if score is not None else "—"}</span>'
            f'</div>'
            f'<div class="card-date">{time_str} · {status_icon}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if a["status"] == "completed":
            with st.expander(f"📋 Detaylar — {(a['file_name'] or '')[:25]}"):
                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    st.metric("Risk", score or "—")
                with mc2:
                    st.metric("Seviye", a["risk_level"] or "—")
                with mc3:
                    dur = a["analysis_duration_seconds"]
                    st.metric("Süre", f"{dur:.0f}s" if dur else "—")

                if a["executive_summary"]:
                    st.info(a["executive_summary"][:200])

                # Aksiyon butonları
                bc1, bc2, bc3, bc4 = st.columns(4)
                with bc1:
                    if a["result_json"]:
                        try:
                            result_data = safe_json_parse(a["result_json"])
                            result_for_pdf = {"risk_score": score, "risk_level": a["risk_level"], **result_data}
                            from src.report.generator import ReportGenerator
                            gen = ReportGenerator()
                            pdf_bytes = gen.generate(result_for_pdf, a["file_name"] or "rapor")
                            st.download_button("📥 PDF", data=pdf_bytes, file_name=f"TenderAI_{a['file_name']}.pdf",
                                              mime="application/pdf", key=f"pdf_{a['id']}")
                        except Exception:
                            pass
                with bc2:
                    if a["result_json"]:
                        try:
                            from src.report.excel_exporter import ExcelExporter
                            result_data = safe_json_parse(a["result_json"])
                            exp = ExcelExporter()
                            xlsx = exp.export(result_data, a["file_name"] or "rapor")
                            st.download_button("📊 Excel", data=xlsx, file_name=f"TenderAI_{a['file_name']}.xlsx",
                                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                              key=f"xlsx_{a['id']}")
                        except Exception:
                            pass
                with bc3:
                    if a["result_json"]:
                        try:
                            from src.report.docx_exporter import generate_docx_report
                            result_data = safe_json_parse(a["result_json"])
                            docx_bytes = generate_docx_report(result_data, a["file_name"] or "rapor")
                            st.download_button("📝 Word", data=docx_bytes, file_name=f"TenderAI_{a['file_name']}.docx",
                                              mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                              key=f"docx_{a['id']}")
                        except Exception:
                            pass
                with bc4:
                    if st.button("💬 Soru Sor", key=f"chat_{a['id']}"):
                        st.session_state["chatbot_analysis_id"] = a["id"]
                        st.session_state["current_page"] = "chatbot"
                        st.rerun()


def _load_analyses(user_id: int) -> list:
    """Analizleri dict olarak yükle."""
    try:
        db_mgr = DatabaseManager()
        db_mgr.init_db()
        with db_mgr.get_db() as db:
            raw = get_user_analyses(db, user_id, limit=50)
            return [
                {
                    "id": a.id, "file_name": a.file_name,
                    "risk_score": a.risk_score, "risk_level": a.risk_level,
                    "status": a.status, "created_at": a.created_at,
                    "executive_summary": a.executive_summary,
                    "analysis_duration_seconds": a.analysis_duration_seconds,
                    "result_json": a.result_json,
                }
                for a in raw
            ]
    except Exception:
        return []
