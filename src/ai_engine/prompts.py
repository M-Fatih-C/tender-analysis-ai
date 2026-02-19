"""
TenderAI LLM Prompt Şablonları / LLM Prompt Templates.

Tüm yapay zeka analiz prompt'larını içerir.
Contains all AI analysis prompts.

Bu modül Modül 3'te implement edilecektir.
This module will be implemented in Module 3.
"""

# === Risk Analizi Prompt'u / Risk Analysis Prompt ===
RISK_ANALYSIS_PROMPT: str = """
Sen bir ihale teknik şartname analiz uzmanısın.
Aşağıdaki ihale şartname metnini analiz ederek potansiyel riskleri belirle.

Her risk için şunları belirt:
1. İlgili madde numarası
2. Risk açıklaması
3. Risk seviyesi (düşük/orta/yüksek/kritik)
4. Öneri

Şartname Metni:
{document_text}

JSON formatında yanıt ver.
"""

# === Gerekli Belgeler Prompt'u / Required Documents Prompt ===
REQUIRED_DOCUMENTS_PROMPT: str = """
Sen bir ihale belge uzmanısın.
Aşağıdaki ihale şartname metnini analiz ederek,
teklif için sunulması gereken tüm belgeleri listele.

Her belge için:
1. Belge adı
2. Zorunlu mu / İsteğe bağlı mı
3. İlgili madde numarası

Şartname Metni:
{document_text}

JSON formatında yanıt ver.
"""

# === Ceza Maddeleri Prompt'u / Penalty Clauses Prompt ===
PENALTY_CLAUSES_PROMPT: str = """
Sen bir ihale hukuk uzmanısın.
Aşağıdaki ihale şartname metnindeki ceza maddelerini tespit et.

Her ceza maddesi için:
1. Madde numarası
2. Ceza türü (gecikme/eksiklik/uyumsuzluk)
3. Ceza miktarı veya oranı
4. Koşullar

Şartname Metni:
{document_text}

JSON formatında yanıt ver.
"""

# === Mali Özet Prompt'u / Financial Summary Prompt ===
FINANCIAL_SUMMARY_PROMPT: str = """
Sen bir mali analiz uzmanısın.
Aşağıdaki ihale şartname metninden mali bilgileri çıkar.

Şunları belirle:
1. Tahmini bütçe / Yaklaşık maliyet
2. Teminat miktarı ve türü
3. Ödeme koşulları ve takvimi
4. Fiyat farkı hükümleri
5. Diğer mali yükümlülükler

Şartname Metni:
{document_text}

JSON formatında yanıt ver.
"""

# === Süre Analizi Prompt'u / Timeline Analysis Prompt ===
TIMELINE_ANALYSIS_PROMPT: str = """
Sen bir proje planlama uzmanısın.
Aşağıdaki ihale şartname metninden süre bilgilerini çıkar.

Şunları belirle:
1. Toplam proje süresi
2. Önemli kilometre taşları
3. Teslim tarihleri
4. Kritik tarihler (ihale tarihi, teklif son tarihi vb.)
5. Gecikme koşulları

Şartname Metni:
{document_text}

JSON formatında yanıt ver.
"""

# === Genel Analiz Prompt'u / General Analysis Prompt ===
GENERAL_ANALYSIS_PROMPT: str = """
Sen deneyimli bir ihale analiz uzmanısın.
Aşağıdaki ihale teknik şartnamesini kapsamlı olarak analiz et.

Analizin şu bölümleri içermeli:
1. Genel Değerlendirme
2. Risk Analizi
3. Gerekli Belgeler
4. Ceza Maddeleri
5. Mali Özet
6. Süre Analizi
7. Öneriler

Şartname Metni:
{document_text}

JSON formatında yanıt ver.
"""


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
            - "general_analysis"

    Returns:
        Prompt şablon metni / Prompt template text

    Raises:
        ValueError: Geçersiz prompt adı / Invalid prompt name
    """
    prompts: dict[str, str] = {
        "risk_analysis": RISK_ANALYSIS_PROMPT,
        "required_documents": REQUIRED_DOCUMENTS_PROMPT,
        "penalty_clauses": PENALTY_CLAUSES_PROMPT,
        "financial_summary": FINANCIAL_SUMMARY_PROMPT,
        "timeline_analysis": TIMELINE_ANALYSIS_PROMPT,
        "general_analysis": GENERAL_ANALYSIS_PROMPT,
    }

    if prompt_name not in prompts:
        raise ValueError(
            f"Geçersiz prompt adı / Invalid prompt name: {prompt_name}. "
            f"Geçerli değerler / Valid values: {list(prompts.keys())}"
        )

    return prompts[prompt_name]
