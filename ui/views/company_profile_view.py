"""
TenderAI Firma Profili Sayfası v2.0.
"""

import json
import streamlit as st
from ui.components.header import render_header
from src.utils.helpers import get_turkish_cities


_SECTORS = ["İnşaat", "Bilişim (IT)", "Savunma Sanayi", "Medikal", "Enerji", "Ulaşım", "Çevre", "Gıda", "Diğer"]
_CERT_OPTIONS = ["ISO 9001", "ISO 14001", "ISO 45001", "ISO 27001", "TSE Belgesi", "CE Belgesi", "TÜRKAK Akreditasyonu"]
_EXPERIENCE_OPTIONS = ["Hastane", "Okul", "Yol", "Köprü", "Bina", "Altyapı", "Tünel", "Baraj", "Peyzaj", "Mekanik Tesisat", "Elektrik Tesisat"]


def render_company_profile() -> None:
    """Firma profili sayfası."""
    render_header("🏢 Firma Profili", "Firma bilgilerinizi girin, ihale uygunluk skorunuz otomatik hesaplansın")

    user_id = st.session_state.get("user_id", 0)
    profile = _load_profile(user_id)

    # ── Bölüm 1: Temel Bilgiler ──
    st.markdown('<div class="form-section"><div class="form-section-title">🏢 Temel Bilgiler</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        company_name = st.text_input("Firma Adı", value=profile.get("company_name", ""))
        tax_number = st.text_input("Vergi No", value=profile.get("tax_number", ""))
        city = st.selectbox("Şehir", [""] + get_turkish_cities(), index=_idx(profile.get("city"), get_turkish_cities()))
        established_year = st.number_input("Kuruluş Yılı", min_value=1900, max_value=2025, value=profile.get("established_year") or 2020)
    with c2:
        phone = st.text_input("Telefon", value=profile.get("phone", ""))
        website = st.text_input("Website", value=profile.get("website", ""))
        sector = st.selectbox("Sektör", [""] + _SECTORS, index=_idx(profile.get("sector"), _SECTORS))
        address = st.text_area("Adres", value=profile.get("address", ""), height=80)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Bölüm 2: Mali Bilgiler ──
    st.markdown('<div class="form-section"><div class="form-section-title">💰 Mali Bilgiler</div>', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        annual_revenue = st.number_input("Yıllık Ciro (TL)", min_value=0, value=int(profile.get("annual_revenue_try") or 0), step=1000000)
        employee_count = st.number_input("Personel Sayısı", min_value=0, value=profile.get("employee_count") or 0)
    with m2:
        bank_credit = st.number_input("Banka Kredi Limiti (TL)", min_value=0, value=int(profile.get("bank_credit_limit_try") or 0), step=1000000)
        max_tender = st.number_input("Maks İhale Tutarı (TL)", min_value=0, value=int(profile.get("max_tender_value_try") or 0), step=1000000)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Bölüm 3: Sertifikalar ──
    st.markdown('<div class="form-section"><div class="form-section-title">📜 Sertifikalar</div>', unsafe_allow_html=True)
    current_certs = _parse_json(profile.get("certifications", "[]"))
    certifications = st.multiselect("Sertifikalar", _CERT_OPTIONS, default=[c for c in current_certs if c in _CERT_OPTIONS])
    other_cert = st.text_input("Diğer sertifikalar (virgülle ayırın)")
    if other_cert:
        certifications.extend([c.strip() for c in other_cert.split(",") if c.strip()])
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Bölüm 4: İş Deneyimi ──
    st.markdown('<div class="form-section"><div class="form-section-title">🔧 İş Deneyimi</div>', unsafe_allow_html=True)
    current_areas = _parse_json(profile.get("experience_areas", "[]"))
    experience_areas = st.multiselect("Faaliyet Alanları", _EXPERIENCE_OPTIONS, default=[e for e in current_areas if e in _EXPERIENCE_OPTIONS])
    reference_projects = st.text_area("Referans Projeler (her satır bir proje)", value="\n".join(_parse_json(profile.get("reference_projects", "[]"))), height=100)
    equipment_list = st.text_area("Ekipman Listesi (her satır bir ekipman)", value="\n".join(_parse_json(profile.get("equipment_list", "[]"))), height=80)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Kaydet ──
    if st.button("💾 Profili Kaydet", type="primary", use_container_width=True):
        with st.spinner("Kaydediliyor..."):
            try:
                refs = [r.strip() for r in reference_projects.split("\n") if r.strip()]
                equips = [e.strip() for e in equipment_list.split("\n") if e.strip()]

                from src.database.db import DatabaseManager, create_or_update_company_profile
                db_mgr = DatabaseManager()
                db_mgr.init_db()
                with db_mgr.get_db() as db:
                    create_or_update_company_profile(
                        db, user_id,
                        company_name=company_name, tax_number=tax_number,
                        city=city, address=address, phone=phone, website=website,
                        sector=sector, annual_revenue_try=annual_revenue,
                        employee_count=employee_count, established_year=established_year,
                        certifications=json.dumps(certifications, ensure_ascii=False),
                        experience_areas=json.dumps(experience_areas, ensure_ascii=False),
                        equipment_list=json.dumps(equips, ensure_ascii=False),
                        max_tender_value_try=max_tender,
                        bank_credit_limit_try=bank_credit,
                        reference_projects=json.dumps(refs, ensure_ascii=False),
                    )
                    db.commit()
                st.success("✅ Firma profili kaydedildi!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Kayıt hatası: {e}")


def _load_profile(user_id: int) -> dict:
    try:
        from src.database.db import DatabaseManager, get_company_profile
        db_mgr = DatabaseManager()
        db_mgr.init_db()
        with db_mgr.get_db() as db:
            p = get_company_profile(db, user_id)
            if p:
                return {
                    "company_name": p.company_name or "", "tax_number": p.tax_number or "",
                    "city": p.city or "", "address": p.address or "", "phone": p.phone or "",
                    "website": p.website or "", "sector": p.sector or "",
                    "annual_revenue_try": p.annual_revenue_try, "employee_count": p.employee_count,
                    "established_year": p.established_year, "certifications": p.certifications or "[]",
                    "experience_areas": p.experience_areas or "[]",
                    "equipment_list": p.equipment_list or "[]",
                    "max_tender_value_try": p.max_tender_value_try,
                    "bank_credit_limit_try": p.bank_credit_limit_try,
                    "reference_projects": p.reference_projects or "[]",
                }
    except Exception:
        pass
    return {}


def _idx(val, options):
    """Selectbox index helper."""
    if val and val in options:
        return options.index(val) + 1
    return 0


def _parse_json(val) -> list:
    if isinstance(val, list):
        return val
    try:
        r = json.loads(val)
        return r if isinstance(r, list) else []
    except Exception:
        return []
