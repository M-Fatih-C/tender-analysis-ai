"""
TenderAI Premium Analiz Sayfası v2.0.

3 aşama: upload → analyzing → results.
"""

import asyncio
import json
import time
import streamlit as st

from ui.components.header import render_header
from src.utils.helpers import risk_color_hex, safe_json_parse, format_file_size
from src.utils.demo_data import DEMO_ANALYSIS_RESULT


def render_analysis() -> None:
    """Analiz sayfası render."""
    render_header("🔍 Yeni Analiz", "Şartname PDF'inizi yükleyin ve AI ile analiz edin")

    state = st.session_state.get("analysis_state", "upload")
    if state == "upload":
        _stage_upload()
    elif state == "analyzing":
        _stage_analyzing()
    elif state == "batch_analyzing":
        _stage_batch_analyzing()
    elif state == "results":
        _stage_results()


# ==============================================================
# AŞAMA 1: UPLOAD
# ==============================================================

def _stage_upload() -> None:
    """Dosya yükleme aşaması — tekli veya çoklu."""
    plan = st.session_state.get("user_plan", "free")
    count = st.session_state.get("analysis_count", 0)
    limit_map = {"free": 3, "starter": 20, "pro": 9999}
    limit = limit_map.get(plan, 3)

    if limit < 9999 and count >= limit:
        st.warning("⚠️ Aylık analiz limitinize ulaştınız!")
        if st.button("💎 Planınızı Yükseltin", type="primary"):
            st.session_state["current_page"] = "payment"
            st.rerun()
        return

    # Mod seçimi
    mode_col1, mode_col2 = st.columns(2)
    with mode_col1:
        single = st.button("📄 Tekli Analiz", use_container_width=True,
                           type="primary" if not st.session_state.get("batch_mode") else "secondary")
        if single:
            st.session_state["batch_mode"] = False
            st.rerun()
    with mode_col2:
        batch = st.button("📚 Çoklu Analiz (Batch)", use_container_width=True,
                          type="primary" if st.session_state.get("batch_mode") else "secondary")
        if batch:
            st.session_state["batch_mode"] = True
            st.rerun()

    batch_mode = st.session_state.get("batch_mode", False)

    st.markdown(
        '<div style="text-align:center;padding:1rem 0;">'
        f'<div style="font-size:3rem;">{"📚" if batch_mode else "📤"}</div>'
        f'<p style="color:#8892b0;">{"Birden fazla şartname PDF\'i seçin" if batch_mode else "Şartname PDF\'inizi sürükleyip bırakın veya tıklayarak seçin"}</p>'
        '<p style="font-size:0.75rem;color:#555;">Maksimum 50MB • Sadece PDF</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    if batch_mode:
        _batch_upload(plan, count, limit)
    else:
        _single_upload()


def _single_upload() -> None:
    """Tekli dosya yükleme."""
    uploaded = st.file_uploader("PDF Yükle", type=["pdf"], label_visibility="collapsed", key="pdf_uploader")

    if uploaded:
        size_mb = len(uploaded.getvalue()) / (1024 * 1024)
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
                f'<div class="metric-card"><div class="metric-icon">📏</div>'
                f'<div class="metric-value" style="font-size:1rem;">{format_file_size(size_mb)}</div>'
                f'<div class="metric-label">Boyut</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                '<div class="metric-card"><div class="metric-icon">📋</div>'
                '<div class="metric-value" style="font-size:1rem;">PDF</div>'
                '<div class="metric-label">Format</div></div>',
                unsafe_allow_html=True,
            )

        with st.expander("📖 Ön İzleme"):
            try:
                from src.pdf_parser.parser import IhalePDFParser
                preview_parser = IhalePDFParser()
                preview_doc = preview_parser.parse(uploaded.getvalue())
                st.caption(f"📄 {preview_doc.metadata.total_pages} sayfa, {preview_doc.metadata.total_tables} tablo")
                st.text(preview_doc.full_text[:500] + "..." if len(preview_doc.full_text) > 500 else preview_doc.full_text)
            except Exception as e:
                st.info(f"Ön izleme yüklenemedi: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 AI Analizi Başlat", type="primary", use_container_width=True):
            st.session_state["uploaded_file_bytes"] = uploaded.getvalue()
            st.session_state["uploaded_file_name"] = uploaded.name
            st.session_state["uploaded_file_size"] = size_mb
            st.session_state["analysis_state"] = "analyzing"
            st.rerun()


def _batch_upload(plan: str, count: int, limit: int) -> None:
    """Çoklu dosya yükleme — batch analiz."""
    remaining = max(0, limit - count) if limit < 9999 else 999
    max_files = min(10, remaining)

    uploaded_files = st.file_uploader(
        "PDF Yükle", type=["pdf"], label_visibility="collapsed",
        key="batch_uploader", accept_multiple_files=True,
    )

    if uploaded_files:
        if len(uploaded_files) > max_files:
            st.warning(f"⚠️ Maksimum {max_files} dosya seçebilirsiniz. İlk {max_files} dosya alınacak.")
            uploaded_files = uploaded_files[:max_files]

        # Dosya kartları
        st.markdown(f"##### 📋 {len(uploaded_files)} Dosya Seçildi")
        for i, f in enumerate(uploaded_files):
            size_mb = len(f.getvalue()) / (1024 * 1024)
            st.markdown(
                f'<div class="analysis-card" style="border-left-color:#667eea;">'
                f'<div class="card-header">'
                f'<span class="card-title">📄 {f.name[:35]}</span>'
                f'<span style="font-size:0.75rem;color:#8892b0;">{format_file_size(size_mb)}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 Toplu AI Analizi Başlat", type="primary", use_container_width=True):
            # Store all files for batch processing
            batch_items = []
            for f in uploaded_files:
                batch_items.append({
                    "name": f.name,
                    "bytes": f.getvalue(),
                    "size_mb": len(f.getvalue()) / (1024 * 1024),
                })
            st.session_state["batch_items"] = batch_items
            st.session_state["analysis_state"] = "batch_analyzing"
            st.rerun()


# ==============================================================
# AŞAMA 2B: BATCH ANALYZING
# ==============================================================

def _stage_batch_analyzing() -> None:
    """Çoklu dosya analiz süreci."""
    batch_items = st.session_state.get("batch_items", [])

    if not batch_items:
        st.session_state["analysis_state"] = "upload"
        st.rerun()
        return

    total = len(batch_items)
    st.markdown(
        f'<div style="text-align:center;padding:1rem;">'
        f'<div style="font-size:3rem;">📚</div>'
        f'<h3>Toplu Analiz — {total} Dosya</h3>'
        f'<p style="color:#8892b0;">Her dosya sırayla analiz ediliyor</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    overall_progress = st.progress(0)
    results_container = st.container()
    results = []

    for idx, item in enumerate(batch_items):
        file_name = item["name"]
        file_bytes = item["bytes"]
        pct = (idx / total)
        overall_progress.progress(pct, text=f"({idx + 1}/{total}) {file_name[:30]}...")

        with results_container:
            status_placeholder = st.empty()
            status_placeholder.markdown(
                f'<div class="analysis-card" style="border-left-color:#f39c12;">'
                f'<div class="card-header">'
                f'<span class="card-title">🔄 {file_name[:35]}</span>'
                f'<span style="color:#f39c12;">Analiz ediliyor...</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        try:
            # Parse
            from src.pdf_parser.parser import IhalePDFParser
            parser = IhalePDFParser()
            doc = parser.parse(file_bytes)

            # AI Analysis — same fallback chain
            result = None
            model_used = "demo"
            demo = st.session_state.get("demo_mode", False)

            if not demo:
                from config.settings import settings
                try:
                    from src.ai_engine.analyzer import IhaleAnalizAI
                    ai = IhaleAnalizAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini")
                    result = asyncio.get_event_loop().run_until_complete(ai.analyze(doc))
                    if isinstance(result, dict):
                        model_used = "openai"
                except Exception:
                    pass

                if result is None:
                    try:
                        from src.ai_engine.gemini_analyzer import GeminiAnalizAI
                        gem = GeminiAnalizAI(gemini_api_key=settings.GEMINI_API_KEY)
                        result = gem.analyze(doc)
                        model_used = "gemini"
                    except Exception:
                        pass

            if result is None:
                result = dict(DEMO_ANALYSIS_RESULT)
                result["model_used"] = "demo"
                model_used = "demo"

            score = result.get("risk_score", 0)
            level = result.get("risk_level", "")
            color = risk_color_hex(score) if score else "#555"

            # Save to DB
            _save_batch_result(file_name, item["size_mb"], doc, result, model_used)

            results.append({"name": file_name, "score": score, "level": level, "status": "✅"})

            status_placeholder.markdown(
                f'<div class="analysis-card" style="border-left-color:{color};">'
                f'<div class="card-header">'
                f'<span class="card-title">✅ {file_name[:35]}</span>'
                f'<span class="card-score" style="color:{color};">{score}</span>'
                f'</div>'
                f'<div class="card-date">{level} • {model_used}</div></div>',
                unsafe_allow_html=True,
            )

        except Exception as e:
            results.append({"name": file_name, "score": None, "level": "HATA", "status": "❌"})
            status_placeholder.markdown(
                f'<div class="analysis-card" style="border-left-color:#e74c3c;">'
                f'<div class="card-header">'
                f'<span class="card-title">❌ {file_name[:35]}</span>'
                f'<span style="color:#e74c3c;">Hata</span>'
                f'</div>'
                f'<div class="card-date">{str(e)[:50]}</div></div>',
                unsafe_allow_html=True,
            )

    overall_progress.progress(1.0, text="Tamamlandı!")

    # Özet
    ok_count = sum(1 for r in results if r["status"] == "✅")
    st.markdown(
        f'<div class="advice-card advice-gir" style="margin-top:1rem;">'
        f'<div class="advice-icon">🏁</div>'
        f'<div class="advice-title">{ok_count}/{total} analiz tamamlandı</div>'
        f'<div class="advice-text">Sonuçları görmek için Dashboard veya Geçmiş Analizler sayfasına gidin</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📊 Dashboard'a Git", type="primary", use_container_width=True):
            st.session_state["analysis_state"] = "upload"
            st.session_state["current_page"] = "dashboard"
            st.rerun()
    with c2:
        if st.button("📁 Geçmiş Analizler", use_container_width=True):
            st.session_state["analysis_state"] = "upload"
            st.session_state["current_page"] = "history"
            st.rerun()
    with c3:
        if st.button("📚 Yeni Batch", use_container_width=True):
            st.session_state["analysis_state"] = "upload"
            st.session_state["batch_mode"] = True
            st.rerun()


def _save_batch_result(file_name, size_mb, doc, result, model_used):
    """Batch analiz sonucunu DB'ye kaydet."""
    try:
        user_id = st.session_state.get("user_id", 0)
        from src.database.db import DatabaseManager, create_analysis, update_analysis_result
        db_mgr = DatabaseManager()
        db_mgr.init_db()
        with db_mgr.get_db() as db:
            analysis = create_analysis(
                db, user_id=user_id, file_name=file_name,
                file_size_mb=size_mb, total_pages=doc.metadata.total_pages,
            )
            db.commit()

            es = result.get("executive_summary", {})
            summary = es.get("ozet", "") if isinstance(es, dict) else str(es)[:200]

            update_analysis_result(
                db, analysis.id,
                result_json=json.dumps(result, ensure_ascii=False, default=str),
                risk_score=result.get("risk_score"),
                risk_level=result.get("risk_level"),
                executive_summary=summary,
                model_used=model_used,
                tokens_used=result.get("tokens_used"),
                cost_usd=result.get("cost_usd"),
                analysis_duration_seconds=result.get("analysis_time"),
            )
            db.commit()

        # Count güncelle
        count = st.session_state.get("analysis_count", 0)
        st.session_state["analysis_count"] = count + 1
    except Exception:
        pass


# ==============================================================
# AŞAMA 2: ANALYZING
# ==============================================================

def _stage_analyzing() -> None:
    """Analiz süreci."""
    file_bytes = st.session_state.get("uploaded_file_bytes")
    file_name = st.session_state.get("uploaded_file_name", "dosya.pdf")

    if not file_bytes:
        st.session_state["analysis_state"] = "upload"
        st.rerun()
        return

    st.markdown(
        '<div style="text-align:center;padding:2rem;">'
        '<div style="font-size:3rem;">🤖</div>'
        '<h3>AI Analiz Ediliyor...</h3>'
        '<p style="color:#8892b0;">Lütfen sayfayı kapatmayın</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    progress = st.progress(0)
    status = st.empty()

    steps = [
        (5, "📄 PDF okunuyor..."),
        (15, "📝 Metin çıkarılıyor..."),
        (25, "🧩 Bölümler tespit ediliyor..."),
        (35, "🧠 Vektör veritabanı oluşturuluyor..."),
        (45, "⚠️ Risk analizi yapılıyor..."),
        (55, "📋 Belgeler kontrol ediliyor..."),
        (65, "💰 Ceza maddeleri taranıyor..."),
        (75, "💵 Mali analiz yapılıyor..."),
        (85, "⏱️ Süre analizi yapılıyor..."),
        (95, "📊 Rapor hazırlanıyor..."),
    ]

    demo = st.session_state.get("demo_mode", False)
    result = None
    model_used = "demo"

    try:
        # Parse
        from src.pdf_parser.parser import IhalePDFParser
        parser = IhalePDFParser()

        for pct, msg in steps[:3]:
            progress.progress(pct / 100)
            status.caption(msg)
            time.sleep(0.3)

        parsed_doc = parser.parse(file_bytes)

        for pct, msg in steps[3:4]:
            progress.progress(pct / 100)
            status.caption(msg)
            time.sleep(0.2)

        # AI analysis
        if demo:
            for pct, msg in steps[4:]:
                progress.progress(pct / 100)
                status.caption(msg)
                time.sleep(0.4)
            result = dict(DEMO_ANALYSIS_RESULT)
            model_used = "demo"
        else:
            # Try OpenAI → Gemini → Demo
            from config.settings import settings

            openai_ok = settings.OPENAI_API_KEY and settings.OPENAI_API_KEY not in ("", "sk-your-key-here")
            gemini_ok = settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 5

            if openai_ok:
                try:
                    for pct, msg in steps[4:6]:
                        progress.progress(pct / 100)
                        status.caption(msg)

                    from src.ai_engine.analyzer import IhaleAnalizAI
                    engine = IhaleAnalizAI(openai_api_key=settings.OPENAI_API_KEY)
                    result = asyncio.run(engine.analyze(parsed_doc))
                    model_used = "gpt-4o"

                    for pct, msg in steps[6:]:
                        progress.progress(pct / 100)
                        status.caption(msg)
                        time.sleep(0.2)

                except Exception as e:
                    st.warning(f"⚠️ OpenAI hatası: {e}. Gemini deneniyor...")
                    openai_ok = False

            if not openai_ok and gemini_ok and result is None:
                try:
                    for pct, msg in steps[4:6]:
                        progress.progress(pct / 100)
                        status.caption(msg)

                    from src.ai_engine.gemini_analyzer import GeminiAnalizAI
                    engine = GeminiAnalizAI(gemini_api_key=settings.GEMINI_API_KEY)
                    result = engine.analyze(parsed_doc)
                    model_used = "gemini"

                    for pct, msg in steps[6:]:
                        progress.progress(pct / 100)
                        status.caption(msg)
                        time.sleep(0.2)

                except Exception as e:
                    st.warning(f"⚠️ Gemini hatası: {e}. Demo moda geçiliyor...")

            if result is None:
                for pct, msg in steps[4:]:
                    progress.progress(pct / 100)
                    status.caption(msg)
                    time.sleep(0.3)
                result = dict(DEMO_ANALYSIS_RESULT)
                model_used = "demo"

        progress.progress(1.0)
        status.caption("✅ Analiz tamamlandı!")

        # Sonucu sakla
        if isinstance(result, dict):
            result["model_used"] = model_used
        st.session_state["analysis_result"] = result
        st.session_state["analysis_file_name"] = file_name
        st.session_state["analysis_state"] = "results"

        # DB kaydet
        try:
            risk_score = result.get("risk_score", 0)
            risk_level = result.get("risk_level", "")
            exec_summary = ""
            es = result.get("executive_summary", {})
            if isinstance(es, dict):
                exec_summary = es.get("ozet", "")
            elif isinstance(es, str):
                exec_summary = es

            from src.database.db import DatabaseManager, create_analysis, update_analysis_result
            db_mgr = DatabaseManager()
            db_mgr.init_db()
            with db_mgr.get_db() as db:
                analysis = create_analysis(
                    db, user_id=st.session_state.get("user_id", 0),
                    file_name=file_name,
                    file_size_mb=st.session_state.get("uploaded_file_size", 0),
                    total_pages=getattr(parsed_doc.metadata, "total_pages", 0) if hasattr(parsed_doc, "metadata") else 0,
                )
                update_analysis_result(
                    db, analysis_id=analysis.id,
                    risk_score=risk_score, risk_level=risk_level,
                    result_json=json.dumps(result, ensure_ascii=False, default=str),
                    executive_summary=exec_summary,
                )
                db.commit()
                st.session_state["current_analysis_id"] = analysis.id
                st.session_state["analysis_count"] = st.session_state.get("analysis_count", 0) + 1
        except Exception:
            pass

        # Parsed doc sakla (chatbot için)
        if hasattr(parsed_doc, "full_text"):
            st.session_state["parsed_doc_text"] = parsed_doc.full_text

        time.sleep(0.5)
        st.rerun()

    except Exception as e:
        st.error(f"❌ Analiz hatası: {e}")
        if st.button("🔄 Tekrar Dene"):
            st.session_state["analysis_state"] = "upload"
            st.rerun()


# ==============================================================
# AŞAMA 3: RESULTS
# ==============================================================

def _stage_results() -> None:
    """Analiz sonuçları."""
    result = st.session_state.get("analysis_result", {})
    file_name = st.session_state.get("analysis_file_name", "")
    if not result:
        st.session_state["analysis_state"] = "upload"
        st.rerun()
        return

    r = safe_json_parse(result) if isinstance(result, str) else result
    score = r.get("risk_score", 0)
    level = r.get("risk_level", "")
    model = r.get("model_used", "")

    if model:
        model_labels = {"gpt-4o": "OpenAI GPT-4o", "gemini": "Google Gemini", "demo": "Demo Modu"}
        st.caption(f"🤖 Model: **{model_labels.get(model, model)}**")

    # ── Üst 3 kolon ──
    top1, top2, top3 = st.columns([1, 1, 1])

    with top1:
        color = risk_color_hex(score)
        st.markdown(
            f'<div class="risk-circle" style="border-color:{color};">'
            f'<div class="score" style="color:{color};">{score}</div>'
            f'<div class="label" style="color:{color};">{level}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with top2:
        es = safe_json_parse(r.get("executive_summary", {})) if isinstance(r.get("executive_summary"), str) else r.get("executive_summary", {})
        tavsiye = es.get("tavsiye", "—") if isinstance(es, dict) else "—"
        neden = es.get("tavsiye_nedeni", "") if isinstance(es, dict) else ""
        if "GİRME" in tavsiye.upper():
            cls = "advice-girme"
            icon = "❌"
        elif "DİKKAT" in tavsiye.upper():
            cls = "advice-dikkatli"
            icon = "⚠️"
        else:
            cls = "advice-gir"
            icon = "✅"
        st.markdown(
            f'<div class="advice-card {cls}">'
            f'<div class="advice-icon">{icon}</div>'
            f'<div class="advice-title">{tavsiye}</div>'
            f'<div class="advice-text">{neden[:120]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with top3:
        risks = safe_json_parse(r.get("risk_analysis", {}))
        n_risks = len(risks.get("riskler", [])) if isinstance(risks, dict) else 0
        pens = safe_json_parse(r.get("penalty_clauses", {}))
        n_pen = len(pens.get("cezalar", [])) if isinstance(pens, dict) else 0
        docs = safe_json_parse(r.get("required_documents", {}))
        n_docs = len(docs.get("zorunlu_belgeler", [])) if isinstance(docs, dict) else 0

        for val, lbl, em in [(n_risks, "Tespit Edilen Risk", "⚠️"), (n_pen, "Ceza Maddesi", "💰"), (n_docs, "Zorunlu Belge", "📋")]:
            st.markdown(
                f'<div class="metric-card" style="padding:0.6rem;margin-bottom:6px;">'
                f'<span style="font-size:1rem;">{em}</span> '
                f'<span class="metric-value" style="font-size:1.2rem;">{val}</span> '
                f'<span class="metric-label" style="display:inline;">{lbl}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 6 Tab ──
    tabs = st.tabs(["⚠️ Risk", "📋 Belgeler", "💰 Cezalar", "💵 Mali", "⏱️ Süre", "📊 Özet"])

    with tabs[0]:
        _tab_risks(risks)
    with tabs[1]:
        _tab_documents(docs)
    with tabs[2]:
        _tab_penalties(pens)
    with tabs[3]:
        _tab_financial(safe_json_parse(r.get("financial_summary", {})))
    with tabs[4]:
        _tab_timeline(safe_json_parse(r.get("timeline_analysis", {})))
    with tabs[5]:
        _tab_summary(es)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # ── Aksiyon Butonları ──
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        try:
            from src.report.generator import ReportGenerator
            gen = ReportGenerator()
            pdf_bytes = gen.generate(r, file_name or "rapor")
            st.download_button("📥 PDF", data=pdf_bytes, file_name=f"TenderAI_{file_name}.pdf", mime="application/pdf")
        except Exception:
            st.button("📥 PDF", disabled=True)
    with b2:
        try:
            from src.report.excel_exporter import ExcelExporter
            exp = ExcelExporter()
            xlsx = exp.export(r, file_name or "rapor")
            st.download_button("📊 Excel", data=xlsx, file_name=f"TenderAI_{file_name}.xlsx",
                              mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception:
            st.button("📊 Excel", disabled=True)
    with b3:
        try:
            from src.report.docx_exporter import generate_docx_report
            docx_bytes = generate_docx_report(r, file_name or "rapor")
            st.download_button("📝 Word", data=docx_bytes, file_name=f"TenderAI_{file_name}.docx",
                              mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except Exception:
            st.button("📝 Word", disabled=True)
    with b4:
        if st.button("💬 Şartnameye Sor"):
            st.session_state["current_page"] = "chatbot"
            st.rerun()
    with b5:
        if st.button("🔄 Yeni Analiz"):
            st.session_state["analysis_state"] = "upload"
            st.rerun()


# ── Tab İçerikleri ──

def _tab_risks(data: dict) -> None:
    riskler = data.get("riskler", []) if isinstance(data, dict) else []
    if not riskler:
        st.info("Risk verisi bulunamadı.")
        return

    seviye_order = {"KRİTİK": 0, "YÜKSEK": 1, "ORTA": 2, "DÜŞÜK": 3}
    riskler = sorted(riskler, key=lambda x: seviye_order.get(x.get("seviye", "ORTA"), 2))

    for risk in riskler:
        if not isinstance(risk, dict):
            continue
        sev = risk.get("seviye", "ORTA")
        colors = {"KRİTİK": "#c0392b", "YÜKSEK": "#e74c3c", "ORTA": "#f39c12", "DÜŞÜK": "#27ae60"}
        badge_cls = {"KRİTİK": "risk-badge-critical", "YÜKSEK": "risk-badge-high", "ORTA": "risk-badge-medium", "DÜŞÜK": "risk-badge-low"}
        c = colors.get(sev, "#f39c12")
        b = badge_cls.get(sev, "risk-badge-medium")
        st.markdown(
            f'<div class="risk-item-card" style="border-left-color:{c};">'
            f'<div class="card-header"><span class="card-title">{risk.get("baslik", "")}</span>'
            f'<span class="risk-badge {b}">{sev}</span></div>'
            f'<p style="color:#b0b8d1;font-size:0.85rem;margin:8px 0;">{risk.get("aciklama", "")}</p>'
            f'<div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#8892b0;">'
            f'<span>📌 {risk.get("madde_referans", "")}</span>'
            f'<span>💡 {risk.get("oneri", "")}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _tab_documents(data: dict) -> None:
    zorunlu = data.get("zorunlu_belgeler", []) if isinstance(data, dict) else []
    if not zorunlu:
        st.info("Belge verisi bulunamadı.")
        return

    html = '<table class="styled-table"><tr><th>Belge</th><th>Kategori</th><th>Nereden</th><th>Süre</th></tr>'
    for d in zorunlu:
        if not isinstance(d, dict):
            continue
        html += (
            f'<tr><td><strong>{d.get("belge_adi", "")}</strong><br>'
            f'<span style="font-size:0.75rem;color:#8892b0;">{d.get("aciklama", "")}</span></td>'
            f'<td>{d.get("kategori", "")}</td>'
            f'<td>{d.get("nereden_alinir", "")}</td>'
            f'<td>{d.get("tahmini_sure", "")}</td></tr>'
        )
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)

    warnings = data.get("onemli_uyarilar", [])
    if warnings:
        for w in warnings:
            st.warning(f"⚠️ {w}")


def _tab_penalties(data: dict) -> None:
    cezalar = data.get("cezalar", []) if isinstance(data, dict) else []
    if not cezalar:
        st.info("Ceza maddesi bulunamadı.")
        return

    for c in cezalar:
        if not isinstance(c, dict):
            continue
        sev = c.get("risk_seviyesi", "ORTA")
        colors = {"KRİTİK": "#c0392b", "YÜKSEK": "#e74c3c", "ORTA": "#f39c12", "DÜŞÜK": "#27ae60"}
        border = colors.get(sev, "#f39c12")
        st.markdown(
            f'<div class="risk-item-card" style="border-left-color:{border};">'
            f'<div class="card-header">'
            f'<span class="card-title">📌 Madde {c.get("madde_no", "")}</span>'
            f'<span class="risk-badge risk-badge-{"critical" if sev=="KRİTİK" else "high" if sev=="YÜKSEK" else "medium"}">{sev}</span>'
            f'</div>'
            f'<div style="font-size:1.1rem;font-weight:700;color:#f093fb;margin:8px 0;">{c.get("miktar_oran", "")}</div>'
            f'<p style="color:#b0b8d1;font-size:0.85rem;">{c.get("aciklama", "")}</p>'
            f'<p style="font-size:0.8rem;color:#667eea;">📖 Senaryo: {c.get("senaryo", "")}</p>'
            f'<p style="font-size:0.75rem;color:#8892b0;">💡 {c.get("oneri", "")}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _tab_financial(data: dict) -> None:
    if not isinstance(data, dict) or not data:
        st.info("Mali veri bulunamadı.")
        return

    c1, c2, c3, c4 = st.columns(4)
    items = [
        (c1, "💰", "Tahmini Bedel", data.get("tahmini_ihale_bedeli", "—")),
        (c2, "🔒", "Geçici Teminat", data.get("gecici_teminat", "—")),
        (c3, "🏦", "Kesin Teminat", data.get("kesin_teminat", "—")),
        (c4, "💳", "Ödeme", data.get("odeme_kosullari", "—")),
    ]
    for col, icon, label, val in items:
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-icon">{icon}</div>'
                f'<div class="metric-value" style="font-size:0.9rem;">{str(val)[:40]}</div>'
                f'<div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    col_r, col_o = st.columns(2)
    with col_r:
        st.markdown("**🔴 Mali Riskler**")
        for item in data.get("mali_riskler", []):
            st.markdown(f"- ❌ {item}")
    with col_o:
        st.markdown("**🟢 Mali Fırsatlar**")
        for item in data.get("mali_firsatlar", []):
            st.markdown(f"- ✅ {item}")

    recs = data.get("oneriler", [])
    if recs:
        st.markdown("**💡 Öneriler**")
        for rec in recs:
            st.info(f"💡 {rec}")


def _tab_timeline(data: dict) -> None:
    if not isinstance(data, dict) or not data:
        st.info("Süre verisi bulunamadı.")
        return

    st.markdown(
        f'<div class="metric-card" style="text-align:center;margin-bottom:1rem;">'
        f'<div class="metric-icon">⏱️</div>'
        f'<div class="metric-value">{data.get("toplam_is_suresi", "—")}</div>'
        f'<div class="metric-label">Toplam İş Süresi</div></div>',
        unsafe_allow_html=True,
    )

    milestones = data.get("milestones", [])
    if milestones:
        st.markdown("##### 📍 Aşamalar")
        for ms in milestones:
            if isinstance(ms, dict):
                st.markdown(f"- **{ms.get('asama', '')}** — {ms.get('sure', '')} — {ms.get('tamamlanma', '')}")

    recs = data.get("oneriler", [])
    if recs:
        st.markdown("##### 💡 Öneriler")
        for rec in recs:
            st.info(f"💡 {rec}")


def _tab_summary(data) -> None:
    if isinstance(data, str):
        data = safe_json_parse(data)
    if not isinstance(data, dict):
        st.info("Özet bulunamadı.")
        return

    ozet = data.get("ozet", data.get("sonuc_paragraf", ""))
    if ozet:
        st.markdown(f"> {ozet}")

    kritik = data.get("en_kritik_3_bulgu", [])
    if kritik:
        st.markdown("##### 🔥 En Kritik Bulgular")
        for i, k in enumerate(kritik, 1):
            st.markdown(f"**{i}.** {k}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### ✅ Güçlü Yanlar")
        for g in data.get("guclu_yanlar", data.get("avantajlar", [])):
            st.markdown(f"- ✅ {g}")

    with col2:
        st.markdown("##### ❌ Riskli Alanlar")
        for r in data.get("riskli_alanlar", data.get("dezavantajlar", [])):
            st.markdown(f"- ❌ {r}")
