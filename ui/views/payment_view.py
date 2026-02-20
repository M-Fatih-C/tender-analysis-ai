"""
TenderAI Plan & Ödeme Sayfası / Payment Page.
"""

import streamlit as st
from ui.components.header import render_header
from src.payment.payment import PLANS


def render_payment() -> None:
    """Plan ve ödeme sayfasını render et / Render payment page."""
    render_header("Plan & Ödeme", "Abonelik planınızı yönetin")

    current_plan = st.session_state.get("user_plan", "free")

    # Mevcut plan
    plan_info = PLANS.get(current_plan, PLANS["free"])
    plan_names = {"free": "🆓 Ücretsiz", "starter": "⭐ Başlangıç", "pro": "💎 Profesyonel"}

    st.markdown(
        f'<div class="metric-card" style="border:2px solid #667eea;">'
        f'<div class="metric-label">MEVCUT PLAN</div>'
        f'<div class="metric-value" style="color:#667eea;">{plan_names.get(current_plan, current_plan)}</div>'
        f'<div style="font-size:0.85rem;color:#8892b0;margin-top:4px;">'
        f'{plan_info["max_analysis_per_month"] if plan_info["max_analysis_per_month"] < 9999 else "Sınırsız"} analiz/ay</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📋 Planları Karşılaştır")

    # Plan kartları
    cols = st.columns(3)
    plan_keys = ["free", "starter", "pro"]
    is_popular = [False, True, False]

    for col, key, popular in zip(cols, plan_keys, is_popular):
        with col:
            plan = PLANS[key]
            is_current = key == current_plan
            hl_class = "highlighted" if popular else ""
            badge = '<div class="plan-badge">EN POPÜLER</div>' if popular else ""
            current_tag = '<div style="color:#667eea;font-weight:600;margin-top:0.5rem;">✅ Mevcut Plan</div>' if is_current else ""

            price = f'{plan["price_monthly_try"]:,.0f} ₺' if plan["price_monthly_try"] > 0 else "0 ₺"
            limit = "Sınırsız" if plan["max_analysis_per_month"] >= 9999 else str(plan["max_analysis_per_month"])

            features_html = ""
            for f in plan["features"]:
                features_html += f'<li>✅ {f}</li>'

            st.markdown(
                f'<div class="plan-card {hl_class}">'
                f'{badge}'
                f'<div class="plan-name">{plan_names.get(key, key)}</div>'
                f'<div class="plan-price">{price}</div>'
                f'<div class="plan-period">/ ay · {limit} analiz</div>'
                f'<hr style="opacity:0.1;">'
                f'<ul class="plan-features">{features_html}</ul>'
                f'{current_tag}'
                f'</div>',
                unsafe_allow_html=True,
            )

            if not is_current and key != "free":
                plan_order = {"free": 0, "starter": 1, "pro": 2}
                can_upgrade = plan_order.get(key, 0) > plan_order.get(current_plan, 0)

                if can_upgrade:
                    if st.button(f"🔄 {plan['name']}'a Geç", key=f"upgrade_{key}", use_container_width=True):
                        _upgrade(key)
                else:
                    st.button(f"{plan['name']}", key=f"btn_{key}", disabled=True, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "🚧 **Ödeme sistemi geliştirme aşamasında.**\n\n"
        "Plan değişiklikleri şu an demo olarak çalışmaktadır. "
        "Gerçek ödeme entegrasyonu (iyzico/PayTR) yakında aktif olacaktır."
    )


def _upgrade(new_plan: str) -> None:
    """Plan yükselt (demo)."""
    try:
        user_id = st.session_state.get("user_id", 0)
        if not user_id:
            st.warning("Giriş yapmanız gerekiyor.")
            return

        from src.database.db import DatabaseManager
        from src.payment.payment import PaymentManager

        db_mgr = DatabaseManager()
        db_mgr.init_db()
        with db_mgr.get_db() as db:
            from src.database.db import get_user_by_id
            user = get_user_by_id(db, user_id)
            if not user:
                st.error("Kullanıcı bulunamadı.")
                return

            pm = PaymentManager(db)
            ok, msg = pm.upgrade_plan(user, new_plan)
            if ok:
                st.session_state["user_plan"] = new_plan
                st.session_state["analysis_count"] = 0
                st.success(f"✅ {msg}")
                st.rerun()
            else:
                st.error(msg)
    except Exception as e:
        st.error(f"Plan güncelleme hatası: {e}")
