"""
TenderAI Ayarlar Sayfası v2.0.
"""

import streamlit as st
from ui.components.header import render_header
from src.utils.helpers import calculate_password_strength


def render_settings() -> None:
    """Kullanıcı ayarları sayfası."""
    render_header("⚙️ Ayarlar", "Hesap ve uygulama ayarlarınız")

    # ── Profil Bilgileri ──
    with st.expander("👤 Profil Bilgileri", expanded=True):
        with st.form("profile_form"):
            name = st.text_input("Ad Soyad", value=st.session_state.get("user_name", ""))
            email = st.text_input("Email", value=st.session_state.get("user_email", ""), disabled=True)
            company = st.text_input("Firma Adı", value=st.session_state.get("user_company", ""))
            if st.form_submit_button("Güncelle", use_container_width=True):
                try:
                    user_id = st.session_state.get("user_id", 0)
                    from src.database.db import DatabaseManager
                    from src.database.models import User
                    db_mgr = DatabaseManager()
                    db_mgr.init_db()
                    with db_mgr.get_db() as db:
                        user = db.query(User).filter(User.id == user_id).first()
                        if user:
                            user.full_name = name
                            user.company_name = company
                            db.commit()
                    st.session_state["user_name"] = name
                    st.session_state["user_company"] = company
                    st.success("✅ Profil güncellendi!")
                except Exception as e:
                    st.error(f"❌ Hata: {e}")

    # ── Şifre Değiştir ──
    with st.expander("🔒 Şifre Değiştir"):
        with st.form("password_form"):
            old_pass = st.text_input("Mevcut Şifre", type="password")
            new_pass = st.text_input("Yeni Şifre", type="password")
            if new_pass:
                s = calculate_password_strength(new_pass)
                st.markdown(
                    f'<div class="strength-bar"><div class="strength-fill" '
                    f'style="width:{s["score"]*25}%;background:{s["color"]};"></div></div>'
                    f'<span style="font-size:0.7rem;color:{s["color"]};">{s["label"]}</span>',
                    unsafe_allow_html=True,
                )
            new_pass2 = st.text_input("Yeni Şifre Tekrar", type="password")
            if st.form_submit_button("Şifreyi Değiştir", use_container_width=True):
                if not old_pass or not new_pass:
                    st.error("Tüm alanlar zorunludur.")
                elif new_pass != new_pass2:
                    st.error("Şifreler eşleşmiyor.")
                elif len(new_pass) < 8:
                    st.error("En az 8 karakter.")
                else:
                    try:
                        user_id = st.session_state.get("user_id", 0)
                        from src.database.db import DatabaseManager
                        from src.auth.auth import AuthManager
                        db_mgr = DatabaseManager()
                        db_mgr.init_db()
                        with db_mgr.get_db() as db:
                            auth = AuthManager(db)
                            email = st.session_state.get("user_email", "")
                            success, msg, _ = auth.login(email, old_pass)
                            if not success:
                                st.error("Mevcut şifre hatalı.")
                            else:
                                from src.database.models import User
                                import bcrypt
                                user = db.query(User).filter(User.id == user_id).first()
                                if user:
                                    user.password_hash = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
                                    db.commit()
                                    st.success("✅ Şifre değiştirildi!")
                    except Exception as e:
                        st.error(f"❌ Hata: {e}")

    # ── Bildirim Tercihleri ──
    with st.expander("🔔 Bildirim Tercihleri"):
        st.toggle("Analiz tamamlandığında bildir", value=True, key="notif_analysis")
        st.toggle("Plan limiti uyarısı", value=True, key="notif_limit")
        st.toggle("Yeni özellik duyuruları", value=True, key="notif_features")
        st.caption("Bildirim ayarları şimdilik yerel olarak saklanmaktadır.")

    # ── Uygulama Ayarları ──
    with st.expander("🎨 Uygulama Ayarları"):
        st.selectbox("Dil", ["🇹🇷 Türkçe"], disabled=True)
        st.selectbox("Tema", ["🌙 Dark"], disabled=True)
        st.selectbox("Varsayılan Rapor Formatı", ["PDF", "Excel", "İkisi de"], key="default_format")

    # ── Hesap İşlemleri ──
    with st.expander("⚠️ Hesap İşlemleri"):
        st.markdown("**KVKK Uyumu**")
        if st.button("📥 Tüm Verilerimi İndir"):
            st.info("Bu özellik yakında aktif olacaktır.")

        st.markdown("---")
        st.markdown("**⚠️ Tehlikeli Bölge**")
        if st.button("🗑️ Hesabımı Sil", type="secondary"):
            st.warning("Bu işlem geri alınamaz. Tüm verileriniz silinecektir.")
            if st.button("Evet, hesabımı silmek istiyorum", type="primary", key="confirm_delete"):
                st.info("Hesap silme özelliği yakında aktif olacaktır.")

    # ── Hakkında ──
    with st.expander("ℹ️ Hakkında"):
        st.markdown("""
        **TenderAI v2.0.0**
        
        İhale şartnamesi analiz platformu. Yapay zeka destekli risk analizi, 
        belge kontrolü ve ihale danışmanlığı.
        
        © 2025 TenderAI. Tüm hakları saklıdır.
        
        - [Kullanım Koşulları](#)
        - [Gizlilik Politikası](#)
        - [KVKK Aydınlatma Metni](#)
        """)
