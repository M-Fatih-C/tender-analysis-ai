"""
TenderAI Demo Modu Verisi / Demo Mode Data.

DEMO_MODE=True olduğunda AI yerine kullanılan
hazır analiz sonuçları.

Pre-built analysis results used when DEMO_MODE=True
instead of calling the AI engine.
"""

DEMO_ANALYSIS_RESULT: dict = {
    "risk_score": 67,
    "risk_level": "YÜKSEK",
    "risk_analysis": {
        "genel_risk_seviyesi": "YÜKSEK",
        "risk_skoru": 67,
        "ozet": (
            "Bu ihale orta-yüksek risk taşımaktadır. Mali teminat oranları piyasa "
            "ortalamasının üzerinde olup, gecikme cezaları yüksek belirlenmiştir. "
            "Teknik açıdan uzman personel gereksinimi ve ekipman şartları dikkat "
            "gerektirmektedir."
        ),
        "riskler": [
            {
                "kategori": "Mali",
                "baslik": "Yüksek teminat oranı",
                "aciklama": "Geçici teminat %5 olarak belirlenmiş olup, bu oran standart %3'ün üzerindedir.",
                "seviye": "YÜKSEK",
                "madde_referans": "Madde 12.1, Sayfa 5",
                "oneri": "Teminat mektubu maliyetini teklife yansıtın.",
            },
            {
                "kategori": "Teknik",
                "baslik": "Uzman personel gereksinimi",
                "aciklama": "En az 3 adet 10 yıl deneyimli inşaat mühendisi istenmektedir.",
                "seviye": "ORTA",
                "madde_referans": "Madde 8.3, Sayfa 4",
                "oneri": "Mevcut kadronuzu kontrol edin, eksik pozisyonlar için alt yüklenici planlayın.",
            },
            {
                "kategori": "Hukuki",
                "baslik": "Sözleşme feshi koşulları",
                "aciklama": "İdare tek taraflı fesih hakkına sahip, yüklenici tazminat talep edemiyor.",
                "seviye": "KRİTİK",
                "madde_referans": "Madde 45.2, Sayfa 18",
                "oneri": "Hukuk danışmanınızla bu maddeyi detaylı inceleyin.",
            },
            {
                "kategori": "Süre",
                "baslik": "Sıkı teslim takvimi",
                "aciklama": "180 gün iş süresi, mevsim koşulları dikkate alındığında risk oluşturabilir.",
                "seviye": "ORTA",
                "madde_referans": "Madde 3.1, Sayfa 2",
                "oneri": "Detaylı iş programı hazırlayarak süre yeterliliğini analiz edin.",
            },
        ],
    },
    "required_documents": {
        "zorunlu_belgeler": [
            {"belge_adi": "İş Bitirme Belgesi", "aciklama": "Son 15 yıl içinde, teklif bedelinin %80'i tutarında"},
            {"belge_adi": "Bilanço Bilgileri", "aciklama": "Son 3 yıla ait, cari oran en az 0.75"},
            {"belge_adi": "İş Hacmi Belgesi", "aciklama": "Son 3 yılın ortalaması, teklif bedelinin %25'i"},
            {"belge_adi": "Banka Referans Mektubu", "aciklama": "Teklif bedelinin %10'u kadar kullanılmamış kredi"},
            {"belge_adi": "Anahtar Teknik Personel Listesi", "aciklama": "3 İnşaat Mühendisi, 1 Elektrik Mühendisi"},
            {"belge_adi": "Makine-Ekipman Taahhütnamesi", "aciklama": "Ekskavatör, vinç, beton pompası"},
        ],
        "istege_bagli_belgeler": [
            {"belge_adi": "ISO 9001 Kalite Yönetim Belgesi"},
            {"belge_adi": "ISO 14001 Çevre Yönetim Belgesi"},
        ],
        "onemli_uyarilar": [
            "Eksik belge sunulması halinde değerlendirme dışı bırakılırsınız.",
            "Belgelerin aslı veya noter onaylı sureti istenecektir.",
        ],
    },
    "penalty_clauses": {
        "cezalar": [
            {
                "ceza_turu": "Günlük Gecikme Cezası",
                "miktar_oran": "Sözleşme bedelinin %0.05'i / gün",
                "risk_seviyesi": "YÜKSEK",
                "madde_referans": "Madde 35.1",
                "aciklama": "Her takvim günü için uygulanır, üst limit sözleşme bedelinin %10'u",
            },
            {
                "ceza_turu": "Kalite Uyumsuzluk Cezası",
                "miktar_oran": "Sözleşme bedelinin %1'i",
                "risk_seviyesi": "ORTA",
                "madde_referans": "Madde 36.2",
                "aciklama": "Teknik şartnameye uygun olmayan iş tespit edildiğinde uygulanır",
            },
            {
                "ceza_turu": "İş Güvenliği İhlali",
                "miktar_oran": "25.000 TL / ihlal",
                "risk_seviyesi": "ORTA",
                "madde_referans": "Madde 38.4",
                "aciklama": "İSG mevzuatına aykırılık halinde",
            },
        ],
    },
    "financial_summary": {
        "tahmini_ihale_bedeli": "5.250.000 TL",
        "gecici_teminat": "262.500 TL (%5)",
        "kesin_teminat": "315.000 TL (%6)",
        "odeme_kosullari": "Aylık hakediş, onaydan sonra 30 gün içinde ödeme",
        "fiyat_farki": "Fiyat farkı hesaplanacaktır (2024/1 Bakanlar Kurulu Kararı)",
        "mali_riskler": [
            "Geçici teminat oranı standartın üzerinde (%5 vs %3)",
            "Hakediş ödeme süresi 30 gün — nakit akışını olumsuz etkileyebilir",
            "Fiyat farkı formülü net değil, ek maliyet riski var",
        ],
    },
    "timeline_analysis": {
        "toplam_is_suresi": "180 takvim günü",
        "ise_baslama_suresi": "Yer tesliminden itibaren 10 gün",
        "milestones": [
            {"asama": "Yer Teslimi", "sure": "Sözleşme + 15 gün"},
            {"asama": "Temel Kazı", "sure": "30 gün"},
            {"asama": "Kaba İnşaat", "sure": "90 gün"},
            {"asama": "İnce İşler", "sure": "45 gün"},
            {"asama": "Geçici Kabul", "sure": "180 gün (toplam)"},
        ],
        "gecikme_riski_degerlendirmesi": (
            "180 günlük süre kış aylarına denk gelmesi halinde sıkışık olabilir. "
            "Beton dökümü ve dış cephe işleri hava koşullarından etkilenebilir."
        ),
    },
    "executive_summary": {
        "ozet": (
            "5.250.000 TL tahmini bedelli bu yapım işi ihalesi, orta-yüksek risk "
            "kategorisinde değerlendirilmektedir. Mali açıdan teminat oranlarının "
            "yüksekliği, teknik açıdan uzman personel gereksinimleri, hukuki açıdan "
            "ise tek taraflı fesih maddeleri öne çıkan risklerdir."
        ),
        "guclu_yanlar": [
            "Teknik şartname açık ve net tanımlanmış",
            "Fiyat farkı hesaplanması öngörülmüş",
            "Hakediş usulü ödeme, nakit akışı için olumlu",
        ],
        "riskli_alanlar": [
            "Teminat oranları piyasa ortalamasının üzerinde",
            "Gecikme cezası oranı yüksek (%0.05/gün)",
            "Tek taraflı fesih riski mevcut",
            "180 günlük süre mevsim koşullarına göre sıkışık olabilir",
        ],
        "tavsiye": (
            "İhaleye DİKKATLİ GİRİLMESİ önerilir. Teminat maliyetleri teklif fiyatına "
            "yansıtılmalı, hukuki riskler avukat eşliğinde değerlendirilmeli ve detaylı "
            "iş programı ile süre yeterliliği kontrol edilmelidir."
        ),
    },
    "tokens_used": 12450,
    "cost_usd": 0.0623,
    "analysis_time": 38.5,
}
