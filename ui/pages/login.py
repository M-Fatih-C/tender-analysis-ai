"""
TenderAI Giriş Sayfası / Login Page.

Kullanıcı giriş ve kayıt arayüzü.
User login and registration interface.

Bu modül Modül 5'te implement edilecektir.
This module will be implemented in Module 5.
"""

import streamlit as st


def render_login_page() -> None:
    """
    Giriş sayfasını render et / Render login page.

    Kullanıcı giriş formu ve kayıt yönlendirmesi.
    User login form and registration redirect.

    Raises:
        NotImplementedError: Modül 5'te implement edilecek
    """
    st.title("🔐 Giriş Yap")
    st.markdown("---")

    with st.form("login_form"):
        username = st.text_input("Kullanıcı Adı", placeholder="kullanici@email.com")
        password = st.text_input("Şifre", type="password", placeholder="••••••••")
        submit = st.form_submit_button("Giriş Yap", use_container_width=True)

        if submit:
            st.warning("⚠️ Giriş sistemi Modül 5'te implement edilecektir.")

    st.markdown("---")
    st.markdown("Hesabınız yok mu? **Kayıt olun**")


def render_register_page() -> None:
    """
    Kayıt sayfasını render et / Render registration page.

    Yeni kullanıcı kayıt formu.
    New user registration form.

    Raises:
        NotImplementedError: Modül 5'te implement edilecek
    """
    st.title("📝 Kayıt Ol")
    st.markdown("---")

    with st.form("register_form"):
        full_name = st.text_input("Ad Soyad", placeholder="Ad Soyad")
        email = st.text_input("E-posta", placeholder="kullanici@email.com")
        company = st.text_input("Firma Adı", placeholder="Firma A.Ş.")
        username = st.text_input("Kullanıcı Adı", placeholder="kullanici123")
        password = st.text_input("Şifre", type="password", placeholder="••••••••")
        password_confirm = st.text_input("Şifre Tekrar", type="password", placeholder="••••••••")
        submit = st.form_submit_button("Kayıt Ol", use_container_width=True)

        if submit:
            st.warning("⚠️ Kayıt sistemi Modül 5'te implement edilecektir.")
