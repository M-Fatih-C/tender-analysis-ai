"""
TenderAI Analiz Sayfası / Analysis Page.

3 aşamalı state machine: upload → analyzing → results.
"""

import io
import json
import time
import asyncio
import logging
import streamlit as st

from ui.components.header import render_header
from config.demo_data import DEMO_ANALYSIS_RESULT

logger = logging.getLogger(__name__)


def render_analysis() -> None:
    """Analiz sayfasını render et / Render analysis page."""
    render_header("Yeni Analiz", "İhale şartname PDF'ini yükleyin ve analiz edin")

    state = st.session_state.get("analysis_state", "upload")

    if state == "upload":
        _render_upload()
    elif state == "analyzing":
        _render_analyzing()
    elif state == "results":
        _render_results()


# ============================================================
# AŞAMA 1: UPLOAD
# ============================================================

def _render_upload() -> None:
    """PDF yükleme aşaması."""
    # Limit kontrolü
    plan = st.session_state.get("user_plan", "free")
    limit_map = {"free": 3, "starter": 20, "pro": 9999}
    count = st.session_state.get("analysis_count", 0)
    limit = limit_map.get(plan, 3)

    if count >= limit and limit < 9999:
        st.warning(f"⚠️ Aylık analiz limitiniz ({limit}) doldu.")
        if st.button("💳 Planınızı Yükseltin", type="primary"):
            st.session_state["current_page"] = "payment"
            st.rerun()
        return

    st.markdown(
        "<div style='text-align:center;padding:1rem 0;'>"
        "<span style='font-size:3rem;'>📤</span><br>"
        "<span style='color:#8892b0;'>İhale şartname PDF dosyasını yükleyin</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "PDF yükle", type=["pdf"], label_visibility="collapsed",
        help="Maksimum 50MB, sadece PDF formatı",
    )

    if uploaded:
        size_mb = len(uploaded.getvalue()) / (1024 * 1024)

        if size_mb > 50:
            st.error("❌ Dosya boyutu 50MB'ı aşıyor.")
            return

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="metric-card"><div class="metric-icon">📄</div>'
                f'<div class="metric-value" style="font-size:1rem;">{uploaded.name[:30]}</div>'
                f'<div class="metric-label">Dosya Adı</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="metric-card"><div class="metric-icon">💾</div>'
                f'<div class="metric-value" style="font-size:1rem;">{size_mb:.1f} MB</div>'
                f'<div class="metric-label">Boyut</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="metric-card"><div class="metric-icon">📋</div>'
                f'<div class="metric-value" style="font-size:1rem;">PDF</div>'
                f'<div class="metric-label">Format</div></div>',
                unsafe_allow_html=True,
            )

        # Ön izleme
        try:
            uploaded.seek(0)
            from src.pdf_parser.parser import IhalePDFParser
            parser = IhalePDFParser()
            doc = parser.parse(uploaded.getvalue())
            preview = doc.full_text[:1000] if doc.full_text else "Metin çıkarılamadı."
            with st.expander("📖 Ön İzleme (ilk 1000 karakter)"):
                st.text(preview)
        except Exception:
            pass

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 AI Analizi Başlat", use_container_width=True, type="primary"):
            st.session_state["uploaded_file_bytes"] = uploaded.getvalue()
            st.session_state["uploaded_file_name"] = uploaded.name
            st.session_state["uploaded_file_size"] = size_mb
            st.session_state["analysis_state"] = "analyzing"
            st.rerun()


# ============================================================
# AŞAMA 2: ANALYZING
# ============================================================

def _render_analyzing() -> None:
    """Analiz devam ediyor aşaması."""
    st.markdown(
        "<div style='text-align:center;padding:2rem 0;'>"
        "<span style='font-size:3rem;'>🤖</span><br>"
        "<h3>AI Analiz Ediliyor...</h3>"
        "<p style='color:#8892b0;'>Şartname yapay zeka ile inceleniyor, lütfen bekleyin</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    progress = st.progress(0)
    status = st.empty()

    steps = [
        (5, "📄 PDF okunuyor..."),
        (15, "📝 Metin çıkarılıyor..."),
        (25, "🧠 Vektör veritabanı hazırlanıyor..."),
        (35, "⚠️ Risk analizi yapılıyor..."),
        (50, "📋 Belge kontrolü yapılıyor..."),
        (65, "💰 Ceza maddeleri taranıyor..."),
        (75, "💵 Mali analiz yapılıyor..."),
        (85, "⏱️ Süre analizi yapılıyor..."),
        (95, "📊 Yönetici özeti hazırlanıyor..."),
    ]

    try:
        file_bytes = st.session_state.get("uploaded_file_bytes")
        file_name = st.session_state.get("uploaded_file_name", "document.pdf")

        if not file_bytes:
            st.error("Dosya bulunamadı. Lütfen tekrar yükleyin.")
            st.session_state["analysis_state"] = "upload"
            return

        # Progress animasyonu başlat
        for pct, msg in steps[:3]:
            progress.progress(pct / 100)
            status.info(msg)
            time.sleep(0.3)

        # PDF parse
        from src.pdf_parser.parser import IhalePDFParser
        parser = IhalePDFParser()
        doc = parser.parse(file_bytes)

        for pct, msg in steps[3:5]:
            progress.progress(pct / 100)
            status.info(msg)
            time.sleep(0.2)

        # AI analiz veya demo
        from config.settings import settings
        api_key = settings.OPENAI_API_KEY
        demo_mode = st.session_state.get("demo_mode", False) or settings.DEMO_MODE

        use_ai = (
            not demo_mode
            and api_key
            and api_key != "sk-your-key-here"
            and len(api_key) > 10
        )

        if use_ai:
            for pct, msg in steps[5:]:
                progress.progress(pct / 100)
                status.info(msg)
                time.sleep(0.2)

            from src.ai_engine.analyzer import IhaleAnalizAI
            engine = IhaleAnalizAI(openai_api_key=api_key)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(engine.analyze(doc))
            finally:
                loop.close()

            # AnalysisResult → dict
            if hasattr(result, "__dict__"):
                result_dict = {k: v for k, v in result.__dict__.items() if not k.startswith("_")}
            elif isinstance(result, dict):
                result_dict = result
            else:
                result_dict = DEMO_ANALYSIS_RESULT
        else:
            # Demo sonuçları
            for pct, msg in steps[5:]:
                progress.progress(pct / 100)
                status.info(msg)
                time.sleep(0.4)
            result_dict = dict(DEMO_ANALYSIS_RESULT)

        progress.progress(1.0)
        status.success("✅ Analiz tamamlandı!")
        time.sleep(0.5)

        # DB kaydet
        _save_to_db(result_dict, file_name, st.session_state.get("uploaded_file_size", 0), doc)

        # Session'a kaydet
        st.session_state["analysis_result"] = result_dict
        st.session_state["analysis_state"] = "results"
        st.rerun()

    except Exception as e:
        logger.error(f"Analiz hatası: {e}", exc_info=True)
        st.error(f"❌ Analiz sırasında hata oluştu: {e}")
        if st.button("🔄 Tekrar Dene"):
            st.session_state["analysis_state"] = "upload"
            st.rerun()


def _save_to_db(result: dict, file_name: str, size_mb: float, doc) -> None:
    """Sonuçları DB'ye kaydet."""
    try:
        user_id = st.session_state.get("user_id", 0)
        if not user_id:
            return

        from src.database.db import (
            DatabaseManager, create_analysis,
            update_analysis_result, increment_analysis_count,
        )

        db_mgr = DatabaseManager()
        db_mgr.init_db()
        with db_mgr.get_db() as db:
            analysis = create_analysis(
                db, user_id,
                file_name=file_name,
                file_size_mb=size_mb,
                total_pages=doc.metadata.total_pages if doc.metadata else None,
            )

            exec_summary = ""
            exec_data = result.get("executive_summary", {})
            if isinstance(exec_data, dict):
                exec_summary = exec_data.get("ozet", "")
            elif isinstance(exec_data, str):
                exec_summary = exec_data

            update_analysis_result(
                db, analysis.id,
                risk_score=result.get("risk_score", 0),
                risk_level=result.get("risk_level", "—"),
                result_json=result,
                executive_summary=exec_summary[:500],
                tokens_used=result.get("tokens_used", 0),
                cost_usd=result.get("cost_usd", 0),
                analysis_duration_seconds=result.get("analysis_time", 0),
            )
            increment_analysis_count(db, user_id)

        # Session güncelle
        st.session_state["analysis_count"] = st.session_state.get("analysis_count", 0) + 1
    except Exception as e:
        logger.error(f"DB kayıt hatası: {e}", exc_info=True)


# ============================================================
# AŞAMA 3: RESULTS
# ============================================================

def _render_results() -> None:
    """Analiz sonuçları aşaması."""
    result = st.session_state.get("analysis_result", {})
    if not result:
        st.warning("Sonuç bulunamadı.")
        st.session_state["analysis_state"] = "upload"
        return

    score = result.get("risk_score", 0)
    level = result.get("risk_level", "—")

    # Renk
    if score <= 40:
        color = "#27ae60"
        advice_class, advice_icon, advice_title, advice_text = "advice-gir", "✅", "GİR", "Bu ihaleye katılım önerilir."
    elif score <= 70:
        color = "#f39c12"
        advice_class, advice_icon, advice_title, advice_text = "advice-dikkatli", "⚠️", "DİKKATLİ GİR", "Risklere karşı önlem alarak katılın."
    else:
        color = "#e74c3c"
        advice_class, advice_icon, advice_title, advice_text = "advice-girme", "❌", "GİRME", "Yüksek risk, katılım önerilmez."

    # ── Üst bölüm: Skor + Tavsiye + İstatistik ──
    c1, c2, c3 = st.columns([1, 1.2, 1])

    with c1:
        st.markdown(
            f'<div class="risk-circle" style="border-color:{color};">'
            f'<span class="score" style="color:{color};">{score}</span>'
            f'<span class="label">{level}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f'<div class="advice-card {advice_class}">'
            f'<div class="advice-icon">{advice_icon}</div>'
            f'<div class="advice-title">{advice_title}</div>'
            f'<div class="advice-text">{advice_text}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with c3:
        risk_data = result.get("risk_analysis", {})
        risks = risk_data.get("riskler", []) if isinstance(risk_data, dict) else []
        penalties = result.get("penalty_clauses", {})
        cezalar = penalties.get("cezalar", []) if isinstance(penalties, dict) else []
        docs = result.get("required_documents", {})
        zorunlu = docs.get("zorunlu_belgeler", []) if isinstance(docs, dict) else []

        st.markdown(
            f'<div class="metric-card">'
            f'<div style="font-size:0.85rem;">⚠️ <b>{len(risks)}</b> Risk</div>'
            f'<div style="font-size:0.85rem;">💰 <b>{len(cezalar)}</b> Ceza</div>'
            f'<div style="font-size:0.85rem;">📋 <b>{len(zorunlu)}</b> Zorunlu Belge</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 6 Tab ──
    tabs = st.tabs(["⚠️ Riskler", "📋 Belgeler", "💰 Cezalar", "💵 Mali", "⏱️ Süre", "📊 Özet"])

    with tabs[0]:
        _tab_risks(result)
    with tabs[1]:
        _tab_documents(result)
    with tabs[2]:
        _tab_penalties(result)
    with tabs[3]:
        _tab_financial(result)
    with tabs[4]:
        _tab_timeline(result)
    with tabs[5]:
        _tab_summary(result)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Alt butonlar ──
    b1, b2 = st.columns(2)
    with b1:
        try:
            from src.report.generator import ReportGenerator
            gen = ReportGenerator()
            file_name = st.session_state.get("uploaded_file_name", "rapor")
            pdf_bytes = gen.generate(result, file_name)
            st.download_button(
                "📥 PDF Rapor İndir", data=pdf_bytes,
                file_name=f"TenderAI_{file_name}.pdf",
                mime="application/pdf", use_container_width=True,
            )
        except Exception as e:
            st.warning(f"PDF oluşturulamadı: {e}")

    with b2:
        if st.button("🔄 Yeni Analiz", use_container_width=True, type="primary"):
            st.session_state["analysis_state"] = "upload"
            st.session_state.pop("analysis_result", None)
            st.session_state.pop("uploaded_file_bytes", None)
            st.rerun()


# ============================================================
# TAB İÇERİKLERİ / TAB CONTENTS
# ============================================================

def _safe_get(data: dict | str, key: str, default=None):
    """Güvenli dict erişimi."""
    if isinstance(data, dict):
        return data.get(key, default)
    return default


def _risk_badge(seviye: str) -> str:
    """Risk seviyesi badge HTML."""
    s = seviye.upper().strip()
    if s == "KRİTİK":
        return f'<span class="risk-badge risk-badge-critical">{seviye}</span>'
    elif s == "YÜKSEK":
        return f'<span class="risk-badge risk-badge-high">{seviye}</span>'
    elif s == "ORTA":
        return f'<span class="risk-badge risk-badge-medium">{seviye}</span>'
    else:
        return f'<span class="risk-badge risk-badge-low">{seviye}</span>'


def _tab_risks(result: dict) -> None:
    """Risk analizi tab."""
    data = _safe_get(result, "risk_analysis", {})
    ozet = _safe_get(data, "ozet", "")
    if ozet:
        st.info(str(ozet))

    riskler = _safe_get(data, "riskler", [])
    if not riskler:
        st.caption("Risk tespit edilmedi.")
        return

    for risk in riskler:
        if not isinstance(risk, dict):
            continue
        seviye = risk.get("seviye", "ORTA")
        border = "#e74c3c" if seviye in ("KRİTİK", "YÜKSEK") else "#f39c12" if seviye == "ORTA" else "#27ae60"

        st.markdown(
            f'<div class="risk-item-card" style="border-left-color:{border};">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<b>{risk.get("baslik", "—")}</b> {_risk_badge(seviye)}'
            f'</div>'
            f'<div style="font-size:0.85rem;color:#b0b8d1;margin:0.4rem 0;">{risk.get("aciklama", "")}</div>'
            f'<div style="font-size:0.8rem;">📌 {risk.get("madde_referans", "—")} · 💡 {risk.get("oneri", "—")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _tab_documents(result: dict) -> None:
    """Belgeler tab."""
    data = _safe_get(result, "required_documents", {})
    zorunlu = _safe_get(data, "zorunlu_belgeler", [])
    istege = _safe_get(data, "istege_bagli_belgeler", [])
    uyarilar = _safe_get(data, "onemli_uyarilar", [])

    if zorunlu:
        st.markdown("**Zorunlu Belgeler:**")
        for i, item in enumerate(zorunlu, 1):
            name = item.get("belge_adi", str(item)) if isinstance(item, dict) else str(item)
            desc = item.get("aciklama", "") if isinstance(item, dict) else ""
            st.markdown(f"{i}. **{name}** {f'— {desc}' if desc else ''}")

    if istege:
        with st.expander("📎 İsteğe Bağlı Belgeler"):
            for item in istege:
                name = item.get("belge_adi", str(item)) if isinstance(item, dict) else str(item)
                st.markdown(f"• {name}")

    if uyarilar:
        for u in uyarilar:
            st.warning(str(u))


def _tab_penalties(result: dict) -> None:
    """Cezalar tab."""
    data = _safe_get(result, "penalty_clauses", {})
    cezalar = _safe_get(data, "cezalar", [])

    if not cezalar:
        st.caption("Ceza maddesi tespit edilmedi.")
        return

    for ceza in cezalar:
        if not isinstance(ceza, dict):
            continue
        seviye = ceza.get("risk_seviyesi", "ORTA")
        border = "#e74c3c" if seviye in ("KRİTİK", "YÜKSEK") else "#f39c12"

        st.markdown(
            f'<div class="risk-item-card" style="border-left-color:{border};">'
            f'<div style="display:flex;justify-content:space-between;">'
            f'<b>{ceza.get("ceza_turu", "—")}</b> {_risk_badge(seviye)}'
            f'</div>'
            f'<div style="font-size:0.95rem;color:#667eea;font-weight:600;margin:0.3rem 0;">'
            f'{ceza.get("miktar_oran", "—")}</div>'
            f'<div style="font-size:0.8rem;color:#b0b8d1;">'
            f'{ceza.get("aciklama", "")} · 📌 {ceza.get("madde_referans", "")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _tab_financial(result: dict) -> None:
    """Mali özet tab."""
    data = _safe_get(result, "financial_summary", {})
    if not data:
        st.caption("Mali veri bulunamadı.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("💰 İhale Bedeli", _safe_get(data, "tahmini_ihale_bedeli", "—"))
    with c2:
        st.metric("🔒 Geçici Teminat", _safe_get(data, "gecici_teminat", "—"))
    with c3:
        st.metric("🔐 Kesin Teminat", _safe_get(data, "kesin_teminat", "—"))

    odeme = _safe_get(data, "odeme_kosullari", "")
    if odeme:
        st.info(f"💳 **Ödeme Koşulları:** {odeme}")

    fiyat = _safe_get(data, "fiyat_farki", "")
    if fiyat:
        st.info(f"📈 **Fiyat Farkı:** {fiyat}")

    mali_riskler = _safe_get(data, "mali_riskler", [])
    if mali_riskler:
        st.markdown("**⚠️ Mali Riskler:**")
        for r in mali_riskler:
            st.markdown(f"• {r}")


def _tab_timeline(result: dict) -> None:
    """Süre analizi tab."""
    data = _safe_get(result, "timeline_analysis", {})
    if not data:
        st.caption("Süre verisi bulunamadı.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.metric("🕐 Toplam Süre", _safe_get(data, "toplam_is_suresi", "—"))
    with c2:
        st.metric("🚀 Başlangıç", _safe_get(data, "ise_baslama_suresi", "—"))

    milestones = _safe_get(data, "milestones", [])
    if milestones:
        st.markdown("**📍 Milestones:**")
        for ms in milestones:
            if isinstance(ms, dict):
                st.markdown(f"• **{ms.get('asama', '—')}** → {ms.get('sure', '—')}")
            else:
                st.markdown(f"• {ms}")

    gecikme = _safe_get(data, "gecikme_riski_degerlendirmesi", "")
    if gecikme:
        st.warning(f"⚠️ {gecikme}")


def _tab_summary(result: dict) -> None:
    """Yönetici özeti tab."""
    data = _safe_get(result, "executive_summary", {})
    if isinstance(data, str):
        st.markdown(data)
        return

    ozet = _safe_get(data, "ozet", "")
    if ozet:
        st.markdown(str(ozet))

    guclu = _safe_get(data, "guclu_yanlar", [])
    if guclu:
        st.markdown("**💪 Güçlü Yanlar:**")
        for item in guclu:
            st.success(f"✅ {item}")

    zayif = _safe_get(data, "riskli_alanlar", _safe_get(data, "zayif_yanlar", []))
    if zayif:
        st.markdown("**⚠️ Riskli Alanlar:**")
        for item in zayif:
            st.error(f"❌ {item}")

    tavsiye = _safe_get(data, "tavsiye", "")
    if tavsiye:
        st.info(f"💡 **Tavsiye:** {tavsiye}")
