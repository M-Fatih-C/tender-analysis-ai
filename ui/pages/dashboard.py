"""
TenderAI Dashboard Sayfası / Dashboard Page.

Kullanıcının genel istatistiklerini ve son analizlerini gösterir.
Shows user's overall statistics and recent analyses.
"""

import streamlit as st
import plotly.graph_objects as go

from src.database.db import DatabaseManager, get_user_analyses, get_analysis_stats


def render_dashboard() -> None:
    """Dashboard sayfasını render et / Render dashboard page."""

    user_name = st.session_state.get("user_name", "Kullanıcı")
    user_id = st.session_state.get("user_id")

    st.markdown(f"## 📊 Hoş Geldiniz, {user_name}!")
    st.caption("İhale analiz platformunuzun genel görünümü")

    st.divider()

    try:
        db_manager = DatabaseManager()
        db_manager.init_db()

        with db_manager.get_db() as db:
            stats = get_analysis_stats(db, user_id) if user_id else {}
            recent_analyses = get_user_analyses(db, user_id, limit=5) if user_id else []

            # ── Metrik Kartları / Metric Cards ──
            _render_metrics(stats)

            st.divider()

            # ── Son Analizler / Recent Analyses ──
            _render_recent_analyses(recent_analyses)

    except Exception as e:
        st.error(f"Dashboard yüklenirken hata: {e}")
        _render_metrics({})
        st.divider()
        _render_recent_analyses([])

    st.divider()

    # Hızlı aksiyon / Quick action
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Yeni Analiz Başlat", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "analysis"
            st.rerun()


def _render_metrics(stats: dict) -> None:
    """Metrik kartlarını render et / Render metric cards."""
    total = stats.get("total_analyses", 0)
    completed = stats.get("completed_analyses", 0)
    avg_risk = stats.get("average_risk_score")
    max_analysis = _get_max_analysis()
    analysis_count = st.session_state.get("analysis_count", 0)
    remaining = max(0, max_analysis - analysis_count) if max_analysis < 999 else "♾️"

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("📄 Toplam Analiz", total)
    with c2:
        st.metric("✅ Tamamlanan", completed)
    with c3:
        risk_display = f"{avg_risk:.0f}" if avg_risk is not None else "—"
        st.metric("⚠️ Ort. Risk Skoru", risk_display)
    with c4:
        st.metric("🎫 Kalan Hak", remaining)


def _render_recent_analyses(analyses: list) -> None:
    """Son analizleri tablo olarak göster / Show recent analyses as table."""
    st.markdown("### 📈 Son Analizler")

    if not analyses:
        st.info("Henüz analiz yapılmamış. İlk analizinizi başlatmak için **Yeni Analiz** sayfasına gidin.")
        return

    # Tablo başlıkları / Table headers
    cols = st.columns([2, 3, 1.5, 1.5, 2])
    with cols[0]:
        st.markdown("**📅 Tarih**")
    with cols[1]:
        st.markdown("**📄 Dosya**")
    with cols[2]:
        st.markdown("**⚠️ Risk**")
    with cols[3]:
        st.markdown("**📊 Skor**")
    with cols[4]:
        st.markdown("**🔄 Durum**")

    st.divider()

    # Analiz satırları / Analysis rows
    for analysis in analyses:
        cols = st.columns([2, 3, 1.5, 1.5, 2])

        with cols[0]:
            date_str = (
                analysis.created_at.strftime("%d.%m.%Y")
                if analysis.created_at else "—"
            )
            st.text(date_str)

        with cols[1]:
            name = analysis.file_name or "—"
            if len(name) > 25:
                name = name[:22] + "..."
            st.text(name)

        with cols[2]:
            _render_risk_badge(analysis.risk_score)

        with cols[3]:
            score = analysis.risk_score
            st.text(f"{score}" if score is not None else "—")

        with cols[4]:
            status_labels = {
                "pending": "⏳ Bekliyor",
                "processing": "🔄 İşleniyor",
                "completed": "✅ Tamamlandı",
                "failed": "❌ Başarısız",
            }
            st.text(status_labels.get(analysis.status, analysis.status))


def _render_risk_badge(score: int | None) -> None:
    """Risk skoru rozetini göster / Render risk score badge."""
    if score is None:
        st.text("—")
        return

    if score <= 40:
        st.markdown(f"🟢")
    elif score <= 70:
        st.markdown(f"🟡")
    else:
        st.markdown(f"🔴")


def _get_max_analysis() -> int:
    """Plan bazlı maksimum analiz / Plan-based max analysis."""
    plan = st.session_state.get("user_plan", "free")
    limits = {"free": 3, "starter": 20, "pro": 999, "enterprise": 999}
    return limits.get(plan, 3)
