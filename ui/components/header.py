"""
TenderAI Header Bileşeni / Header Component v2.0.
"""

import streamlit as st
from datetime import datetime
from src.utils.helpers import format_date_turkish


def render_header(title: str, subtitle: str = "",
                  show_date: bool = True, show_notifications: bool = False) -> None:
    """Premium header render et."""
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(
            f"<div style='animation:fadeIn 0.5s ease;'>"
            f"<h2 style='margin:0;font-weight:800;'>{title}</h2>"
            f"<p style='color:#8892b0;margin:0;font-size:0.9rem;'>{subtitle}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c2:
        parts = []
        if show_date:
            parts.append(f"📅 {format_date_turkish(datetime.now())}")
        if show_notifications:
            try:
                from src.database.db import DatabaseManager, get_unread_notification_count
                user_id = st.session_state.get("user_id", 0)
                if user_id:
                    db_mgr = DatabaseManager()
                    db_mgr.init_db()
                    with db_mgr.get_db() as db:
                        count = get_unread_notification_count(db, user_id)
                    if count > 0:
                        parts.append(f"🔔<span class='notif-badge'>{count}</span>")
            except Exception:
                pass
        if parts:
            st.markdown(
                f"<div style='text-align:right;padding-top:0.5rem;font-size:0.8rem;color:#8892b0;'>"
                f"{'  •  '.join(parts)}</div>",
                unsafe_allow_html=True,
            )
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
