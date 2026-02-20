"""
TenderAI İhale Chatbot / Tender Chatbot v2.0.

Analiz edilmiş şartname üzerinden RAG ile soru-cevap yapar.
Yeni google-genai SDK kullanır. Fallback: demo yanıtlar.
"""

import logging
import time

from google import genai
from google.genai import types

from src.utils.demo_data import DEMO_CHAT_RESPONSES

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """Sen Türkiye kamu ihale mevzuatında (4734 ve 4735 sayılı kanunlar) uzman bir ihale danışmanısın.
Sana verilen ihale şartnamesi dokümanına dayanarak soruları yanıtlıyorsun.

KURALLAR:
1. Yanıtlarını SADECE verilen şartname dokümanına dayandır
2. Şartnamede olmayan bilgi için "Bu bilgi şartnamede belirtilmemiştir" de
3. Her yanıtta madde numarası ve sayfa referansı ver
4. Türkçe, profesyonel ve anlaşılır yanıt ver
5. Yanıtı kısa ve öz tut (maksimum 3-4 paragraf)
6. Gerekli yerlerde uyarı/öneri ekle"""

SUGGESTED_QUESTIONS: list[str] = [
    "Bu ihalenin tahmini bedeli nedir?",
    "Teminat mektubu tutarı ne kadar olmalı?",
    "Gecikme cezası nasıl hesaplanıyor?",
    "Alt yüklenici kullanılabilir mi?",
    "İş deneyim belgesi alt limiti nedir?",
    "Avans imkanı var mı?",
    "Hangi sertifikalar gerekli?",
    "Yer teslim süresi ne kadar?",
]


class IhaleChatbot:
    """İhale şartnamesine soru-cevap chatbot."""

    def __init__(self, gemini_api_key: str = "", openai_api_key: str = "") -> None:
        """Init — google-genai SDK veya demo mod."""
        self._context: str = ""
        self._use_ai = False
        self._client = None

        if gemini_api_key and len(gemini_api_key) > 5:
            try:
                self._client = genai.Client(api_key=gemini_api_key)
                self._use_ai = True
                logger.info("Chatbot: Gemini backend aktif (google-genai SDK)")
            except Exception as e:
                logger.warning(f"Chatbot Gemini init hatası: {e}")

    def set_context(self, text: str) -> None:
        """Şartname metnini context olarak ayarla."""
        self._context = text[:30000]
        logger.info(f"Chatbot context set: {len(self._context)} karakter")

    def ask(self, question: str, chat_history: list[dict] | None = None) -> str:
        """Soruyu yanıtla — AI veya demo."""
        if not self._context:
            return "⚠️ Önce bir şartname yükleyin veya geçmiş analizlerden birini seçin."

        if self._use_ai and self._client:
            return self._ask_ai(question, chat_history or [])
        else:
            return self._ask_demo(question)

    def _ask_ai(self, question: str, history: list[dict]) -> str:
        """Gemini ile yanıtla (yeni SDK)."""
        try:
            history_text = ""
            for msg in history[-5:]:
                role = "Kullanıcı" if msg.get("role") == "user" else "Asistan"
                history_text += f"{role}: {msg.get('message', '')}\n"

            prompt = (
                f"{_SYSTEM_PROMPT}\n\n"
                f"---\nŞARTNAME METNİ:\n{self._context[:20000]}\n---\n\n"
            )
            if history_text:
                prompt += f"ÖNCEKİ KONUŞMA:\n{history_text}\n\n"
            prompt += f"KULLANICI SORUSU: {question}\n\nYANIT:"

            # Retry logic for rate limits
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    response = self._client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.2,
                            max_output_tokens=1024,
                        ),
                    )
                    return response.text or "Yanıt alınamadı."
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        if attempt < max_retries:
                            wait = 30 * (attempt + 1)
                            logger.warning(f"Gemini rate limit, {wait}s bekleniyor... (deneme {attempt + 1})")
                            time.sleep(wait)
                            continue
                        else:
                            logger.warning("Gemini rate limit aşıldı, demo yanıt kullanılıyor")
                            return f"⚠️ AI kota limiti aşıldı. Demo yanıt:\n\n{self._ask_demo(question)}"
                    raise

        except Exception as e:
            logger.error(f"Chatbot AI hatası: {e}")
            return f"⚠️ AI hatası oluştu. Demo yanıt kullanılıyor.\n\n{self._ask_demo(question)}"

    def _ask_demo(self, question: str) -> str:
        """Anahtar kelime eşleşmesi ile demo yanıt."""
        q = question.lower()
        for key, response in DEMO_CHAT_RESPONSES.items():
            if key in q:
                return response
        return DEMO_CHAT_RESPONSES["default"]

    def get_suggested_questions(self) -> list[str]:
        """Önerilen soruları döndür."""
        return list(SUGGESTED_QUESTIONS)
