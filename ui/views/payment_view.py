"""
TenderAI Premium Plan & Ödeme Sayfası v2.0.
"""

import streamlit as st
from ui.components.header import render_header


_PLANS = {
    "free": {
        "icon": "🆓", "name": "Ücretsiz", "price": "0 TL/ay",
        "features": [
            ("3 analiz/ay", True), ("Temel risk analizi", True), ("PDF rapor", True),
            ("Chatbot (5 soru/gün)", True), ("Firma profili", False), ("Karşılaştırma", False),
            ("Excel export", False), ("Öncelikli destek", False),
        ],
    },
    "starter": {
        "icon": "⭐", "name": "Başlangıç", "price": "5.000 TL/ay",
        "features": [
            ("20 analiz/ay", True), ("Tüm analizler", True), ("PDF + Excel rapor", True),
            ("Chatbot (sınırsız)", True), ("Firma profili", True), ("Karşılaştırma (3/ay)", True),
            ("Email destek", True), ("Öncelikli destek", False),
        ],
    },
    "pro": {
        "icon": "💎", "name": "Profesyonel", "price": "15.000 TL/ay",
        "features": [
            ("Sınırsız analiz", True), ("Tüm özellikler", True), ("API erişimi", True),
            ("Sınırsız karşılaştırma", True), ("7/24 öncelikli destek", True),
            ("Özel raporlama", True), ("Dedicated account manager", True),
            ("Tüm özellikler", True),
        ],
        "recommended": True,
    },
}


def render_payment() -> None:
    """Plan & Ödeme sayfası."""
    render_header("💳 Plan & Ödeme", "Planınızı yönetin ve yükseltin")

    current_plan = st.session_state.get("user_plan", "free")
    count = st.session_state.get("analysis_count", 0)
    limit_map = {"free": 3, "starter": 20, "pro": 9999}
    limit = limit_map.get(current_plan, 3)
    remaining = max(0, limit - count) if limit < 9999 else 9999

    plan_info = _PLANS.get(current_plan, _PLANS["free"])

    # Mevcut plan kartı
    st.markdown(
        f'<div class="advice-card advice-gir" style="margin-bottom:1.5rem;">'
        f'<div style="font-size:1.5rem;">{plan_info["icon"]} Mevcut Planınız: <strong>{plan_info["name"]}</strong></div>'
        f'<div class="advice-text">Kalan hak: {"♾️ Sınırsız" if remaining >= 9999 else remaining} • '
        f'Kullanılan: {count}</div></div>',
        unsafe_allow_html=True,
    )

    # 3 plan kartı
    cols = st.columns(3)
    for i, (key, plan) in enumerate(_PLANS.items()):
        with cols[i]:
            is_current = key == current_plan
            is_rec = plan.get("recommended", False)

            border_style = "border: 2px solid #667eea;" if is_current else "border: 2px solid rgba(255,255,255,0.06);" if not is_rec else "border: 2px solid #764ba2;"

            badge = ""
            if is_current:
                badge = '<span style="background:#667eea;color:#fff;padding:2px 10px;border-radius:10px;font-size:0.65rem;font-weight:700;">MEVCUT</span>'
            elif is_rec:
                badge = '<span style="background:#764ba2;color:#fff;padding:2px 10px;border-radius:10px;font-size:0.65rem;font-weight:700;">ÖNERİLEN</span>'

            features_html = ""
            for feat, available in plan["features"]:
                icon = "✅" if available else "❌"
                color = "#c4c9d8" if available else "#555"
                features_html += f'<div style="font-size:0.8rem;color:{color};margin:3px 0;">{icon} {feat}</div>'

            st.markdown(
                f'<div style="{border_style}border-radius:14px;padding:1.5rem;text-align:center;'
                f'background:rgba(255,255,255,0.02);height:100%;">'
                f'<div style="font-size:2rem;">{plan["icon"]}</div>'
                f'{badge}'
                f'<h4 style="margin:8px 0 4px 0;">{plan["name"]}</h4>'
                f'<div style="font-size:1.5rem;font-weight:800;color:#667eea;margin-bottom:1rem;">{plan["price"]}</div>'
                f'{features_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

            if is_current:
                st.button(f"Mevcut Plan", key=f"plan_{key}", disabled=True, use_container_width=True)
            else:
                if st.button(f"{'⬆️ Yükselt' if key != 'free' else 'Seç'}", key=f"plan_{key}", use_container_width=True):
                    _upgrade(key)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.caption("💡 Ödeme entegrasyonu yakında aktif olacaktır. Şu an plan değişiklikleri demo amaçlıdır.")


def _upgrade(new_plan: str) -> None:
    """Plan yükselt (demo)."""
    try:
        user_id = st.session_state.get("user_id", 0)
        plan_limits = {"free": 3, "starter": 20, "pro": 9999}

        from src.database.db import DatabaseManager
        db_mgr = DatabaseManager()
        db_mgr.init_db()
        with db_mgr.get_db() as db:
            from src.database.models import User
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.plan = new_plan
                user.max_analysis_per_month = plan_limits.get(new_plan, 3)
                user.analysis_count = 0
                db.commit()

            # Bildirim
            try:
                from src.utils.notifications import NotificationManager
                nm = NotificationManager(db)
                nm.notify_plan_upgraded(user_id, new_plan)
                db.commit()
            except Exception:
                pass

        st.session_state["user_plan"] = new_plan
        st.session_state["analysis_count"] = 0
        st.success(f"✅ {_PLANS[new_plan]['name']} planına geçildi!")
        st.balloons()
        st.rerun()
    except Exception as e:
        st.error(f"❌ Hata: {e}")
