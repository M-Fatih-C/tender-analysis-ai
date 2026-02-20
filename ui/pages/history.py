"""
TenderAI Geçmiş Analizler Sayfası (Geliştirilmiş) / Analysis History Page (Enhanced).

Filtreli tablo, istatistik paneli, detay görünümü ve PDF indirme.
Filtered table, statistics panel, detail view, and PDF download.
"""

import json
from datetime import datetime, timedelta, timezone

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from src.database.db import DatabaseManager, get_user_analyses, get_analysis_by_id, get_analysis_stats
from src.report.generator import ReportGenerator
from src.utils.helpers import (
    format_risk_score,
    risk_color,
    format_date_turkish,
    format_file_size_mb,
    time_ago,
    truncate_text,
)


def render_history_page() -> None:
    """Geçmiş analizler sayfasını render et / Render history page."""

    st.markdown("## 📁 Geçmiş Analizler")
    st.caption("Tüm analiz geçmişinizi görüntüleyin, filtreleyin ve yönetin")

    user_id = st.session_state.get("user_id")

    # Detay görünümü / Detail view
    if st.session_state.get("view_analysis_id"):
        _render_detail_view(st.session_state["view_analysis_id"])
        return

    st.divider()

    try:
        db_manager = DatabaseManager()
        db_manager.init_db()

        with db_manager.get_db() as db:
            analyses = get_user_analyses(db, user_id, limit=100) if user_id else []
            stats = get_analysis_stats(db, user_id) if user_id else {}

            if not analyses:
                st.info(
                    "📭 Henüz analiz yapılmamış.\n\n"
                    "**Yeni Analiz** sayfasından ilk analizinizi başlatın!"
                )
                return

            # ── İstatistik Paneli / Statistics Panel ──
            _render_stats_panel(analyses, stats)

            st.divider()

            # ── Filtreler / Filters ──
            filtered = _render_filters(analyses)

            st.caption(f"**{len(filtered)}** analiz gösteriliyor (toplam {len(analyses)})")
            st.divider()

            # ── Sıralama / Sorting ──
            sort_col, sort_dir = st.columns([2, 1])
            with sort_col:
                sort_by = st.selectbox(
                    "Sırala",
                    ["Tarih (yeni→eski)", "Tarih (eski→yeni)", "Risk (yüksek→düşük)", "Risk (düşük→yüksek)", "Dosya adı (A-Z)"],
                    label_visibility="collapsed",
                )

            filtered = _sort_analyses(filtered, sort_by)

            # ── Analiz Listesi / Analysis List ──
            _render_analysis_list(filtered)

    except Exception as e:
        st.error(f"Geçmiş analizler yüklenirken hata: {e}")


# ============================================================
# İstatistik Paneli / Statistics Panel
# ============================================================


def _render_stats_panel(analyses: list, stats: dict) -> None:
    """İstatistik paneli / Statistics panel."""

    # ── Üst metrikler / Top metrics ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📄 Toplam Analiz", stats.get("total_analyses", 0))
    with c2:
        avg = stats.get("average_risk_score")
        st.metric("⚠️ Ort. Risk", f"{avg:.0f}" if avg is not None else "—")
    with c3:
        # En riskli ihale / Highest risk
        max_risk = max(
            (a for a in analyses if a.risk_score is not None),
            key=lambda a: a.risk_score,
            default=None,
        )
        if max_risk:
            st.metric("🔴 En Riskli", f"{max_risk.risk_score}")
        else:
            st.metric("🔴 En Riskli", "—")
    with c4:
        completed = sum(1 for a in analyses if a.status == "completed")
        st.metric("✅ Tamamlanan", completed)

    # ── Grafikler / Charts ──
    if len(analyses) >= 2:
        with st.expander("📊 İstatistik Grafikleri", expanded=False):
            chart1, chart2 = st.columns(2)

            with chart1:
                _render_risk_distribution_chart(analyses)

            with chart2:
                _render_risk_trend_chart(analyses)


def _render_risk_distribution_chart(analyses: list) -> None:
    """Risk dağılımı pie chart / Risk distribution pie chart."""
    low = sum(1 for a in analyses if a.risk_score is not None and a.risk_score <= 40)
    med = sum(1 for a in analyses if a.risk_score is not None and 41 <= a.risk_score <= 70)
    high = sum(1 for a in analyses if a.risk_score is not None and a.risk_score > 70)

    if low + med + high == 0:
        st.caption("Yeterli veri yok")
        return

    fig = go.Figure(data=[go.Pie(
        labels=["Düşük (0-40)", "Orta (41-70)", "Yüksek (71-100)"],
        values=[low, med, high],
        marker=dict(colors=["#27ae60", "#f39c12", "#e74c3c"]),
        hole=0.4,
        textinfo="value+percent",
    )])
    fig.update_layout(
        title="Risk Dağılımı",
        height=280,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(orientation="h", y=-0.1),
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_risk_trend_chart(analyses: list) -> None:
    """Risk trendi line chart / Risk trend line chart."""
    scored = [a for a in analyses if a.risk_score is not None and a.created_at is not None]
    if len(scored) < 2:
        st.caption("Trend için yeterli veri yok")
        return

    # Tarih sırasına göre / By date order
    scored = sorted(scored, key=lambda a: a.created_at)

    dates = [a.created_at.strftime("%d.%m") for a in scored]
    scores = [a.risk_score for a in scored]

    fig = go.Figure(data=go.Scatter(
        x=dates, y=scores,
        mode="lines+markers",
        line=dict(color="#667eea", width=2),
        marker=dict(size=6),
        fill="tozeroy",
        fillcolor="rgba(102,126,234,0.1)",
    ))
    fig.update_layout(
        title="Risk Skoru Trendi",
        height=280,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, 100], title="Skor"),
        xaxis=dict(title="Tarih"),
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# Filtreler / Filters
# ============================================================


def _render_filters(analyses: list) -> list:
    """Filtreleri render et ve uygula / Render and apply filters."""

    st.markdown("### 🔎 Filtreler")

    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

    with col1:
        search = st.text_input(
            "🔍 Dosya adı ara",
            placeholder="Dosya adı...",
            key="hist_search",
            label_visibility="collapsed",
        )

    with col2:
        risk_filter = st.multiselect(
            "Risk Seviyesi",
            ["🟢 Düşük", "🟡 Orta", "🔴 Yüksek"],
            default=[],
            key="hist_risk",
            label_visibility="collapsed",
            placeholder="Risk seviyesi",
        )

    with col3:
        status_filter = st.selectbox(
            "Durum",
            ["Tümü", "✅ Tamamlandı", "⏳ Bekliyor", "❌ Başarısız"],
            key="hist_status",
            label_visibility="collapsed",
        )

    with col4:
        date_range = st.selectbox(
            "Tarih",
            ["Tümü", "Son 7 gün", "Son 30 gün", "Son 90 gün"],
            key="hist_date",
            label_visibility="collapsed",
        )

    # Filtreleme uygula / Apply filters
    result = list(analyses)

    if search:
        result = [a for a in result if search.lower() in (a.file_name or "").lower()]

    if risk_filter:
        filtered_by_risk = []
        for a in result:
            s = a.risk_score
            if s is None:
                continue
            if "🟢 Düşük" in risk_filter and s <= 40:
                filtered_by_risk.append(a)
            elif "🟡 Orta" in risk_filter and 41 <= s <= 70:
                filtered_by_risk.append(a)
            elif "🔴 Yüksek" in risk_filter and s > 70:
                filtered_by_risk.append(a)
        result = filtered_by_risk

    status_map = {"✅ Tamamlandı": "completed", "⏳ Bekliyor": "pending", "❌ Başarısız": "failed"}
    if status_filter in status_map:
        result = [a for a in result if a.status == status_map[status_filter]]

    if date_range != "Tümü":
        days_map = {"Son 7 gün": 7, "Son 30 gün": 30, "Son 90 gün": 90}
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_map[date_range])
        result = [a for a in result if a.created_at and a.created_at >= cutoff]

    return result


def _sort_analyses(analyses: list, sort_by: str) -> list:
    """Analizleri sırala / Sort analyses."""
    if sort_by == "Tarih (yeni→eski)":
        return sorted(analyses, key=lambda a: a.created_at or datetime.min, reverse=True)
    elif sort_by == "Tarih (eski→yeni)":
        return sorted(analyses, key=lambda a: a.created_at or datetime.min)
    elif sort_by == "Risk (yüksek→düşük)":
        return sorted(analyses, key=lambda a: a.risk_score or 0, reverse=True)
    elif sort_by == "Risk (düşük→yüksek)":
        return sorted(analyses, key=lambda a: a.risk_score or 0)
    elif sort_by == "Dosya adı (A-Z)":
        return sorted(analyses, key=lambda a: (a.file_name or "").lower())
    return analyses


# ============================================================
# Analiz Listesi / Analysis List
# ============================================================


def _render_analysis_list(analyses: list) -> None:
    """Analiz listesi / Analysis list."""
    if not analyses:
        st.info("Filtrelere uygun analiz bulunamadı.")
        return

    # Başlık satırı / Header row
    cols = st.columns([2.5, 3, 1.5, 1.5, 2, 1.5])
    headers = ["📅 Tarih", "📄 Dosya", "⚠️ Risk", "📊 Skor", "🔄 Durum", ""]
    for col, header in zip(cols, headers):
        with col:
            st.markdown(f"**{header}**")

    st.divider()

    for analysis in analyses:
        _render_row(analysis)


def _render_row(analysis) -> None:
    """Tek analiz satırı / Single analysis row."""
    score = analysis.risk_score
    status_labels = {
        "pending": "⏳ Bekliyor",
        "processing": "🔄 İşleniyor",
        "completed": "✅ Tamamlandı",
        "failed": "❌ Başarısız",
    }

    cols = st.columns([2.5, 3, 1.5, 1.5, 2, 1.5])

    with cols[0]:
        if analysis.created_at:
            st.text(analysis.created_at.strftime("%d.%m.%Y %H:%M"))
        else:
            st.text("—")

    with cols[1]:
        name = analysis.file_name or "—"
        st.text(truncate_text(name, 28))

    with cols[2]:
        icon = "🟢" if score and score <= 40 else "🟡" if score and score <= 70 else "🔴" if score else "⚪"
        st.markdown(icon)

    with cols[3]:
        st.text(str(score) if score is not None else "—")

    with cols[4]:
        st.text(status_labels.get(analysis.status, analysis.status))

    with cols[5]:
        if analysis.status == "completed":
            if st.button("👁️", key=f"v_{analysis.id}", help="Detay görüntüle"):
                st.session_state["view_analysis_id"] = analysis.id
                st.rerun()


# ============================================================
# Detay Görünümü / Detail View
# ============================================================


def _render_detail_view(analysis_id: int) -> None:
    """Analiz detay görünümü / Analysis detail view."""

    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("← Geri"):
            st.session_state.pop("view_analysis_id", None)
            st.rerun()

    st.divider()

    try:
        db_manager = DatabaseManager()
        db_manager.init_db()

        with db_manager.get_db() as db:
            analysis = get_analysis_by_id(db, analysis_id)
            if not analysis:
                st.error("Analiz bulunamadı.")
                return

            # Başlık bilgileri / Title info
            st.markdown(f"### 📄 {analysis.file_name}")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("📅 Tarih", format_date_turkish(analysis.created_at))
            with c2:
                st.metric("⚠️ Risk", format_risk_score(analysis.risk_score))
            with c3:
                st.metric("📊 Seviye", analysis.risk_level or "—")
            with c4:
                dur = analysis.analysis_duration_seconds
                st.metric("⏱️ Süre", f"{dur:.0f}s" if dur else "—")

            # Yönetici özeti
            if analysis.executive_summary:
                st.info(f"**Özet:** {analysis.executive_summary}")

            # Aksiyon butonları / Action buttons
            btn1, btn2, btn3 = st.columns(3)

            # PDF İndirme / PDF Download
            with btn1:
                if analysis.result_json and analysis.status == "completed":
                    try:
                        result_data = json.loads(analysis.result_json)
                        result_for_pdf = {
                            "risk_score": analysis.risk_score,
                            "risk_level": analysis.risk_level,
                            **result_data,
                        }
                        gen = ReportGenerator()
                        pdf_bytes = gen.generate(result_for_pdf, analysis.file_name or "Rapor")
                        st.download_button(
                            "📥 PDF İndir",
                            data=pdf_bytes,
                            file_name=f"TenderAI_Rapor_{analysis.file_name}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.warning(f"PDF oluşturulamadı: {e}")

            # Token / maliyet bilgisi
            with btn2:
                if analysis.tokens_used:
                    st.caption(f"🔤 {analysis.tokens_used:,} token")
            with btn3:
                if analysis.cost_usd:
                    st.caption(f"💵 ${analysis.cost_usd:.4f}")

            st.divider()

            # Tam sonuçlar / Full results
            if analysis.result_json:
                try:
                    result_data = json.loads(analysis.result_json)
                    full_result = {
                        "risk_score": analysis.risk_score,
                        "risk_level": analysis.risk_level,
                        "file_name": analysis.file_name,
                        "tokens_used": analysis.tokens_used,
                        "cost_usd": analysis.cost_usd,
                        "analysis_time": analysis.analysis_duration_seconds,
                        **result_data,
                    }
                    from ui.pages.analysis import _render_results
                    _render_results(full_result)
                except json.JSONDecodeError:
                    st.warning("Analiz sonuçları parse edilemedi.")
            else:
                st.info("Bu analiz için detaylı sonuç verisi bulunmuyor.")

    except Exception as e:
        st.error(f"Analiz detayı yüklenirken hata: {e}")
