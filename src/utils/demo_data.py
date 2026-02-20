"""
TenderAI Demo Verileri / Demo Data.

API key olmadığında veya demo modda kullanılacak gerçekçi Türkçe veriler.
"""

DEMO_ANALYSIS_RESULT: dict = {
    "risk_score": 72,
    "risk_level": "YÜKSEK",
    "model_used": "demo",
    "risk_analysis": {
        "genel_risk_seviyesi": "YÜKSEK",
        "risk_skoru": 72,
        "ozet": "Bu ihale orta-yüksek risk seviyesinde değerlendirilmektedir. Özellikle ceza maddeleri ve teminat koşulları dikkat gerektirmektedir.",
        "riskler": [
            {
                "kategori": "Mali", "baslik": "Yüksek Gecikme Cezası",
                "aciklama": "Sözleşme bedelinin günlük %0.06 oranında gecikme cezası uygulanacaktır. 30 günlük gecikme durumunda toplam ceza sözleşme bedelinin %1.8'ine ulaşmaktadır.",
                "seviye": "KRİTİK", "madde_referans": "Madde 25.1, Sayfa 18",
                "oneri": "Gecikme riskine karşı iş programını %20 güvenlik payı ile hazırlayın."
            },
            {
                "kategori": "Teknik", "baslik": "Özel Uzmanlık Gerektiren İmalat",
                "aciklama": "İhale kapsamında heliport yapımı ve özel ameliyathane havalandırma sistemi kurulumu bulunmaktadır.",
                "seviye": "YÜKSEK", "madde_referans": "Teknik Şartname Bölüm 4.3, Sayfa 45",
                "oneri": "Alt yüklenici anlaşmalarını ihale öncesi tamamlayın."
            },
            {
                "kategori": "Hukuki", "baslik": "Sözleşme Fesih Koşulları Ağır",
                "aciklama": "İdarenin tek taraflı fesih hakkı geniş tutulmuştur. İş programının %15 gerisinde kalınması halinde idare sözleşmeyi feshedebilir.",
                "seviye": "YÜKSEK", "madde_referans": "Madde 30.2, Sayfa 22",
                "oneri": "İş programı takibini haftalık yapın, sapmaları erkenden tespit edin."
            },
            {
                "kategori": "Mali", "baslik": "Teminat Mektubu Yüksek",
                "aciklama": "Kesin teminat oranı sözleşme bedelinin %10'u olarak belirlenmiştir. Tahmini 8.5 milyon TL teminat mektubu gerekecektir.",
                "seviye": "ORTA", "madde_referans": "Madde 11.1, Sayfa 8",
                "oneri": "Banka ile teminat mektubu limitinizi kontrol edin."
            },
            {
                "kategori": "Süre", "baslik": "Kış Aylarında Çalışma Sınırlaması",
                "aciklama": "Teknik şartnamede kış aylarında (Aralık-Şubat) beton dökme işleri sınırlandırılmıştır.",
                "seviye": "ORTA", "madde_referans": "Teknik Şartname 2.8, Sayfa 31",
                "oneri": "İş programında kış aylarını beton dışı işlere ayırın."
            },
        ],
    },
    "required_documents": {
        "toplam_belge_sayisi": 14,
        "zorunlu_belgeler": [
            {"belge_adi": "Bilanço ve Eşdeğer Belgeler", "aciklama": "Son 3 yılın bilançosu, cari oran en az 0.75", "kategori": "Mali", "nereden_alinir": "YMM/SMMM", "tahmini_sure": "3-5 iş günü", "madde_referans": "Madde 7.4.2"},
            {"belge_adi": "İş Hacmini Gösteren Belgeler", "aciklama": "Son 3 yılda en az 40M TL ciro", "kategori": "Mali", "nereden_alinir": "Vergi dairesi/YMM", "tahmini_sure": "3-5 iş günü", "madde_referans": "Madde 7.4.3"},
            {"belge_adi": "İş Deneyim Belgesi", "aciklama": "Son 15 yılda en az 35M TL tutarında benzer iş deneyimi", "kategori": "Referans", "nereden_alinir": "İlgili kamu kurumu", "tahmini_sure": "5-10 iş günü", "madde_referans": "Madde 7.5.1"},
            {"belge_adi": "Geçici Teminat Mektubu", "aciklama": "Teklif bedelinin %3'ü, yaklaşık 2.55M TL", "kategori": "Mali", "nereden_alinir": "Banka", "tahmini_sure": "1-2 iş günü", "madde_referans": "Madde 7.3.1"},
            {"belge_adi": "İmza Sirküleri", "aciklama": "Noterden onaylı, son 6 ay içinde düzenlenmiş", "kategori": "Yeterlilik", "nereden_alinir": "Noter", "tahmini_sure": "1 iş günü", "madde_referans": "Madde 7.1"},
            {"belge_adi": "Ticaret Sicil Gazetesi", "aciklama": "Güncel adres ve ortaklık yapısını gösterir", "kategori": "Yeterlilik", "nereden_alinir": "Ticaret Odası", "tahmini_sure": "1 iş günü", "madde_referans": "Madde 7.1"},
            {"belge_adi": "SGK Borcu Yoktur Belgesi", "aciklama": "İhale tarihinde güncel olmalı", "kategori": "Yeterlilik", "nereden_alinir": "SGK", "tahmini_sure": "1 iş günü", "madde_referans": "Madde 7.1.4"},
            {"belge_adi": "Vergi Borcu Yoktur Belgesi", "aciklama": "İhale tarihinde güncel olmalı", "kategori": "Yeterlilik", "nereden_alinir": "Vergi Dairesi", "tahmini_sure": "1 iş günü", "madde_referans": "Madde 7.1.4"},
            {"belge_adi": "ISO 9001 Kalite Yönetim Sistemi", "aciklama": "TÜRKAK akreditasyonlu kuruluştan", "kategori": "Sertifika", "nereden_alinir": "Belgelendirme kuruluşu", "tahmini_sure": "Mevcut olmalı", "madde_referans": "Teknik Şartname 1.5"},
            {"belge_adi": "ISO 14001 Çevre Yönetim Sistemi", "aciklama": "TÜRKAK akreditasyonlu kuruluştan", "kategori": "Sertifika", "nereden_alinir": "Belgelendirme kuruluşu", "tahmini_sure": "Mevcut olmalı", "madde_referans": "Teknik Şartname 1.5"},
        ],
        "istege_bagli_belgeler": [
            {"belge_adi": "ISO 45001 İSG Belgesi", "aciklama": "Değerlendirmede ek puan sağlar", "kategori": "Sertifika"},
            {"belge_adi": "Kapasite Raporu", "aciklama": "Ekipman durumunu belgeler", "kategori": "Teknik"},
        ],
        "onemli_uyarilar": [
            "Bilanço yeterlilik oranları son derece yüksek tutulmuştur, dikkat edilmeli",
            "İş deneyim belgesi benzer iş tanımı dar kapsamlıdır (B-III grubu)",
            "Tüm belgelerin asılları veya noter onaylı suretleri gereklidir",
        ],
    },
    "penalty_clauses": {
        "toplam_ceza_sayisi": 5,
        "toplam_risk_degerlendirmesi": "Ceza maddeleri ortalamanın üzerinde ağırdır. Özellikle gecikme cezası oranı sektör ortalamasının 2 katıdır.",
        "cezalar": [
            {"madde_no": "25.1", "sayfa": 18, "ceza_turu": "Gecikme", "miktar_oran": "Günlük sözleşme bedelinin %0.06", "aciklama": "Her takvim günü gecikme için uygulanır", "risk_seviyesi": "KRİTİK", "senaryo": "85M TL sözleşmede 30 gün gecikme = 1.53M TL ceza", "oneri": "İş programına minimum %20 güvenlik payı ekleyin", "madde_referans": "Madde 25.1"},
            {"madde_no": "25.3", "sayfa": 19, "ceza_turu": "Eksik İş", "miktar_oran": "Eksik iş bedelinin %10'u", "aciklama": "Geçici kabulde tespit edilen eksikler için", "risk_seviyesi": "YÜKSEK", "senaryo": "500K TL eksik iş = 50K TL ceza", "oneri": "Geçici kabul öncesi kapsamlı iç denetim yapın", "madde_referans": "Madde 25.3"},
            {"madde_no": "25.5", "sayfa": 19, "ceza_turu": "Kalite", "miktar_oran": "Hatalı imalat bedelinin %20'si", "aciklama": "Teknik şartnameye uygun olmayan imalatlar", "risk_seviyesi": "YÜKSEK", "senaryo": "Uygunsuz beton dökümü 2M TL = 400K TL ceza + söküm", "oneri": "Kalite kontrol müfettişi görevlendirin", "madde_referans": "Madde 25.5"},
            {"madde_no": "30.2", "sayfa": 22, "ceza_turu": "Fesih", "miktar_oran": "Kesin teminatın irat kaydı + yasaklama", "aciklama": "İş programının %15 gerisinde kalınması halinde", "risk_seviyesi": "KRİTİK", "senaryo": "Fesih durumunda 8.5M TL teminat kaybı + 2 yıl yasaklama", "oneri": "Haftalık ilerleme raporu hazırlayın", "madde_referans": "Madde 30.2"},
            {"madde_no": "27.1", "sayfa": 20, "ceza_turu": "Kara Liste", "miktar_oran": "1-2 yıl yasaklama", "aciklama": "Taahhüdün yerine getirilmemesi durumunda", "risk_seviyesi": "ORTA", "senaryo": "Yasaklama tüm kamu ihalelerini kapsar", "oneri": "Sözleşme yükümlülüklerini tam olarak anlayın", "madde_referans": "Madde 27.1"},
        ],
    },
    "financial_summary": {
        "tahmini_ihale_bedeli": "85.000.000 TL",
        "gecici_teminat": "2.550.000 TL (%3)",
        "kesin_teminat": "Sözleşme bedelinin %10'u",
        "odeme_kosullari": "Aylık hakediş, fatura tarihinden itibaren 30 gün içinde",
        "avans": {"var_mi": True, "oran": "%10 (SGM üzerinden), teminat mektubu karşılığı"},
        "fiyat_farki": {"var_mi": True, "aciklama": "TÜİK endekslerine göre fiyat farkı hesaplanacak"},
        "mali_riskler": [
            "Gecikme cezası oranı yüksek (%0.06/gün)",
            "Kesin teminat oranı %10 (standart %6'nın üzerinde)",
            "Hakediş ödeme süresi 30 gün (nakit akışı planlaması önemli)",
        ],
        "mali_firsatlar": [
            "%10 avans imkanı nakit akışını rahatlatır",
            "Fiyat farkı uygulanması enflasyon riskini azaltır",
            "Hakediş ödemeleri aylık periyotta",
        ],
        "oneriler": [
            "Avans imkanını mutlaka kullanın",
            "Banka ile teminat mektubu limitini 10M TL üzerine çıkarın",
            "Aylık nakit akışı tablosu hazırlayın",
        ],
    },
    "timeline_analysis": {
        "toplam_is_suresi": "540 takvim günü (18 ay)",
        "ise_baslama_suresi": "Yer tesliminden itibaren 10 gün",
        "onemli_tarihler": [
            {"tarih_veya_sure": "İhale tarihi: 15.07.2025", "aciklama": "Teklif son tarihi"},
            {"tarih_veya_sure": "180. gün", "aciklama": "Kaba inşaat tamamlanmış olacak"},
            {"tarih_veya_sure": "360. gün", "aciklama": "Mekanik ve elektrik tesisat tamamlanacak"},
            {"tarih_veya_sure": "540. gün", "aciklama": "Geçici kabul başvurusu"},
        ],
        "milestones": [
            {"asama": "Temel kazı ve betonarme temel", "sure": "90 gün", "tamamlanma": "%15"},
            {"asama": "Kaba inşaat (taşıyıcı sistem)", "sure": "180 gün", "tamamlanma": "%40"},
            {"asama": "Çatı ve dış cephe", "sure": "270 gün", "tamamlanma": "%55"},
            {"asama": "Mekanik + Elektrik tesisat", "sure": "360 gün", "tamamlanma": "%75"},
            {"asama": "İnce işler", "sure": "450 gün", "tamamlanma": "%90"},
            {"asama": "Tamamlama ve geçici kabul", "sure": "540 gün", "tamamlanma": "%100"},
        ],
        "gecikme_riski_degerlendirmesi": "Orta-Yüksek. Kış aylarında beton dökme kısıtlaması ve 540 günlük süre göz önüne alındığında, iş programı sıkı tutulmalıdır.",
        "oneriler": [
            "İş programını PERT/CPM yöntemiyle hazırlayın",
            "Kış aylarını iç mekan işlerine ayırın",
            "Kritik malzemelerin tedarik süresini önceden planlayın",
        ],
    },
    "executive_summary": {
        "ihale_adi": "Sakarya Devlet Hastanesi Ek Bina İnşaatı Yapım İşi",
        "tavsiye": "DİKKATLİ GİR",
        "tavsiye_nedeni": "İhale kârlı bir iş olma potansiyeli taşımakla birlikte, yüksek gecikme cezaları ve ağır fesih koşulları nedeniyle dikkatli yaklaşılmalıdır.",
        "ozet": "Sakarya Devlet Hastanesi Ek Bina İnşaatı, 85 milyon TL yaklaşık maliyetli orta-büyük ölçekli bir yapım işidir. Firma olarak bu ihaleye katılabilmek için en az 40M TL ciro, 35M TL benzer iş deneyimi ve gerekli sertifikalara sahip olmanız gerekmektedir.",
        "en_kritik_3_bulgu": [
            "Gecikme cezası sektör ortalamasının 2 katı (günlük %0.06)",
            "İş programının %15 gerisinde kalınması halinde tek taraflı fesih hakkı",
            "Heliport ve özel ameliyathane havalandırma sistemi uzmanlık gerektiriyor",
        ],
        "guclu_yanlar": [
            "%10 avans imkanı nakit akışını destekler",
            "Fiyat farkı uygulanması enflasyon koruması sağlar",
            "18 aylık süre bu büyüklükte iş için makul",
            "Kamu hastanesi projesi iş deneyim belgesi için değerli",
        ],
        "riskli_alanlar": [
            "Gecikme cezası çok yüksek",
            "Kesin teminat oranı standart üzerinde (%10)",
            "Özel uzmanlık gerektiren imalatlar var",
            "Kış aylarında çalışma sınırlaması",
            "Fesih koşulları ağır",
        ],
    },
}


DEMO_CHAT_RESPONSES: dict = {
    "teminat": "Bu ihale için geçici teminat tutarı yaklaşık maliyetin %3'ü olan **2.550.000 TL**'dir *(Madde 7.3.1, Sayfa 6)*. Kesin teminat ise sözleşme bedelinin **%10**'u olarak belirlenmiştir *(Madde 11.1, Sayfa 8)*. Standart uygulamada kesin teminat %6 olmakla birlikte, bu ihalede %10 olması dikkat çekicidir.",
    "ceza": "Gecikme cezası günlük sözleşme bedelinin **%0.06**'sı oranındadır *(Madde 25.1, Sayfa 18)*. 85M TL bedelli bir sözleşmede bu, günlük **51.000 TL** ceza anlamına gelir. 30 günlük gecikme durumunda toplam **1.53M TL** ceza uygulanacaktır.",
    "süre": "Toplam iş süresi yer tesliminden itibaren **540 takvim günüdür (18 ay)**. Yer teslimi sözleşmenin imzalanmasından itibaren 10 gün içinde yapılacaktır *(Madde 10.1, Sayfa 7)*.",
    "belge": "Bu ihaleye katılmak için toplam **14 belge** gereklidir. En kritik olanlar: İş Deneyim Belgesi (min 35M TL), Bilanço (cari oran ≥0.75), ISO 9001 ve ISO 14001 sertifikaları *(Madde 7.1-7.5)*.",
    "bedel": "İhalenin yaklaşık maliyeti **85.000.000 TL** olarak hesaplanmıştır. Bu tutar KDV hariçtir *(İlan Metni ve Madde 5)*.",
    "alt yüklenici": "Şartnamede alt yüklenici kullanımına izin verilmektedir ancak toplam iş bedelinin **%30**'unu geçemez. Alt yüklenici onayı idare tarafından verilmelidir *(Madde 18, Sayfa 14)*.",
    "avans": "Evet, bu ihalede avans imkanı vardır. Sözleşme bedelinin **%10**'u oranında avans ödenebilir. Bunun için teminat mektubu sunulması gereklidir *(Madde 19.2, Sayfa 15)*.",
    "default": "Bu konuda şartnamede detaylı bilgi bulunmaktadır. Size daha spesifik yardımcı olabilmem için sorunuzu biraz daha detaylandırabilir misiniz? Örneğin teminat, ceza, süre, belge gereksinimleri gibi konularda soru sorabilirsiniz.",
}
