"""
TenderAI Chatbot Sayfası v2.0.
"""

import streamlit as st
from ui.components.header import render_header
from src.utils.helpers import safe_json_parse


def render_chatbot() -> None:
    """Şartnameye soru-cevap chatbot."""
    render_header("💬 Şartnameye Sor", "Analiz edilmiş şartnamenize soru sorun")

    user_id = st.session_state.get("user_id", 0)

    # Sol: analiz seç, Sağ: chat
    col_sel, col_chat = st.columns([1, 3])

    with col_sel:
        st.markdown("##### 📄 Şartname Seç")
        analyses = _get_analyses(user_id)
        if not analyses:
            st.info("Önce bir analiz yapın.")
            if st.button("🔍 Yeni Analiz", use_container_width=True):
                st.session_state["current_page"] = "analysis"
                st.rerun()
            return

        options = {a["id"]: f"{a['file_name'][:25]} (Risk: {a['risk_score'] or '—'})" for a in analyses}
        selected_id = st.radio("Analiz", list(options.keys()), format_func=lambda x: options[x], label_visibility="collapsed")

        # Session'dan önceki seçim
        prev = st.session_state.get("chatbot_analysis_id")
        if prev != selected_id:
            st.session_state["chatbot_analysis_id"] = selected_id
            st.session_state["chat_messages"] = []
            st.session_state.pop("chatbot_ready", None)

    with col_chat:
        if not selected_id:
            return

        sel_analysis = next((a for a in analyses if a["id"] == selected_id), None)
        if sel_analysis:
            st.caption(f"📄 **{sel_analysis['file_name']}** • Risk: {sel_analysis['risk_score'] or '—'}")

        # Init chatbot
        if "chatbot_ready" not in st.session_state:
            _init_chatbot(selected_id)

        # Önerilen sorular
        from src.ai_engine.chatbot import SUGGESTED_QUESTIONS
        st.markdown("##### 💡 Önerilen Sorular")
        chips_html = ""
        for q in SUGGESTED_QUESTIONS[:6]:
            chips_html += f'<span class="chip">{q}</span> '
        st.markdown(f'<div style="margin-bottom:1rem;">{chips_html}</div>', unsafe_allow_html=True)

        # Mesaj geçmişi
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = []

        for msg in st.session_state["chat_messages"]:
            role = msg.get("role", "user")
            text = msg.get("message", "")
            if role == "user":
                st.markdown(f'<div class="chat-msg chat-user">{text}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-msg chat-ai">🤖 {text}</div>', unsafe_allow_html=True)

        # Input
        question = st.chat_input("Sorunuzu yazın...")
        if question:
            st.session_state["chat_messages"].append({"role": "user", "message": question})

            bot = st.session_state.get("chatbot_instance")
            if bot:
                with st.spinner("Yanıt hazırlanıyor..."):
                    answer = bot.ask(question, st.session_state["chat_messages"])
            else:
                from src.utils.demo_data import DEMO_CHAT_RESPONSES
                q_lower = question.lower()
                answer = DEMO_CHAT_RESPONSES.get("default", "")
                for key, resp in DEMO_CHAT_RESPONSES.items():
                    if key in q_lower:
                        answer = resp
                        break

            st.session_state["chat_messages"].append({"role": "assistant", "message": answer})

            # DB kaydet
            try:
                from src.database.db import DatabaseManager, save_chat_message
                db_mgr = DatabaseManager()
                db_mgr.init_db()
                with db_mgr.get_db() as db:
                    save_chat_message(db, selected_id, user_id, "user", question)
                    save_chat_message(db, selected_id, user_id, "assistant", answer)
                    db.commit()
            except Exception:
                pass

            st.rerun()


def _get_analyses(user_id: int) -> list:
    """Completed analyses as dicts."""
    try:
        from src.database.db import DatabaseManager, get_user_analyses
        db_mgr = DatabaseManager()
        db_mgr.init_db()
        with db_mgr.get_db() as db:
            raw = get_user_analyses(db, user_id, limit=20)
            return [
                {"id": a.id, "file_name": a.file_name, "risk_score": a.risk_score,
                 "result_json": a.result_json, "status": a.status}
                for a in raw if a.status == "completed"
            ]
    except Exception:
        return []


def _init_chatbot(analysis_id: int) -> None:
    """Chatbot init — load context."""
    try:
        from config.settings import settings
        from src.ai_engine.chatbot import IhaleChatbot

        bot = IhaleChatbot(
            gemini_api_key=settings.GEMINI_API_KEY,
            openai_api_key=settings.OPENAI_API_KEY,
        )

        context = st.session_state.get("parsed_doc_text", "")
        if not context:
            # Fallback: result_json'dan özet çıkar
            analyses = _get_analyses(st.session_state.get("user_id", 0))
            for a in analyses:
                if a["id"] == analysis_id and a.get("result_json"):
                    r = safe_json_parse(a["result_json"])
                    parts = []
                    es = r.get("executive_summary", {})
                    if isinstance(es, dict):
                        parts.append(es.get("ozet", ""))
                    context = " ".join(str(v) for v in r.values() if isinstance(v, str))[:15000]
                    break

        if context:
            bot.set_context(context)

        st.session_state["chatbot_instance"] = bot
        st.session_state["chatbot_ready"] = True
    except Exception:
        st.session_state["chatbot_ready"] = True
