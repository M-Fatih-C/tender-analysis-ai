"""
TenderAI Gemini AI Analiz Motoru / Gemini AI Analysis Engine.

Google Gemini API kullanarak ihale şartname analizi yapar.
Aynı prompt şablonlarını kullanır, OpenAI yerine Gemini çağırır.

Uses Google Gemini API for tender specification analysis.
Same prompts, different LLM backend.
"""

import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime

import google.generativeai as genai

from src.ai_engine.prompts import (
    RISK_ANALYSIS_PROMPT,
    REQUIRED_DOCUMENTS_PROMPT,
    PENALTY_CLAUSES_PROMPT,
    FINANCIAL_SUMMARY_PROMPT,
    TIMELINE_ANALYSIS_PROMPT,
    EXECUTIVE_SUMMARY_PROMPT,
)

logger = logging.getLogger(__name__)


class GeminiAnalizAI:
    """
    Gemini tabanlı ihale şartname analiz motoru.
    Gemini-based tender specification analysis engine.

    ParsedDocument alır, 6 analiz yapar, sonuçları dict olarak döner.
    """

    def __init__(
        self,
        gemini_api_key: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.1,
    ) -> None:
        """
        GeminiAnalizAI başlat / Initialize GeminiAnalizAI.

        Args:
            gemini_api_key: Google Gemini API anahtarı
            model: Gemini model adı
            temperature: Yanıt sıcaklığı
        """
        genai.configure(api_key=gemini_api_key)
        self._model = genai.GenerativeModel(model)
        self._temperature = temperature
        self._total_tokens = 0
        logger.info(f"GeminiAnalizAI başlatıldı: model={model}")

    def analyze(self, parsed_document) -> dict:
        """
        Ana analiz pipeline. ParsedDocument alır, dict döner.

        Args:
            parsed_document: PDF parser'dan gelen doküman

        Returns:
            Tam analiz sonucu dict
        """
        start_time = time.time()
        text = parsed_document.full_text or ""

        if not text.strip():
            raise ValueError("Doküman metni boş / Document text is empty")

        # Metnin ilk 30K karakterini kullan (token limiti için)
        context = text[:30000]

        logger.info("Gemini analiz başlıyor / Starting Gemini analysis")

        # 6 analiz adımı
        risk = self._analyze_step("risk_analysis", RISK_ANALYSIS_PROMPT, context)
        docs = self._analyze_step("required_documents", REQUIRED_DOCUMENTS_PROMPT, context)
        penalties = self._analyze_step("penalty_clauses", PENALTY_CLAUSES_PROMPT, context)
        financial = self._analyze_step("financial_summary", FINANCIAL_SUMMARY_PROMPT, context)
        timeline = self._analyze_step("timeline_analysis", TIMELINE_ANALYSIS_PROMPT, context)

        # Executive summary — önceki sonuçları da içerir
        summary_context = (
            f"ÖNCEKİ ANALİZLER:\n"
            f"Risk Analizi: {json.dumps(risk, ensure_ascii=False)[:2000]}\n"
            f"Mali Özet: {json.dumps(financial, ensure_ascii=False)[:1000]}\n\n"
            f"ŞARTNAME METNİ:\n{context[:10000]}"
        )
        executive = self._analyze_step("executive_summary", EXECUTIVE_SUMMARY_PROMPT, summary_context)

        # Risk skoru hesapla
        risk_score = self._calculate_risk_score(risk)
        risk_level = self._score_to_level(risk_score)

        elapsed = time.time() - start_time

        result = {
            "risk_analysis": risk,
            "required_documents": docs,
            "penalty_clauses": penalties,
            "financial_summary": financial,
            "timeline_analysis": timeline,
            "executive_summary": executive,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "tokens_used": self._total_tokens,
            "cost_usd": 0.0,  # Gemini ücretsiz tier
            "analysis_time": round(elapsed, 1),
            "model_used": "gemini",
        }

        logger.info(
            f"Gemini analiz tamamlandı: risk={risk_score}, süre={elapsed:.1f}s"
        )
        return result

    def _analyze_step(self, name: str, prompt: str, context: str) -> dict:
        """Tek analiz adımı — Gemini'ye gönder, JSON parse et."""
        try:
            full_prompt = (
                f"{prompt}\n\n"
                f"---\nŞARTNAME METNİ:\n{context}\n---\n\n"
                f"Yanıtını SADECE geçerli JSON formatında ver. "
                f"Başka açıklama ekleme."
            )

            response = self._model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self._temperature,
                    max_output_tokens=4096,
                ),
            )

            raw = response.text or ""
            self._total_tokens += len(raw.split()) * 2  # Yaklaşık token tahmini

            return self._parse_json(raw)

        except Exception as e:
            logger.error(f"Gemini {name} hatası: {e}")
            return {}

    def _parse_json(self, text: str) -> dict:
        """LLM yanıtından JSON çıkar."""
        # Direkt dene
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # ```json ... ``` bloğu
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # İlk { ... son } arası
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass

        logger.warning("JSON parse edilemedi, boş dict döndürülüyor")
        return {}

    def _calculate_risk_score(self, risk_data: dict) -> int:
        """Risk skorunu hesapla."""
        try:
            # Direkt skor varsa kullan
            score = risk_data.get("risk_skoru")
            if score is not None and isinstance(score, (int, float)):
                return max(0, min(100, int(score)))

            # Riskleri say
            riskler = risk_data.get("riskler", [])
            if not riskler:
                return 30

            weights = {"KRİTİK": 25, "YÜKSEK": 18, "ORTA": 10, "DÜŞÜK": 5}
            total = sum(
                weights.get(r.get("seviye", "ORTA").upper(), 10)
                for r in riskler if isinstance(r, dict)
            )
            return max(0, min(100, total))
        except Exception:
            return 50

    @staticmethod
    def _score_to_level(score: int) -> str:
        """Skor → seviye."""
        if score <= 30:
            return "DÜŞÜK"
        elif score <= 50:
            return "ORTA"
        elif score <= 70:
            return "YÜKSEK"
        else:
            return "ÇOK YÜKSEK"
