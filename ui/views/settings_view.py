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
        st.markdown("**KVKK Uyumu** — Kişisel Verilerin Korunması")
        st.caption("6698 sayılı KVKK kapsamında verilerinize erişim ve silme hakkınız bulunmaktadır.")

        col_k1, col_k2 = st.columns(2)
        with col_k1:
            if st.button("📥 Tüm Verilerimi İndir", use_container_width=True):
                try:
                    user_id = st.session_state.get("user_id", 0)
                    import json
                    from src.database.db import DatabaseManager
                    from src.utils.audit import export_user_data
                    db_mgr = DatabaseManager()
                    db_mgr.init_db()
                    with db_mgr.get_db() as db:
                        data = export_user_data(db, user_id)
                    json_str = json.dumps(data, ensure_ascii=False, default=str, indent=2)
                    st.download_button(
                        "💾 JSON İndir", data=json_str.encode("utf-8"),
                        file_name="TenderAI_KVKK_Export.json", mime="application/json",
                        key="kvkk_download",
                    )
                    st.success("✅ Verileriniz hazır. İndirme butonuna tıklayın.")
                except Exception as e:
                    st.error(f"Veri dışa aktarma hatası: {e}")

        with col_k2:
            if st.button("📋 İşlem Geçmişi", use_container_width=True):
                try:
                    user_id = st.session_state.get("user_id", 0)
                    from src.database.db import DatabaseManager
                    from src.utils.audit import get_user_audit_logs
                    db_mgr = DatabaseManager()
                    db_mgr.init_db()
                    with db_mgr.get_db() as db:
                        logs = get_user_audit_logs(db, user_id, limit=20)
                    if logs:
                        for log in logs:
                            st.markdown(
                                f'<div style="font-size:0.75rem;color:#8892b0;margin:2px 0;">'
                                f'🕐 {log["created_at"]} — <b>{log["action"]}</b>'
                                f'{" — " + log["details"][:50] if log["details"] else ""}'
                                f'</div>', unsafe_allow_html=True,
                            )
                    else:
                        st.caption("Henüz işlem geçmişi yok.")
                except Exception:
                    st.caption("İşlem geçmişi yüklenemedi.")

        st.markdown("---")
        st.markdown("**⚠️ Tehlikeli Bölge**")
        confirm = st.checkbox("Hesabımı ve tüm verilerimi silmek istiyorum", key="kvkk_delete_confirm")
        if confirm:
            if st.button("🗑️ Hesabımı Kalıcı Olarak Sil", type="primary"):
                try:
                    user_id = st.session_state.get("user_id", 0)
                    from src.database.db import DatabaseManager
                    from src.utils.audit import delete_user_data
                    db_mgr = DatabaseManager()
                    db_mgr.init_db()
                    with db_mgr.get_db() as db:
                        ok = delete_user_data(db, user_id)
                    if ok:
                        st.success("✅ Tüm verileriniz silindi. Çıkış yapılıyor...")
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                    else:
                        st.error("Silme işlemi başarısız oldu.")
                except Exception as e:
                    st.error(f"Hesap silme hatası: {e}")

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
