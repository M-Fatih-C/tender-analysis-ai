"""
TenderAI LLM Prompt Şablonları / LLM Prompt Templates.

İhale şartname analizi için kullanılan tüm yapay zeka prompt'larını içerir.
Contains all AI prompts used for tender specification analysis.

Her prompt:
  - Türkçe ihale terminolojisi kullanır
  - JSON formatında çıktı üretir
  - 4734/4735 sayılı kanun referansları verir
  - System role olarak 20 yıl deneyimli ihale uzmanı kullanır
"""

# ============================================================
# Sistem Rolü / System Role
# ============================================================

SYSTEM_ROLE: str = (
    "Sen Türkiye kamu ihale mevzuatında 20 yıl deneyimli bir ihale uzmanısın. "
    "4734 sayılı Kamu İhale Kanunu ve 4735 sayılı Kamu İhale Sözleşmeleri Kanunu'nu "
    "çok iyi biliyorsun. İhale teknik ve idari şartnamelerini analiz edebilir, "
    "riskleri tespit edebilir ve firmaya stratejik öneriler sunabilirsin. "
    "Yanıtlarını kesinlikle JSON formatında ver. Şartnamede bulunmayan bilgi için "
    "'Şartnamede belirtilmemiş' yaz."
)

# ============================================================
# PROMPT 1: Risk Analizi / Risk Analysis
# ============================================================

RISK_ANALYSIS_PROMPT: str = """Aşağıdaki ihale şartname bölümlerini analiz ederek kapsamlı bir risk değerlendirmesi yap.

Analiz edeceğin risk kategorileri:
1. **Mali Riskler**: Teminat oranları, ceza miktarları, ödeme koşulları, fiyat farkı riskleri
2. **Teknik Riskler**: Uzmanlık gereksinimleri, ekipman ihtiyacı, alt yüklenici zorunlulukları, kalite standartları
3. **Hukuki Riskler**: Sözleşme feshi koşulları, ihtilaf çözüm mekanizması, mücbir sebep hükümleri
4. **Süre Riskleri**: Gerçekçi olmayan teslim süreleri, gecikme cezaları, milestone baskısı

Her risk için madde numarası ve sayfa referansı ver. 4734/4735 sayılı kanunlara uygunluk açısından değerlendir.

Şartname Bölümleri:
{context}

Kesinlikle aşağıdaki JSON formatında yanıt ver:
{{
  "genel_risk_seviyesi": "DÜŞÜK/ORTA/YÜKSEK/ÇOK YÜKSEK",
  "risk_skoru": 0-100,
  "ozet": "Genel risk değerlendirme özeti",
  "riskler": [
    {{
      "kategori": "Mali/Teknik/Hukuki/Süre",
      "baslik": "Kısa risk başlığı",
      "aciklama": "Detaylı risk açıklaması",
      "seviye": "DÜŞÜK/ORTA/YÜKSEK/KRİTİK",
      "madde_referans": "Madde X, Sayfa Y",
      "oneri": "Firma bu konuda ne yapmalı"
    }}
  ]
}}"""

# ============================================================
# PROMPT 2: Gerekli Belgeler / Required Documents
# ============================================================

REQUIRED_DOCUMENTS_PROMPT: str = """Aşağıdaki ihale şartname bölümlerini analiz ederek teklif vermek için gerekli TÜM belgeleri listele.

Belge kategorileri:
- **Yeterlilik Belgeleri**: İş deneyim, bilanço, ciro belgeleri
- **Mali Belgeler**: Banka referans mektubu, vergi/SGK borcu yoktur yazısı
- **Teknik Belgeler**: Teknik yeterlilik, kalite sertifikaları, standart uygunluk
- **Sertifika/Lisans**: ISO, TSE, CE belgeleri, yetki belgeleri
- **Referans Belgeleri**: Benzer iş deneyim belgeleri, referans mektupları

Her belge için nereden alınacağı ve tahmini süresini belirt.
4734 sayılı Kanun kapsamında zorunlu ve isteğe bağlı belgeleri ayır.

Şartname Bölümleri:
{context}

Kesinlikle aşağıdaki JSON formatında yanıt ver:
{{
  "toplam_belge_sayisi": 0,
  "zorunlu_belgeler": [
    {{
      "belge_adi": "Belge adı",
      "aciklama": "Belgenin ne olduğu ve neden gerektiği",
      "kategori": "Yeterlilik/Mali/Teknik/Sertifika/Referans",
      "nereden_alinir": "Hangi kurumdan/nasıl temin edilir",
      "tahmini_sure": "Tahmini temin süresi",
      "madde_referans": "İlgili madde numarası"
    }}
  ],
  "istege_bagli_belgeler": [
    {{
      "belge_adi": "Belge adı",
      "aciklama": "Açıklama",
      "kategori": "Kategori",
      "nereden_alinir": "Temin yeri",
      "tahmini_sure": "Süre",
      "madde_referans": "Madde no"
    }}
  ],
  "onemli_uyarilar": ["Dikkat edilmesi gereken kritik uyarılar"]
}}"""

# ============================================================
# PROMPT 3: Ceza Maddeleri / Penalty Clauses
# ============================================================

PENALTY_CLAUSES_PROMPT: str = """Aşağıdaki ihale şartname bölümlerindeki TÜM ceza ve yaptırım maddelerini tespit et.

Ceza türleri:
- **Gecikme Cezası**: Teslim gecikmesi durumunda uygulanan cezalar
- **Eksik İş Cezası**: İşin eksik veya hatalı yapılması durumunda
- **Kalite Cezası**: Kalite standartlarına uyulmaması
- **Fesih**: Sözleşmenin feshi koşulları ve sonuçları
- **Kara Liste**: İhaleden yasaklanma koşulları

Her ceza için oranını/tutarını, uygulanacağı senaryoyu ve firmaya önerisini belirt.
4735 sayılı Kanun açısından cezaların yasal uygunluğunu değerlendir.

Şartname Bölümleri:
{context}

Kesinlikle aşağıdaki JSON formatında yanıt ver:
{{
  "toplam_ceza_sayisi": 0,
  "toplam_risk_degerlendirmesi": "Ceza maddelerinin genel değerlendirmesi",
  "cezalar": [
    {{
      "madde_no": "İlgili madde numarası",
      "sayfa": 0,
      "ceza_turu": "Gecikme/Eksik İş/Kalite/Fesih/Kara Liste",
      "oran_veya_tutar": "Ceza oranı veya tutarı",
      "aciklama": "Cezanın detaylı açıklaması",
      "risk_seviyesi": "DÜŞÜK/ORTA/YÜKSEK/KRİTİK",
      "senaryo": "Bu ceza şu durumda uygulanır: ...",
      "oneri": "Bu cezadan kaçınmak için yapılması gerekenler"
    }}
  ]
}}"""

# ============================================================
# PROMPT 4: Mali Özet / Financial Summary
# ============================================================

FINANCIAL_SUMMARY_PROMPT: str = """Aşağıdaki ihale şartname bölümlerinden tüm mali bilgileri çıkar ve analiz et.

Analiz edilecek mali konular:
- Yaklaşık maliyet / İhale bedeli
- Geçici ve kesin teminat miktarları ve türleri
- Ödeme koşulları ve hakediş takvimi
- Avans imkânı ve koşulları
- Fiyat farkı hükümleri (varsa)
- SGK, vergi ve diğer yasal kesintiler
- Damga vergisi ve sözleşme giderleri

4734/4735 sayılı kanunlar kapsamında mali koşulları değerlendir.

Şartname Bölümleri:
{context}

Kesinlikle aşağıdaki JSON formatında yanıt ver:
{{
  "tahmini_ihale_bedeli": "Tutarı veya 'Şartnamede belirtilmemiş'",
  "gecici_teminat": "Geçici teminat bilgisi",
  "kesin_teminat": "Kesin teminat bilgisi",
  "odeme_kosullari": "Ödeme koşulları özeti",
  "avans": {{
    "var_mi": true,
    "oran": "Avans oranı veya 'Şartnamede belirtilmemiş'"
  }},
  "fiyat_farki": {{
    "var_mi": true,
    "aciklama": "Fiyat farkı açıklaması"
  }},
  "hakedis_detaylari": "Hakediş düzeni detayları",
  "mali_riskler": ["Tespit edilen mali riskler"],
  "mali_firsatlar": ["Tespit edilen mali fırsatlar"],
  "oneriler": ["Firma için mali öneriler"]
}}"""

# ============================================================
# PROMPT 5: Süre Analizi / Timeline Analysis
# ============================================================

TIMELINE_ANALYSIS_PROMPT: str = """Aşağıdaki ihale şartname bölümlerinden tüm süre ve takvim bilgilerini çıkar.

Analiz edilecek konular:
- Toplam iş süresi ve başlangıç koşulları
- Yer teslimi ve işe başlama süreci
- Kritik tarihler (ihale, sözleşme, teslim)
- Ara teslimler ve milestone'lar
- Gecikme koşulları ve süre uzatımı hükümleri
- Mücbir sebep ile süre uzatımı kuralları

4735 sayılı Kanun'un süre uzatımı hükümleri açısından değerlendir.

Şartname Bölümleri:
{context}

Kesinlikle aşağıdaki JSON formatında yanıt ver:
{{
  "toplam_is_suresi": "Toplam proje süresi",
  "baslama_tarihi_kosulu": "İşe başlama koşulu (yer teslimi, vb.)",
  "bitis_tarihi_veya_sure": "Bitiş tarihi veya süresi",
  "onemli_tarihler": [
    {{
      "tarih_veya_sure": "Tarih veya süre bilgisi",
      "aciklama": "Bu tarihin/sürenin önemi",
      "madde_referans": "İlgili madde numarası"
    }}
  ],
  "milestones": [
    {{
      "isim": "Milestone adı",
      "sure": "Ne zaman tamamlanmalı",
      "aciklama": "Detay"
    }}
  ],
  "gecikme_riski_degerlendirmesi": "Gecikme riskinin genel değerlendirmesi",
  "oneriler": ["Süre yönetimi için öneriler"]
}}"""

# ============================================================
# PROMPT 6: Yönetici Özeti / Executive Summary
# ============================================================

EXECUTIVE_SUMMARY_PROMPT: str = """Aşağıda bir ihale şartnamesinin farklı açılardan yapılmış analizleri bulunmaktadır.
Bu analizleri birleştirerek firma yönetimine sunulacak kısa ve öz bir yönetici özeti hazırla.

Karar: Bu ihaleye girilmeli mi, girilmemeli mi? Net bir tavsiye ver.

Analiz Sonuçları:
{analysis_results}

Şartname'den Seçilmiş Bölümler:
{context}

Kesinlikle aşağıdaki JSON formatında yanıt ver:
{{
  "ihale_adi": "İhalenin adı veya konusu",
  "tavsiye": "GİR/DİKKATLİ GİR/GİRME",
  "tavsiye_nedeni": "Tavsiyenin kısa gerekçesi",
  "risk_skoru": 0-100,
  "en_kritik_3_bulgu": [
    "En kritik bulgu 1",
    "En kritik bulgu 2",
    "En kritik bulgu 3"
  ],
  "avantajlar": ["Bu ihaleye girmenin avantajları"],
  "dezavantajlar": ["Bu ihaleye girmenin dezavantajları"],
  "sonuc_paragraf": "Yöneticiye özet paragraf - karar destek bilgisi içeren 3-5 cümle"
}}"""


# ============================================================
# Yardımcı Fonksiyonlar / Helper Functions
# ============================================================

# Tüm prompt'ların isim -> şablon eşlemesi
# Name -> template mapping for all prompts
_PROMPT_REGISTRY: dict[str, str] = {
    "risk_analysis": RISK_ANALYSIS_PROMPT,
    "required_documents": REQUIRED_DOCUMENTS_PROMPT,
    "penalty_clauses": PENALTY_CLAUSES_PROMPT,
    "financial_summary": FINANCIAL_SUMMARY_PROMPT,
    "timeline_analysis": TIMELINE_ANALYSIS_PROMPT,
    "executive_summary": EXECUTIVE_SUMMARY_PROMPT,
}

# Analiz sırasında kullanılacak varsayılan RAG sorguları
# Default RAG queries used during analysis
ANALYSIS_QUERIES: dict[str, str] = {
    "risk_analysis": (
        "risk ceza teminat gecikme fesih yaptırım sorumluluk "
        "teknik yeterlilik alt yüklenici mücbir sebep ihtilaf"
    ),
    "required_documents": (
        "belge yeterlilik sertifika referans iş deneyim bilanço "
        "banka teklif mektubu ISO TSE kalite belgesi"
    ),
    "penalty_clauses": (
        "ceza gecikme eksik iş fesih yaptırım kara liste "
        "müeyyide kesinti uygunsuzluk kalite denetim"
    ),
    "financial_summary": (
        "teminat ödeme hakediş fiyat farkı avans bedel bütçe "
        "maliyet damga vergisi SGK kesinti"
    ),
    "timeline_analysis": (
        "süre tarih teslim başlama bitiş yer teslimi gecikme "
        "uzatım mücbir sebep takvim milestone"
    ),
    "executive_summary": (
        "konu kapsam genel değerlendirme risk önemli madde "
        "teminat ceza süre belge yeterlilik"
    ),
}


def get_prompt(prompt_name: str) -> str:
    """
    İsme göre prompt şablonu getir / Get prompt template by name.

    Args:
        prompt_name: Prompt adı / Prompt name
            Geçerli değerler / Valid values:
            - "risk_analysis"
            - "required_documents"
            - "penalty_clauses"
            - "financial_summary"
            - "timeline_analysis"
            - "executive_summary"

    Returns:
        Prompt şablon metni / Prompt template text

    Raises:
        ValueError: Geçersiz prompt adı / Invalid prompt name
    """
    if prompt_name not in _PROMPT_REGISTRY:
        raise ValueError(
            f"Geçersiz prompt adı / Invalid prompt name: {prompt_name}. "
            f"Geçerli değerler / Valid values: {list(_PROMPT_REGISTRY.keys())}"
        )
    return _PROMPT_REGISTRY[prompt_name]


def get_query(analysis_name: str) -> str:
    """
    Analiz tipine göre varsayılan RAG sorgusunu getir.
    Get default RAG query for analysis type.

    Args:
        analysis_name: Analiz adı / Analysis name

    Returns:
        RAG sorgu metni / RAG query text

    Raises:
        ValueError: Geçersiz analiz adı / Invalid analysis name
    """
    if analysis_name not in ANALYSIS_QUERIES:
        raise ValueError(
            f"Geçersiz analiz adı / Invalid analysis name: {analysis_name}. "
            f"Geçerli değerler / Valid values: {list(ANALYSIS_QUERIES.keys())}"
        )
    return ANALYSIS_QUERIES[analysis_name]


def get_all_prompt_names() -> list[str]:
    """Tüm prompt adlarını döndür / Return all prompt names."""
    return list(_PROMPT_REGISTRY.keys())
