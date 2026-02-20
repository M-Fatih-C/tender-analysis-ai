"""
TenderAI AI Analiz Motoru / AI Analysis Engine.

RAG (Retrieval-Augmented Generation) + LLM (GPT-4) kullanarak
ihale teknik ve idari şartnamelerini analiz eder.

Uses RAG (Retrieval-Augmented Generation) + LLM (GPT-4)
to analyze tender technical and administrative specifications.

Pipeline:
    PDF Metin → Chunk → Embedding → FAISS Vektör DB
                                        ↓
    Sorgu → Embedding → Benzer chunk bul → LLM → Analiz sonucu
"""

import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import tiktoken

from src.ai_engine.prompts import (
    SYSTEM_ROLE,
    get_prompt,
    get_query,
    get_all_prompt_names,
    EXECUTIVE_SUMMARY_PROMPT,
)
from src.pdf_parser.parser import ParsedDocument

logger = logging.getLogger(__name__)


# ============================================================
# Dataclass Tanımları / Dataclass Definitions
# ============================================================


@dataclass
class AnalysisResult:
    """
    Tam analiz sonucu / Full analysis result.

    Attributes:
        risk_analysis: Risk analizi JSON sonucu / Risk analysis JSON result
        required_documents: Gerekli belgeler JSON sonucu / Required documents JSON result
        penalty_clauses: Ceza maddeleri JSON sonucu / Penalty clauses JSON result
        financial_summary: Mali özet JSON sonucu / Financial summary JSON result
        timeline_analysis: Süre analizi JSON sonucu / Timeline analysis JSON result
        executive_summary: Yönetici özeti JSON sonucu / Executive summary JSON result
        risk_score: Genel risk skoru 0-100 / Overall risk score 0-100
        risk_level: Risk seviyesi / Risk level (DÜŞÜK/ORTA/YÜKSEK/ÇOK YÜKSEK)
        analysis_time_seconds: Toplam analiz süresi / Total analysis time
        total_tokens_used: Kullanılan toplam token / Total tokens used
        estimated_cost_usd: Tahmini maliyet (USD) / Estimated cost (USD)
        analyzed_at: Analiz zamanı / Analysis timestamp
    """

    risk_analysis: dict = field(default_factory=dict)
    required_documents: dict = field(default_factory=dict)
    penalty_clauses: dict = field(default_factory=dict)
    financial_summary: dict = field(default_factory=dict)
    timeline_analysis: dict = field(default_factory=dict)
    executive_summary: dict = field(default_factory=dict)
    risk_score: int = 0
    risk_level: str = "DÜŞÜK"
    analysis_time_seconds: float = 0.0
    total_tokens_used: int = 0
    estimated_cost_usd: float = 0.0
    analyzed_at: datetime = field(default_factory=datetime.now)


# ============================================================
# Token Fiyatları / Token Pricing (GPT-4o)
# ============================================================

# USD per 1K tokens (GPT-4o pricing)
_INPUT_COST_PER_1K: float = 0.005
_OUTPUT_COST_PER_1K: float = 0.015


# ============================================================
# IhaleAnalizAI Sınıfı / IhaleAnalizAI Class
# ============================================================


class IhaleAnalizAI:
    """
    RAG tabanlı ihale şartname analiz motoru.
    RAG-based tender specification analysis engine.

    PDF parse edilmiş dokümanı alır, 6 farklı analiz yapar:
    Takes a parsed PDF document and performs 6 different analyses:
        1. Risk Analizi / Risk Analysis
        2. Gerekli Belgeler / Required Documents
        3. Ceza Maddeleri / Penalty Clauses
        4. Mali Özet / Financial Summary
        5. Süre Analizi / Timeline Analysis
        6. Yönetici Özeti / Executive Summary
    """

    def __init__(
        self,
        openai_api_key: str,
        model: str = "gpt-4o",
        temperature: float = 0.1,
        chunk_size: int = 1500,
        chunk_overlap: int = 200,
        top_k: int = 15,
    ) -> None:
        """
        IhaleAnalizAI başlat / Initialize IhaleAnalizAI.

        Args:
            openai_api_key: OpenAI API anahtarı / OpenAI API key
            model: LLM model adı / LLM model name
            temperature: LLM sıcaklık / LLM temperature (düşük = deterministik)
            chunk_size: Metin parça boyutu / Text chunk size (karakter)
            chunk_overlap: Parça örtüşme miktarı / Chunk overlap (karakter)
            top_k: RAG'da çekilecek en alakalı parça sayısı / Top-K retrieval count
        """
        self.api_key = openai_api_key
        self.model = model
        self.temperature = temperature
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k

        # Token takibi / Token tracking
        self._total_input_tokens: int = 0
        self._total_output_tokens: int = 0

        # LLM ve Embedding başlat / Initialize LLM and Embeddings
        self._llm = ChatOpenAI(
            api_key=openai_api_key,
            model=model,
            temperature=temperature,
            max_tokens=4096,
        )
        self._embeddings = OpenAIEmbeddings(api_key=openai_api_key)

        # Metin bölücü — ihale şartname yapısına uygun separator'lar
        # Text splitter — separators suited for tender specification structure
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\nMadde ",
                "\nMADDE ",
                "\nBÖLÜM ",
                "\nBölüm ",
                "\nEK-",
                "\nEk ",
                "\n\n",
                "\n",
                " ",
            ],
        )

        # tiktoken encoder (token sayımı için)
        try:
            self._encoder = tiktoken.encoding_for_model(model)
        except KeyError:
            self._encoder = tiktoken.get_encoding("cl100k_base")

        logger.info(
            f"IhaleAnalizAI başlatıldı / initialized: model={model}, "
            f"chunk_size={chunk_size}, top_k={top_k}"
        )

    # ----------------------------------------------------------
    # Vektör Store Oluşturma / Vector Store Creation
    # ----------------------------------------------------------

    def create_vector_store(self, text: str) -> FAISS:
        """
        Metni chunk'la ve in-memory FAISS vektör DB oluştur.
        Chunk text and create in-memory FAISS vector store.

        Args:
            text: Doküman metni / Document text

        Returns:
            FAISS vektör store / FAISS vector store

        Raises:
            ValueError: Metin boş olduğunda / When text is empty
        """
        if not text or not text.strip():
            raise ValueError("Vektör store için metin boş olamaz / Text cannot be empty for vector store")

        logger.info("Metin chunk'lanıyor / Chunking text...")
        chunks = self._splitter.split_text(text)
        logger.info(f"{len(chunks)} chunk oluşturuldu / chunks created")

        logger.info("FAISS vektör store oluşturuluyor / Creating FAISS vector store...")
        vector_store = FAISS.from_texts(texts=chunks, embedding=self._embeddings)
        logger.info("Vektör store hazır / Vector store ready")

        return vector_store

    # ----------------------------------------------------------
    # RAG Sorgusu / RAG Query
    # ----------------------------------------------------------

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=lambda retry_state: logger.warning(
            f"Yeniden deneniyor / Retrying: attempt {retry_state.attempt_number}"
        ),
    )
    def _query_with_prompt(
        self,
        vector_store: FAISS,
        prompt_template: str,
        query: str,
        extra_context: str = "",
    ) -> str:
        """
        RAG sorgusu yap — ilgili chunk'ları bul + LLM'e gönder.
        Perform RAG query — find relevant chunks + send to LLM.

        Args:
            vector_store: FAISS vektör store
            prompt_template: Prompt şablonu / Prompt template
            query: Arama sorgusu / Search query
            extra_context: Ek bağlam (executive summary için) / Extra context

        Returns:
            LLM yanıtı (raw string) / LLM response (raw string)
        """
        # En alakalı chunk'ları çek / Retrieve most relevant chunks
        docs = vector_store.similarity_search(query, k=self.top_k)
        context = "\n\n---\n\n".join(doc.page_content for doc in docs)

        # Prompt'u doldur / Fill prompt template
        if "{analysis_results}" in prompt_template:
            filled_prompt = prompt_template.format(
                context=context,
                analysis_results=extra_context,
            )
        else:
            filled_prompt = prompt_template.format(context=context)

        # Token sayısını hesapla / Calculate token count
        input_tokens = self._count_tokens(SYSTEM_ROLE + filled_prompt)
        logger.info(f"LLM'e gönderiliyor / Sending to LLM: ~{input_tokens} input tokens")

        # LLM çağrısı / LLM call
        messages = [
            {"role": "system", "content": SYSTEM_ROLE},
            {"role": "user", "content": filled_prompt},
        ]
        response = self._llm.invoke(messages)

        # Token takibi / Track tokens
        output_tokens = self._count_tokens(response.content)
        self._total_input_tokens += input_tokens
        self._total_output_tokens += output_tokens
        logger.info(f"LLM yanıtı alındı / Response received: ~{output_tokens} output tokens")

        return response.content

    # ----------------------------------------------------------
    # JSON Parse / JSON Parsing
    # ----------------------------------------------------------

    def _parse_json_response(self, response: str) -> dict:
        """
        LLM yanıtından JSON çıkar. Hatalı JSON'ı düzeltmeye çalışır.
        Extract JSON from LLM response. Tries to fix malformed JSON.

        Args:
            response: LLM ham yanıtı / LLM raw response

        Returns:
            Parse edilmiş JSON dict / Parsed JSON dict
        """
        if not response:
            logger.warning("Boş LLM yanıtı / Empty LLM response")
            return {}

        # 1. Doğrudan JSON parse dene / Try direct JSON parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 2. JSON bloğunu regex ile çıkar / Extract JSON block with regex
        # ```json ... ``` veya { ... } kalıpları
        json_patterns = [
            re.compile(r"```json\s*(.*?)\s*```", re.DOTALL),
            re.compile(r"```\s*(.*?)\s*```", re.DOTALL),
            re.compile(r"(\{.*\})", re.DOTALL),
        ]

        for pattern in json_patterns:
            match = pattern.search(response)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue

        # 3. Hatalı JSON düzeltme denemeleri / Attempt to fix malformed JSON
        # Trailing comma kaldır
        cleaned = re.sub(r",\s*([}\]])", r"\1", response)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        logger.error(
            "JSON parse edilemedi / Could not parse JSON. "
            f"Yanıt başlangıcı / Response start: {response[:200]}"
        )
        return {"raw_response": response, "parse_error": True}

    # ----------------------------------------------------------
    # Ana Analiz Pipeline / Main Analysis Pipeline
    # ----------------------------------------------------------

    async def analyze(self, parsed_document: ParsedDocument) -> AnalysisResult:
        """
        Ana analiz pipeline. ParsedDocument alır, tam analiz döner.
        Main analysis pipeline. Takes ParsedDocument, returns full analysis.

        Adımlar / Steps:
            1. Vektör store oluştur / Create vector store
            2. 6 analizi sırayla çalıştır / Run 6 analyses sequentially
            3. Risk skoru hesapla / Calculate risk score
            4. Sonuçları birleştir / Combine results

        Args:
            parsed_document: PDF parser'dan gelen doküman / Document from PDF parser

        Returns:
            AnalysisResult: Tam analiz sonucu / Full analysis result
        """
        start_time = time.time()
        self._total_input_tokens = 0
        self._total_output_tokens = 0

        logger.info("=" * 60)
        logger.info("İHALE ANALİZİ BAŞLIYOR / TENDER ANALYSIS STARTING")
        logger.info("=" * 60)

        # 1. Vektör store oluştur / Create vector store
        text = parsed_document.full_text
        if not text or not text.strip():
            logger.warning("Doküman metni boş / Document text is empty")
            return AnalysisResult(analyzed_at=datetime.now())

        vector_store = self.create_vector_store(text)

        # 2. Analizleri sırayla çalıştır (rate limit'e dikkat)
        # Run analyses sequentially (respecting rate limits)
        logger.info("1/6 Risk analizi başlıyor / Risk analysis starting...")
        risk_result = await self.risk_analysis(vector_store)

        logger.info("2/6 Gerekli belgeler analizi / Required documents analysis...")
        docs_result = await self.required_documents(vector_store)

        logger.info("3/6 Ceza maddeleri analizi / Penalty clauses analysis...")
        penalty_result = await self.penalty_clauses(vector_store)

        logger.info("4/6 Mali özet analizi / Financial summary analysis...")
        financial_result = await self.financial_summary(vector_store)

        logger.info("5/6 Süre analizi / Timeline analysis...")
        timeline_result = await self.timeline_analysis(vector_store)

        # 6. Yönetici özeti — diğer tüm sonuçları bağlam olarak alır
        # Executive summary — uses all other results as context
        logger.info("6/6 Yönetici özeti / Executive summary...")
        all_results = {
            "risk_analysis": risk_result,
            "required_documents": docs_result,
            "penalty_clauses": penalty_result,
            "financial_summary": financial_result,
            "timeline_analysis": timeline_result,
        }
        executive_result = await self.executive_summary(vector_store, all_results)

        # 3. Risk skoru hesapla / Calculate risk score
        risk_score = self.calculate_risk_score(all_results)
        risk_level = self._score_to_level(risk_score)

        # 4. Sonuçları birleştir / Combine results
        elapsed = time.time() - start_time
        total_tokens = self._total_input_tokens + self._total_output_tokens
        estimated_cost = (
            (self._total_input_tokens / 1000) * _INPUT_COST_PER_1K
            + (self._total_output_tokens / 1000) * _OUTPUT_COST_PER_1K
        )

        result = AnalysisResult(
            risk_analysis=risk_result,
            required_documents=docs_result,
            penalty_clauses=penalty_result,
            financial_summary=financial_result,
            timeline_analysis=timeline_result,
            executive_summary=executive_result,
            risk_score=risk_score,
            risk_level=risk_level,
            analysis_time_seconds=round(elapsed, 2),
            total_tokens_used=total_tokens,
            estimated_cost_usd=round(estimated_cost, 4),
            analyzed_at=datetime.now(),
        )

        logger.info("=" * 60)
        logger.info(
            f"ANALİZ TAMAMLANDI / ANALYSIS COMPLETED: "
            f"risk_score={risk_score}, tokens={total_tokens}, "
            f"cost=${estimated_cost:.4f}, time={elapsed:.1f}s"
        )
        logger.info("=" * 60)

        return result

    # ----------------------------------------------------------
    # Bireysel Analiz Metodları / Individual Analysis Methods
    # ----------------------------------------------------------

    async def risk_analysis(self, vector_store: FAISS) -> dict:
        """
        Risk analizi yap / Perform risk analysis.

        Args:
            vector_store: FAISS vektör store

        Returns:
            Risk analizi sonucu / Risk analysis result
        """
        try:
            prompt = get_prompt("risk_analysis")
            query = get_query("risk_analysis")
            response = self._query_with_prompt(vector_store, prompt, query)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Risk analizi hatası / Risk analysis error: {e}", exc_info=True)
            return {"error": str(e)}

    async def required_documents(self, vector_store: FAISS) -> dict:
        """
        Gerekli belge analizi yap / Perform required documents analysis.

        Args:
            vector_store: FAISS vektör store

        Returns:
            Gerekli belgeler sonucu / Required documents result
        """
        try:
            prompt = get_prompt("required_documents")
            query = get_query("required_documents")
            response = self._query_with_prompt(vector_store, prompt, query)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Belge analizi hatası / Document analysis error: {e}", exc_info=True)
            return {"error": str(e)}

    async def penalty_clauses(self, vector_store: FAISS) -> dict:
        """
        Ceza maddeleri analizi yap / Perform penalty clauses analysis.

        Args:
            vector_store: FAISS vektör store

        Returns:
            Ceza maddeleri sonucu / Penalty clauses result
        """
        try:
            prompt = get_prompt("penalty_clauses")
            query = get_query("penalty_clauses")
            response = self._query_with_prompt(vector_store, prompt, query)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Ceza analizi hatası / Penalty analysis error: {e}", exc_info=True)
            return {"error": str(e)}

    async def financial_summary(self, vector_store: FAISS) -> dict:
        """
        Mali özet analizi yap / Perform financial summary analysis.

        Args:
            vector_store: FAISS vektör store

        Returns:
            Mali özet sonucu / Financial summary result
        """
        try:
            prompt = get_prompt("financial_summary")
            query = get_query("financial_summary")
            response = self._query_with_prompt(vector_store, prompt, query)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Mali analiz hatası / Financial analysis error: {e}", exc_info=True)
            return {"error": str(e)}

    async def timeline_analysis(self, vector_store: FAISS) -> dict:
        """
        Süre analizi yap / Perform timeline analysis.

        Args:
            vector_store: FAISS vektör store

        Returns:
            Süre analizi sonucu / Timeline analysis result
        """
        try:
            prompt = get_prompt("timeline_analysis")
            query = get_query("timeline_analysis")
            response = self._query_with_prompt(vector_store, prompt, query)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Süre analizi hatası / Timeline analysis error: {e}", exc_info=True)
            return {"error": str(e)}

    async def executive_summary(self, vector_store: FAISS, all_results: dict) -> dict:
        """
        Yönetici özeti oluştur — diğer tüm sonuçları kullanarak.
        Create executive summary — using all other analysis results.

        Args:
            vector_store: FAISS vektör store
            all_results: Diğer 5 analizin sonuçları / Results of other 5 analyses

        Returns:
            Yönetici özeti sonucu / Executive summary result
        """
        try:
            prompt = get_prompt("executive_summary")
            query = get_query("executive_summary")

            # Diğer sonuçları bağlam olarak formatla
            # Format other results as context
            results_text = json.dumps(all_results, ensure_ascii=False, indent=2, default=str)
            # Çok uzunsa kes / Truncate if too long
            max_results_len = 8000
            if len(results_text) > max_results_len:
                results_text = results_text[:max_results_len] + "\n... (kısaltıldı / truncated)"

            response = self._query_with_prompt(
                vector_store, prompt, query, extra_context=results_text
            )
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Yönetici özeti hatası / Executive summary error: {e}", exc_info=True)
            return {"error": str(e)}

    # ----------------------------------------------------------
    # Risk Skoru Hesaplama / Risk Score Calculation
    # ----------------------------------------------------------

    def calculate_risk_score(self, all_results: dict) -> int:
        """
        Ağırlıklı ortalama ile 0-100 arası risk skoru hesapla.
        Calculate 0-100 risk score using weighted average.

        Ağırlıklar / Weights:
            - Ceza maddeleri / Penalty clauses: %30
            - Mali riskler / Financial risks: %25
            - Süre riskleri / Timeline risks: %20
            - Teknik riskler / Technical risks: %15
            - Belge eksiklikleri / Document gaps: %10

        Args:
            all_results: Tüm analiz sonuçları / All analysis results

        Returns:
            Risk skoru (0-100) / Risk score (0-100)
        """
        try:
            scores: dict[str, float] = {}

            # Ceza skoru — ceza sayısı ve şiddetine göre
            # Penalty score — based on count and severity
            penalty_data = all_results.get("penalty_clauses", {})
            scores["penalty"] = self._score_from_severity_list(
                penalty_data.get("cezalar", []),
                severity_key="risk_seviyesi",
            )

            # Mali risk skoru
            financial_data = all_results.get("financial_summary", {})
            mali_riskler = financial_data.get("mali_riskler", [])
            scores["financial"] = min(100, len(mali_riskler) * 20) if mali_riskler else 25

            # Süre risk skoru
            timeline_data = all_results.get("timeline_analysis", {})
            gecikme = timeline_data.get("gecikme_riski_degerlendirmesi", "")
            scores["timeline"] = self._score_from_text_severity(gecikme)

            # Risk analizi skoru — doğrudan risk_skoru alanını kullan
            risk_data = all_results.get("risk_analysis", {})
            if "risk_skoru" in risk_data:
                try:
                    scores["technical"] = int(risk_data["risk_skoru"])
                except (ValueError, TypeError):
                    scores["technical"] = self._score_from_severity_list(
                        risk_data.get("riskler", []),
                        severity_key="seviye",
                    )
            else:
                scores["technical"] = self._score_from_severity_list(
                    risk_data.get("riskler", []),
                    severity_key="seviye",
                )

            # Belge skoru — belge sayısına göre
            docs_data = all_results.get("required_documents", {})
            zorunlu = docs_data.get("zorunlu_belgeler", [])
            uyarilar = docs_data.get("onemli_uyarilar", [])
            scores["documents"] = min(100, len(zorunlu) * 3 + len(uyarilar) * 15)

            # Ağırlıklı ortalama / Weighted average
            weights = {
                "penalty": 0.30,
                "financial": 0.25,
                "timeline": 0.20,
                "technical": 0.15,
                "documents": 0.10,
            }

            weighted_score = sum(
                scores.get(k, 30) * w for k, w in weights.items()
            )

            final_score = max(0, min(100, int(round(weighted_score))))
            logger.info(
                f"Risk skoru hesaplandı / Risk score calculated: {final_score} "
                f"(detay / detail: {scores})"
            )
            return final_score

        except Exception as e:
            logger.error(f"Risk skoru hesaplama hatası / Risk score error: {e}", exc_info=True)
            return 50  # Hata durumunda orta skor / Default middle score on error

    # ----------------------------------------------------------
    # Dahili Yardımcı Metodlar / Internal Helper Methods
    # ----------------------------------------------------------

    def _count_tokens(self, text: str) -> int:
        """Token sayısını hesapla / Count tokens."""
        try:
            return len(self._encoder.encode(text))
        except Exception:
            # Yaklaşık hesaplama / Approximate calculation
            return len(text) // 4

    def _score_from_severity_list(
        self,
        items: list,
        severity_key: str = "risk_seviyesi",
    ) -> float:
        """
        Şiddet listesinden skor hesapla / Calculate score from severity list.

        Args:
            items: Risk/ceza listesi / List of risks/penalties
            severity_key: Şiddet alanı adı / Severity field name

        Returns:
            Hesaplanan skor (0-100) / Calculated score
        """
        if not items:
            return 20  # Veri yoksa düşük skor / Low score when no data

        severity_scores = {
            "düşük": 15,
            "DÜŞÜK": 15,
            "orta": 40,
            "ORTA": 40,
            "yüksek": 70,
            "YÜKSEK": 70,
            "kritik": 95,
            "KRİTİK": 95,
        }

        total = 0
        for item in items:
            if isinstance(item, dict):
                severity = item.get(severity_key, "ORTA")
                total += severity_scores.get(severity, 40)
            else:
                total += 40

        avg = total / len(items)
        # Çok sayıda risk/ceza varsa skoru artır / Increase score for many items
        count_bonus = min(20, len(items) * 3)
        return min(100, avg + count_bonus)

    def _score_from_text_severity(self, text: str) -> float:
        """Metin içeriğinden skor tahmin et / Estimate score from text content."""
        if not text:
            return 30

        text_lower = text.lower()
        if any(w in text_lower for w in ["çok yüksek", "kritik", "tehlikeli"]):
            return 85
        elif any(w in text_lower for w in ["yüksek", "riskli", "dikkat"]):
            return 65
        elif any(w in text_lower for w in ["orta", "makul"]):
            return 45
        elif any(w in text_lower for w in ["düşük", "uygun", "sorunsuz"]):
            return 25
        return 40

    @staticmethod
    def _score_to_level(score: int) -> str:
        """
        Sayısal skoru risk seviyesine çevir / Convert numeric score to risk level.

        Args:
            score: Risk skoru (0-100) / Risk score

        Returns:
            Risk seviyesi / Risk level
        """
        if score <= 25:
            return "DÜŞÜK"
        elif score <= 50:
            return "ORTA"
        elif score <= 75:
            return "YÜKSEK"
        else:
            return "ÇOK YÜKSEK"
