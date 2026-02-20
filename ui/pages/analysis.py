"""
TenderAI Yeni Analiz Sayfası / New Analysis Page.

PDF yükleme, analiz başlatma ve sonuçları görüntüleme.
PDF upload, analysis execution, and results display.
"""

import json
import time
import asyncio
import streamlit as st
import plotly.graph_objects as go

from src.pdf_parser.parser import IhalePDFParser
from src.database.db import (
    DatabaseManager,
    create_analysis,
    update_analysis_result,
    increment_analysis_count,
    check_analysis_limit,
)


def render_analysis_page() -> None:
    """Analiz sayfasını render et / Render analysis page."""

    st.markdown("## 🔍 Yeni İhale Analizi")
    st.caption("PDF şartname dosyanızı yükleyin ve yapay zeka ile analiz edin")

    st.divider()

    # Analiz sonucu session'da varsa göster / Show results if in session
    if st.session_state.get("analysis_result"):
        _render_results(st.session_state["analysis_result"])
        if st.button("🔄 Yeni Analiz Yap", use_container_width=True):
            st.session_state.pop("analysis_result", None)
            st.session_state.pop("uploaded_file_info", None)
            st.rerun()
        return

    # ADIM 1: PDF Yükleme / Step 1: PDF Upload
    _render_upload_step()


def _render_upload_step() -> None:
    """PDF yükleme adımı / PDF upload step."""

    st.markdown("### 📄 Adım 1: Şartname PDF'ini Yükleyin")

    uploaded_file = st.file_uploader(
        "PDF dosyası seçin",
        type=["pdf"],
        help="Maksimum dosya boyutu: 50 MB",
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)

        if file_size_mb > 50:
            st.error("❌ Dosya boyutu 50 MB'ı aşıyor. Lütfen daha küçük bir dosya yükleyin.")
            return

        # Dosya bilgileri / File info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Dosya Adı", uploaded_file.name)
        with col2:
            st.metric("📦 Boyut", f"{file_size_mb:.1f} MB")
        with col3:
            st.metric("📋 Tür", "PDF")

        # PDF önizleme / PDF preview
        with st.expander("📖 Metin Önizleme", expanded=False):
            try:
                parser = IhalePDFParser()
                doc = parser.parse(uploaded_file.getvalue())
                preview_text = doc.full_text[:2000] if doc.full_text else "Metin çıkarılamadı."
                st.text_area("İlk sayfalardan alıntı", preview_text, height=200, disabled=True)
                st.session_state["uploaded_file_info"] = {
                    "name": uploaded_file.name,
                    "size_mb": file_size_mb,
                    "pages": len(doc.pages),
                    "raw_bytes": uploaded_file.getvalue(),
                }
            except Exception as e:
                st.warning(f"Önizleme oluşturulamadı: {e}")

        st.divider()

        # ADIM 2: Analiz Başlat / Step 2: Start Analysis
        st.markdown("### 🚀 Adım 2: Analizi Başlatın")

        # Limit kontrolü / Limit check
        user_id = st.session_state.get("user_id")

        col_btn, col_info = st.columns([2, 1])
        with col_btn:
            start_analysis = st.button(
                "⚡ Analizi Başlat",
                use_container_width=True,
                type="primary",
            )
        with col_info:
            st.caption("Analiz yaklaşık 1-3 dakika sürer")

        if start_analysis:
            _run_analysis(uploaded_file)


def _run_analysis(uploaded_file) -> None:
    """Analiz pipeline'ını çalıştır / Run analysis pipeline."""

    user_id = st.session_state.get("user_id")
    api_key = _get_api_key()

    if not api_key:
        st.error(
            "⚠️ OpenAI API anahtarı bulunamadı. "
            "Lütfen `.env` dosyasına `OPENAI_API_KEY` ekleyin veya aşağıya girin."
        )
        api_key = st.text_input("OpenAI API Key", type="password")
        if not api_key:
            return

    progress_bar = st.progress(0, text="Hazırlanıyor...")
    status_container = st.empty()

    try:
        db_manager = DatabaseManager()
        db_manager.init_db()

        # ── Adım 1: PDF Parse ──
        progress_bar.progress(10, text="📄 PDF okunuyor...")
        status_container.info("PDF dosyası okunuyor ve metin çıkarılıyor...")

        parser = IhalePDFParser()
        parsed_doc = parser.parse(uploaded_file.getvalue())

        if not parsed_doc.full_text or not parsed_doc.full_text.strip():
            st.error("❌ PDF'den metin çıkarılamadı. Dosya taranmış (OCR gerekli) olabilir.")
            progress_bar.empty()
            status_container.empty()
            return

        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)

        # DB'ye analiz kaydı oluştur / Create analysis record in DB
        with db_manager.get_db() as db:
            analysis_record = create_analysis(
                db, user_id,
                file_name=uploaded_file.name,
                file_size_mb=round(file_size_mb, 2),
                total_pages=len(parsed_doc.pages),
            )
            analysis_id = analysis_record.id

        # ── Adım 2: AI Analiz ──
        progress_bar.progress(20, text="🔍 Metin analiz ediliyor...")
        status_container.info("Yapay zeka ile analiz başlatılıyor...")

        from src.ai_engine.analyzer import IhaleAnalizAI

        ai = IhaleAnalizAI(openai_api_key=api_key)

        # Her adımı simüle et / Simulate each step with progress
        steps = [
            (35, "⚠️ Risk analizi yapılıyor..."),
            (50, "📋 Belgeler kontrol ediliyor..."),
            (65, "💰 Ceza maddeleri taranıyor..."),
            (80, "💵 Mali analiz yapılıyor..."),
            (90, "⏱️ Süre analizi yapılıyor..."),
            (95, "📊 Yönetici özeti hazırlanıyor..."),
        ]

        # Async analiz çalıştır / Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Progress callback simülasyonu
        for pct, msg in steps[:2]:
            progress_bar.progress(pct, text=msg)
            status_container.info(msg)

        result = loop.run_until_complete(ai.analyze(parsed_doc))
        loop.close()

        progress_bar.progress(100, text="✅ Analiz tamamlandı!")
        status_container.success("Analiz başarıyla tamamlandı!")

        # ── DB'ye sonuçları kaydet / Save results to DB ──
        result_dict = {
            "risk_analysis": result.risk_analysis,
            "required_documents": result.required_documents,
            "penalty_clauses": result.penalty_clauses,
            "financial_summary": result.financial_summary,
            "timeline_analysis": result.timeline_analysis,
            "executive_summary": result.executive_summary,
        }

        exec_summary_text = ""
        if isinstance(result.executive_summary, dict):
            exec_summary_text = result.executive_summary.get("ozet", "")

        with db_manager.get_db() as db:
            update_analysis_result(
                db,
                analysis_id=analysis_id,
                risk_score=result.risk_score,
                risk_level=result.risk_level,
                result_json=result_dict,
                executive_summary=exec_summary_text,
                tokens_used=result.total_tokens_used,
                cost_usd=result.estimated_cost_usd,
                analysis_duration_seconds=result.analysis_time_seconds,
            )
            increment_analysis_count(db, user_id)

        # Session'a analiz sonucunu kaydet
        st.session_state["analysis_result"] = {
            "risk_score": result.risk_score,
            "risk_level": result.risk_level,
            "risk_analysis": result.risk_analysis,
            "required_documents": result.required_documents,
            "penalty_clauses": result.penalty_clauses,
            "financial_summary": result.financial_summary,
            "timeline_analysis": result.timeline_analysis,
            "executive_summary": result.executive_summary,
            "tokens_used": result.total_tokens_used,
            "cost_usd": result.estimated_cost_usd,
            "analysis_time": result.analysis_time_seconds,
            "file_name": uploaded_file.name,
        }
        st.session_state["analysis_count"] = st.session_state.get("analysis_count", 0) + 1

        time.sleep(1)
        st.rerun()

    except Exception as e:
        progress_bar.empty()
        status_container.empty()
        st.error(f"❌ Analiz sırasında hata: {e}")


# ============================================================
# Sonuç Render / Result Rendering
# ============================================================


def _render_results(result: dict) -> None:
    """Analiz sonuçlarını göster / Display analysis results."""

    file_name = result.get("file_name", "Dosya")
    risk_score = result.get("risk_score", 0)
    risk_level = result.get("risk_level", "—")

    st.markdown(f"### 📊 Analiz Sonuçları — {file_name}")
    st.divider()

    # ── Üst bölüm: Risk gauge + Tavsiye / Top: Risk gauge + Recommendation ──
    col_gauge, col_advice = st.columns([1, 1])

    with col_gauge:
        _render_risk_gauge(risk_score)

    with col_advice:
        _render_recommendation(risk_score, risk_level)

        # Özet metrikler / Summary metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("⏱️ Süre", f"{result.get('analysis_time', 0):.0f}s")
        with m2:
            st.metric("🔤 Token", f"{result.get('tokens_used', 0):,}")
        with m3:
            st.metric("💵 Maliyet", f"${result.get('cost_usd', 0):.4f}")

    st.divider()

    # ── 6 Tab / 6 Tabs ──
    tabs = st.tabs([
        "⚠️ Risk Analizi",
        "📋 Gerekli Belgeler",
        "💰 Ceza Maddeleri",
        "💵 Mali Özet",
        "⏱️ Süre Analizi",
        "📊 Yönetici Özeti",
    ])

    with tabs[0]:
        _render_risk_tab(result.get("risk_analysis", {}))

    with tabs[1]:
        _render_documents_tab(result.get("required_documents", {}))

    with tabs[2]:
        _render_penalties_tab(result.get("penalty_clauses", {}))

    with tabs[3]:
        _render_financial_tab(result.get("financial_summary", {}))

    with tabs[4]:
        _render_timeline_tab(result.get("timeline_analysis", {}))

    with tabs[5]:
        _render_executive_tab(result.get("executive_summary", {}))


def _render_risk_gauge(score: int) -> None:
    """Plotly risk gauge chart / Risk gauge with Plotly."""
    color = "#27ae60" if score <= 40 else "#f39c12" if score <= 70 else "#e74c3c"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Risk Skoru", "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color},
            "bgcolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0, 40], "color": "rgba(39,174,96,0.15)"},
                {"range": [40, 70], "color": "rgba(243,156,18,0.15)"},
                {"range": [70, 100], "color": "rgba(231,76,60,0.15)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.75,
                "value": score,
            },
        },
        number={"font": {"size": 40}},
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_recommendation(score: int, level: str) -> None:
    """Tavsiye kartı / Recommendation card."""
    if score <= 35:
        st.success("### ✅ GİR\nBu ihaleye katılım önerilir. Risk seviyesi kabul edilebilir düzeydedir.")
    elif score <= 65:
        st.warning("### ⚠️ DİKKATLİ GİR\nBu ihaleye dikkatli yaklaşılmalıdır. Belirtilen risklere karşı önlem alınmalıdır.")
    else:
        st.error("### ❌ GİRME\nBu ihale yüksek risk taşımaktadır. Katılım önerilmez veya ciddi önlemler gerektirir.")

    st.markdown(f"**Risk Seviyesi:** {level}")


def _render_risk_tab(data: dict) -> None:
    """Risk analizi tab'ı / Risk analysis tab."""
    if not data or data.get("error"):
        st.warning("Risk analizi verisi bulunamadı.")
        return

    # Özet
    ozet = data.get("ozet", "")
    if ozet:
        st.info(f"**Özet:** {ozet}")

    # Risk listesi
    riskler = data.get("riskler", [])
    if not riskler:
        st.info("Belirgin risk tespit edilmedi.")
        return

    for risk in riskler:
        if not isinstance(risk, dict):
            continue

        seviye = risk.get("seviye", "ORTA")
        css_class = (
            "risk-high" if seviye in ("YÜKSEK", "KRİTİK")
            else "risk-medium" if seviye == "ORTA"
            else "risk-low"
        )

        kategori = risk.get("kategori", "")
        baslik = risk.get("baslik", "")
        aciklama = risk.get("aciklama", "")
        referans = risk.get("madde_referans", "")
        oneri = risk.get("oneri", "")

        st.markdown(
            f"""<div class="{css_class}">
            <strong>{kategori} — {baslik}</strong> [{seviye}]<br>
            {aciklama}<br>
            <small>📌 {referans}</small><br>
            <em>💡 Öneri: {oneri}</em>
            </div>""",
            unsafe_allow_html=True,
        )


def _render_documents_tab(data: dict) -> None:
    """Gerekli belgeler tab'ı / Required documents tab."""
    if not data or data.get("error"):
        st.warning("Belge analizi verisi bulunamadı.")
        return

    # Zorunlu belgeler
    zorunlu = data.get("zorunlu_belgeler", [])
    if zorunlu:
        st.markdown("#### 📌 Zorunlu Belgeler")
        for item in zorunlu:
            if isinstance(item, dict):
                name = item.get("belge_adi", item.get("ad", str(item)))
                st.checkbox(name, value=False, disabled=True, key=f"doc_{name}")
            else:
                st.checkbox(str(item), value=False, disabled=True, key=f"doc_{item}")

    # İsteğe bağlı
    istege_bagli = data.get("istege_bagli_belgeler", [])
    if istege_bagli:
        st.markdown("#### 📎 İsteğe Bağlı Belgeler")
        for item in istege_bagli:
            if isinstance(item, dict):
                name = item.get("belge_adi", item.get("ad", str(item)))
                st.caption(f"• {name}")
            else:
                st.caption(f"• {item}")

    # Uyarılar
    uyarilar = data.get("onemli_uyarilar", [])
    if uyarilar:
        st.markdown("#### ⚠️ Önemli Uyarılar")
        for u in uyarilar:
            st.warning(str(u))


def _render_penalties_tab(data: dict) -> None:
    """Ceza maddeleri tab'ı / Penalty clauses tab."""
    if not data or data.get("error"):
        st.warning("Ceza analizi verisi bulunamadı.")
        return

    cezalar = data.get("cezalar", [])
    if not cezalar:
        st.info("Belirgin ceza maddesi tespit edilmedi.")
        return

    st.markdown(f"**Toplam {len(cezalar)} ceza maddesi tespit edildi**")

    for i, ceza in enumerate(cezalar, 1):
        if not isinstance(ceza, dict):
            continue

        with st.expander(f"Ceza {i}: {ceza.get('ceza_turu', 'Bilinmeyen')}", expanded=i <= 3):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Tür:** {ceza.get('ceza_turu', '—')}")
                st.markdown(f"**Miktar:** {ceza.get('miktar_oran', '—')}")
            with c2:
                st.markdown(f"**Risk:** {ceza.get('risk_seviyesi', '—')}")
                st.markdown(f"**Referans:** {ceza.get('madde_referans', '—')}")

            aciklama = ceza.get("aciklama", "")
            if aciklama:
                st.caption(aciklama)


def _render_financial_tab(data: dict) -> None:
    """Mali özet tab'ı / Financial summary tab."""
    if not data or data.get("error"):
        st.warning("Mali analiz verisi bulunamadı.")
        return

    # Ana metrikler
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("💰 Tahmini Bedel", data.get("tahmini_ihale_bedeli", "—"))
    with c2:
        st.metric("🔒 Geçici Teminat", data.get("gecici_teminat", "—"))
    with c3:
        st.metric("🔐 Kesin Teminat", data.get("kesin_teminat", "—"))

    # Ödeme koşulları
    odeme = data.get("odeme_kosullari", "")
    if odeme:
        st.markdown("#### 💳 Ödeme Koşulları")
        st.info(str(odeme))

    # Fiyat farkı
    fiyat = data.get("fiyat_farki", "")
    if fiyat:
        st.markdown("#### 📈 Fiyat Farkı")
        st.info(str(fiyat))

    # Mali riskler
    mali_riskler = data.get("mali_riskler", [])
    if mali_riskler:
        st.markdown("#### ⚠️ Mali Riskler")
        for risk in mali_riskler:
            st.warning(str(risk))


def _render_timeline_tab(data: dict) -> None:
    """Süre analizi tab'ı / Timeline analysis tab."""
    if not data or data.get("error"):
        st.warning("Süre analizi verisi bulunamadı.")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.metric("📅 Toplam İş Süresi", data.get("toplam_is_suresi", "—"))
    with c2:
        st.metric("📅 İşe Başlama", data.get("ise_baslama_suresi", "—"))

    # Milestones
    milestones = data.get("milestones", [])
    if milestones:
        st.markdown("#### 🏁 Önemli Tarihler / Milestones")
        for ms in milestones:
            if isinstance(ms, dict):
                st.markdown(f"• **{ms.get('asamme', ms.get('asama', '—'))}**: {ms.get('sure', '—')}")
            else:
                st.markdown(f"• {ms}")

    # Gecikme riski
    gecikme = data.get("gecikme_riski_degerlendirmesi", "")
    if gecikme:
        st.markdown("#### ⚠️ Gecikme Riski Değerlendirmesi")
        st.info(str(gecikme))


def _render_executive_tab(data: dict) -> None:
    """Yönetici özeti tab'ı / Executive summary tab."""
    if not data or data.get("error"):
        st.warning("Yönetici özeti verisi bulunamadı.")
        return

    ozet = data.get("ozet", data.get("genel_degerlendirme", ""))
    if ozet:
        st.markdown("#### 📋 Genel Değerlendirme")
        st.markdown(str(ozet))

    tavsiye = data.get("tavsiye", data.get("katilim_tavsiyesi", ""))
    if tavsiye:
        st.markdown("#### 💡 Katılım Tavsiyesi")
        st.info(str(tavsiye))

    guclu = data.get("guclu_yanlar", [])
    if guclu:
        st.markdown("#### ✅ Güçlü Yanlar")
        for item in guclu:
            st.markdown(f"• {item}")

    zayif = data.get("zayif_yanlar", data.get("riskli_alanlar", []))
    if zayif:
        st.markdown("#### ⚠️ Riskli Alanlar")
        for item in zayif:
            st.markdown(f"• {item}")


def _get_api_key() -> str | None:
    """OpenAI API anahtarını al / Get OpenAI API key."""
    import os
    # 1. Ortam değişkeni
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key

    # 2. .env dosyası
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("OPENAI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")

    return None


# Path import for _get_api_key
from pathlib import Path
