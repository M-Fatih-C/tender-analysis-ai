"""
TenderAI Geçmiş Analizler Sayfası / Analysis History Page.

Kullanıcının tüm geçmiş analizlerini listeler ve detay gösterir.
Lists all past analyses and shows details.
"""

import json
import streamlit as st

from src.database.db import DatabaseManager, get_user_analyses, get_analysis_by_id


def render_history_page() -> None:
    """Geçmiş analizler sayfasını render et / Render history page."""

    st.markdown("## 📁 Geçmiş Analizler")
    st.caption("Tüm analiz geçmişinizi görüntüleyin ve yönetin")

    user_id = st.session_state.get("user_id")

    # Detay görünümü kontrol / Detail view check
    if st.session_state.get("view_analysis_id"):
        _render_detail_view(st.session_state["view_analysis_id"])
        return

    st.divider()

    try:
        db_manager = DatabaseManager()
        db_manager.init_db()

        with db_manager.get_db() as db:
            analyses = get_user_analyses(db, user_id, limit=50) if user_id else []

            if not analyses:
                st.info(
                    "📭 Henüz analiz yapılmamış.\n\n"
                    "**Yeni Analiz** sayfasından ilk analizinizi başlatın!"
                )
                return

            # ── Filtreler / Filters ──
            col_search, col_risk, col_status = st.columns([3, 2, 2])

            with col_search:
                search_term = st.text_input(
                    "🔍 Dosya adına göre ara",
                    placeholder="Dosya adı...",
                    label_visibility="collapsed",
                )
            with col_risk:
                risk_filter = st.selectbox(
                    "Risk Seviyesi",
                    ["Tümü", "🟢 Düşük (0-40)", "🟡 Orta (41-70)", "🔴 Yüksek (71-100)"],
                    label_visibility="collapsed",
                )
            with col_status:
                status_filter = st.selectbox(
                    "Durum",
                    ["Tümü", "✅ Tamamlandı", "⏳ Bekliyor", "❌ Başarısız"],
                    label_visibility="collapsed",
                )

            # Filtreleme / Filtering
            filtered = _apply_filters(analyses, search_term, risk_filter, status_filter)

            st.caption(f"Toplam {len(filtered)} analiz gösteriliyor")
            st.divider()

            # ── Analiz Listesi / Analysis List ──
            for analysis in filtered:
                _render_analysis_row(analysis)

    except Exception as e:
        st.error(f"Geçmiş analizler yüklenirken hata: {e}")


def _apply_filters(analyses, search_term, risk_filter, status_filter) -> list:
    """Filtreleri uygula / Apply filters."""
    result = analyses

    # Dosya adı arama
    if search_term:
        result = [a for a in result if search_term.lower() in (a.file_name or "").lower()]

    # Risk filtresi
    if risk_filter == "🟢 Düşük (0-40)":
        result = [a for a in result if a.risk_score is not None and a.risk_score <= 40]
    elif risk_filter == "🟡 Orta (41-70)":
        result = [a for a in result if a.risk_score is not None and 41 <= a.risk_score <= 70]
    elif risk_filter == "🔴 Yüksek (71-100)":
        result = [a for a in result if a.risk_score is not None and a.risk_score >= 71]

    # Durum filtresi
    status_map = {
        "✅ Tamamlandı": "completed",
        "⏳ Bekliyor": "pending",
        "❌ Başarısız": "failed",
    }
    if status_filter in status_map:
        result = [a for a in result if a.status == status_map[status_filter]]

    return result


def _render_analysis_row(analysis) -> None:
    """Tek analiz satırı / Single analysis row."""
    score = analysis.risk_score
    risk_icon = "🟢" if score and score <= 40 else "🟡" if score and score <= 70 else "🔴" if score else "⚪"

    status_labels = {
        "pending": "⏳ Bekliyor",
        "processing": "🔄 İşleniyor",
        "completed": "✅ Tamamlandı",
        "failed": "❌ Başarısız",
    }

    date_str = analysis.created_at.strftime("%d.%m.%Y %H:%M") if analysis.created_at else "—"
    file_name = analysis.file_name or "—"

    col_date, col_file, col_risk, col_status, col_action = st.columns([2, 3, 1.5, 2, 1.5])

    with col_date:
        st.text(date_str)

    with col_file:
        st.text(file_name[:30] + "..." if len(file_name) > 30 else file_name)

    with col_risk:
        st.markdown(f"{risk_icon} **{score if score is not None else '—'}**")

    with col_status:
        st.text(status_labels.get(analysis.status, analysis.status))

    with col_action:
        if analysis.status == "completed":
            if st.button("👁️ Görüntüle", key=f"view_{analysis.id}"):
                st.session_state["view_analysis_id"] = analysis.id
                st.rerun()


def _render_detail_view(analysis_id: int) -> None:
    """Analiz detay görünümü / Analysis detail view."""

    if st.button("← Listeye Dön"):
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

            # Başlık bilgileri
            st.markdown(f"### 📄 {analysis.file_name}")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("📅 Tarih", analysis.created_at.strftime("%d.%m.%Y") if analysis.created_at else "—")
            with c2:
                st.metric("⚠️ Risk Skoru", analysis.risk_score or "—")
            with c3:
                st.metric("📊 Risk Seviyesi", analysis.risk_level or "—")
            with c4:
                st.metric("⏱️ Süre", f"{analysis.analysis_duration_seconds:.0f}s" if analysis.analysis_duration_seconds else "—")

            # Yönetici özeti
            if analysis.executive_summary:
                st.info(f"**Yönetici Özeti:** {analysis.executive_summary}")

            # Tam sonuç JSON
            if analysis.result_json:
                try:
                    result_data = json.loads(analysis.result_json)

                    # Sonuçları session'a yükle ve render et
                    result = {
                        "risk_score": analysis.risk_score,
                        "risk_level": analysis.risk_level,
                        "file_name": analysis.file_name,
                        "tokens_used": analysis.tokens_used,
                        "cost_usd": analysis.cost_usd,
                        "analysis_time": analysis.analysis_duration_seconds,
                        **result_data,
                    }

                    # analysis.py'deki render fonksiyonunu import et
                    from ui.pages.analysis import _render_results
                    _render_results(result)

                except json.JSONDecodeError:
                    st.warning("Analiz sonuçları parse edilemedi.")
            else:
                st.info("Bu analiz için detaylı sonuç verisi bulunmuyor.")

    except Exception as e:
        st.error(f"Analiz detayı yüklenirken hata: {e}")
