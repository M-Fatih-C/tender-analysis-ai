"""
TenderAI Plan & Ödeme Sayfası / Plan & Payment Page.

Abonelik planları ve ödeme yönetimi.
Subscription plans and payment management.
"""

import streamlit as st


def render_payment_page() -> None:
    """Plan ve ödeme sayfasını render et / Render payment page."""

    st.markdown("## 💳 Plan & Ödeme")
    st.caption("Abonelik planınızı yönetin ve yükseltin")

    st.divider()

    # Mevcut plan bilgisi / Current plan info
    current_plan = st.session_state.get("user_plan", "free")
    _render_current_plan(current_plan)

    st.divider()

    # Plan kartları / Plan cards
    st.markdown("### 📋 Planları Karşılaştır")

    col1, col2, col3 = st.columns(3)

    with col1:
        _render_plan_card(
            title="🆓 Ücretsiz",
            price="0 ₺",
            period="Süresiz",
            features=[
                "✅ 3 analiz / ay",
                "✅ Temel risk analizi",
                "✅ PDF metin çıkarma",
                "❌ Yönetici özeti",
                "❌ Öncelikli destek",
                "❌ API erişimi",
            ],
            is_current=current_plan == "free",
            plan_key="free",
        )

    with col2:
        _render_plan_card(
            title="⭐ Başlangıç",
            price="5.000 ₺",
            period="/ ay",
            features=[
                "✅ 20 analiz / ay",
                "✅ 6 analiz modülü",
                "✅ Yönetici özeti",
                "✅ PDF rapor indirme",
                "✅ E-posta desteği",
                "❌ API erişimi",
            ],
            is_current=current_plan == "starter",
            plan_key="starter",
            highlighted=True,
        )

    with col3:
        _render_plan_card(
            title="💎 Profesyonel",
            price="15.000 ₺",
            period="/ ay",
            features=[
                "✅ Sınırsız analiz",
                "✅ 6 analiz modülü",
                "✅ Yönetici özeti",
                "✅ PDF rapor indirme",
                "✅ Öncelikli destek",
                "✅ API erişimi",
            ],
            is_current=current_plan == "pro",
            plan_key="pro",
        )

    st.divider()

    # Karşılaştırma tablosu / Comparison table
    _render_comparison_table()

    st.divider()

    # Geliştirme notu / Development note
    st.info(
        "🚧 **Ödeme Sistemi Geliştirme Aşamasında**\n\n"
        "Ödeme işlemleri yakında aktif olacaktır. "
        "Şu anda ücretsiz plandaki tüm özelliklerden yararlanabilirsiniz.\n\n"
        "Sorularınız için: destek@tenderai.com.tr"
    )


def _render_current_plan(plan: str) -> None:
    """Mevcut plan bilgisi / Current plan info."""
    plan_names = {
        "free": "🆓 Ücretsiz",
        "starter": "⭐ Başlangıç",
        "pro": "💎 Profesyonel",
        "enterprise": "🏢 Kurumsal",
    }
    plan_limits = {
        "free": "3 analiz / ay",
        "starter": "20 analiz / ay",
        "pro": "Sınırsız",
        "enterprise": "Sınırsız",
    }

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 Mevcut Plan", plan_names.get(plan, plan))
    with col2:
        st.metric("📊 Analiz Limiti", plan_limits.get(plan, "3"))
    with col3:
        analysis_count = st.session_state.get("analysis_count", 0)
        st.metric("🔢 Bu Ay Kullanılan", analysis_count)


def _render_plan_card(
    title: str,
    price: str,
    period: str,
    features: list[str],
    is_current: bool,
    plan_key: str,
    highlighted: bool = False,
) -> None:
    """Plan kartı render et / Render plan card."""
    border_color = "#667eea" if highlighted else "rgba(128,128,128,0.2)"
    bg = "rgba(102,126,234,0.05)" if highlighted else "transparent"
    badge = ""

    if highlighted:
        badge = '<span style="background:#667eea; color:white; padding:2px 10px; border-radius:10px; font-size:0.75rem;">EN POPÜLER</span>'

    st.markdown(
        f"""
        <div style="
            border: 2px solid {border_color};
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            background: {bg};
            min-height: 400px;
        ">
            {badge}
            <h3 style="margin-top: 0.5rem;">{title}</h3>
            <h2 style="margin: 0.5rem 0 0;">{price}</h2>
            <p style="opacity: 0.6; margin-top: 0;">{period}</p>
            <hr style="opacity: 0.15;">
            <div style="text-align: left; padding: 0 0.5rem;">
                {"<br>".join(features)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if is_current:
        st.success("✅ Mevcut planınız")
    elif plan_key != "free":
        st.button(
            f"🔄 {title} Planına Geç",
            key=f"upgrade_{plan_key}",
            use_container_width=True,
            disabled=True,
        )


def _render_comparison_table() -> None:
    """Plan karşılaştırma tablosu / Plan comparison table."""
    st.markdown("### 📊 Detaylı Karşılaştırma")

    data = {
        "Özellik": [
            "Aylık Analiz",
            "Risk Analizi",
            "Belge Kontrolü",
            "Ceza Taraması",
            "Mali Özet",
            "Süre Analizi",
            "Yönetici Özeti",
            "PDF Rapor",
            "API Erişimi",
            "Öncelikli Destek",
        ],
        "🆓 Ücretsiz": [
            "3", "✅", "✅", "✅", "❌", "❌", "❌", "❌", "❌", "❌",
        ],
        "⭐ Başlangıç": [
            "20", "✅", "✅", "✅", "✅", "✅", "✅", "✅", "❌", "❌",
        ],
        "💎 Profesyonel": [
            "♾️", "✅", "✅", "✅", "✅", "✅", "✅", "✅", "✅", "✅",
        ],
    }

    st.table(data)
