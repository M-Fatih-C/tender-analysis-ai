"""
TenderAI Onboarding Bileşeni v2.0.
"""

import streamlit as st


def render_onboarding() -> None:
    """İlk kez giriş yapan kullanıcıya hoşgeldin akışı."""
    step = st.session_state.get("onboarding_step", 1)

    # İlerleme göstergesi
    cols = st.columns(5)
    with cols[1]:
        cls1 = "step-active" if step == 1 else "step-done" if step > 1 else "step-inactive"
        st.markdown(f'<div style="text-align:center;"><span class="onboarding-step {cls1}">1</span></div>', unsafe_allow_html=True)
    with cols[2]:
        cls2 = "step-active" if step == 2 else "step-done" if step > 2 else "step-inactive"
        st.markdown(f'<div style="text-align:center;"><span class="onboarding-step {cls2}">2</span></div>', unsafe_allow_html=True)
    with cols[3]:
        cls3 = "step-active" if step == 3 else "step-inactive"
        st.markdown(f'<div style="text-align:center;"><span class="onboarding-step {cls3}">3</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if step == 1:
        _step_welcome()
    elif step == 2:
        _step_profile()
    elif step == 3:
        _step_first_analysis()


def _step_welcome() -> None:
    """Adım 1: Hoşgeldin."""
    st.markdown(
        '<div class="onboarding-card">'
        '<div style="font-size:3rem;">🎉</div>'
        '<h2>TenderAI\'a Hoş Geldiniz!</h2>'
        '<p style="color:#8892b0;">Yapay zeka ile ihale şartnamelerinizi analiz edin</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="action-card"><div class="action-icon">📤</div>'
            '<div class="action-title">PDF Yükle</div>'
            '<div class="action-desc">Şartname dosyanızı yükleyin</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="action-card"><div class="action-icon">🤖</div>'
            '<div class="action-title">AI Analiz</div>'
            '<div class="action-desc">Yapay zeka risk analizi yapsın</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="action-card"><div class="action-icon">📊</div>'
            '<div class="action-title">Karar Ver</div>'
            '<div class="action-desc">Detaylı rapor ile karar verin</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    c_next, c_skip = st.columns([3, 1])
    with c_next:
        if st.button("Devam →", type="primary", use_container_width=True):
            st.session_state["onboarding_step"] = 2
            st.rerun()
    with c_skip:
        if st.button("Atla", use_container_width=True):
            st.session_state["onboarding_completed"] = True
            st.rerun()


def _step_profile() -> None:
    """Adım 2: Firma profili."""
    st.markdown(
        '<div class="onboarding-card">'
        '<div style="font-size:3rem;">🏢</div>'
        '<h3>Firma Profilinizi Oluşturun</h3>'
        '<p style="color:#8892b0;">Profiliniz sayesinde her ihale için uygunluk skoru hesaplayabiliriz</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏢 Şimdi Oluştur", type="primary", use_container_width=True):
            st.session_state["onboarding_completed"] = True
            st.session_state["current_page"] = "company_profile"
            st.rerun()
    with c2:
        if st.button("Sonra Yapacağım →", use_container_width=True):
            st.session_state["onboarding_step"] = 3
            st.rerun()


def _step_first_analysis() -> None:
    """Adım 3: İlk analiz."""
    st.markdown(
        '<div class="onboarding-card">'
        '<div style="font-size:3rem;">🔍</div>'
        '<h3>İlk Analizinizi Yapın!</h3>'
        '<p style="color:#8892b0;">Bir şartname PDF\'i yükleyerek başlayın</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎮 Demo ile Dene", use_container_width=True):
            st.session_state["onboarding_completed"] = True
            st.session_state["demo_mode"] = True
            st.session_state["current_page"] = "analysis"
            st.session_state["analysis_state"] = "upload"
            st.rerun()
    with c2:
        if st.button("📤 PDF Yükle", type="primary", use_container_width=True):
            st.session_state["onboarding_completed"] = True
            st.session_state["current_page"] = "analysis"
            st.session_state["analysis_state"] = "upload"
            st.rerun()
