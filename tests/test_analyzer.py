"""
TenderAI AI Analiz Motoru Testleri / AI Analysis Engine Tests.

IhaleAnalizAI sınıfı, prompt'lar ve yardımcı fonksiyonlar için birim testleri.
Unit tests for IhaleAnalizAI class, prompts, and helper functions.

Mock OpenAI API kullanarak test eder — gerçek API çağrısı yapmaz.
Tests using Mock OpenAI API — no real API calls are made.
"""

import json
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock

from src.ai_engine.analyzer import IhaleAnalizAI, AnalysisResult
from src.ai_engine.prompts import (
    get_prompt,
    get_query,
    get_all_prompt_names,
    SYSTEM_ROLE,
    RISK_ANALYSIS_PROMPT,
    REQUIRED_DOCUMENTS_PROMPT,
    PENALTY_CLAUSES_PROMPT,
    FINANCIAL_SUMMARY_PROMPT,
    TIMELINE_ANALYSIS_PROMPT,
    EXECUTIVE_SUMMARY_PROMPT,
    _PROMPT_REGISTRY,
    ANALYSIS_QUERIES,
)
from src.pdf_parser.parser import ParsedDocument, PageContent, DocumentMetadata


# ============================================================
# Prompt Testleri / Prompt Tests
# ============================================================


class TestPrompts:
    """Prompt şablon testleri / Prompt template tests."""

    def test_all_prompts_exist(self) -> None:
        """Tüm 6 prompt tanımlı olmalı / All 6 prompts should be defined."""
        expected = [
            "risk_analysis",
            "required_documents",
            "penalty_clauses",
            "financial_summary",
            "timeline_analysis",
            "executive_summary",
        ]
        for name in expected:
            prompt = get_prompt(name)
            assert isinstance(prompt, str)
            assert len(prompt) > 100  # Anlamlı uzunlukta olmalı

    def test_get_prompt_invalid_name(self) -> None:
        """Geçersiz prompt adı ValueError fırlatmalı / Invalid name should raise ValueError."""
        with pytest.raises(ValueError, match="Geçersiz prompt adı"):
            get_prompt("nonexistent_prompt")

    def test_all_prompts_have_context_placeholder(self) -> None:
        """Tüm prompt'lar {context} placeholder içermeli / All should contain {context}."""
        for name in get_all_prompt_names():
            prompt = get_prompt(name)
            assert "{context}" in prompt, f"'{name}' prompt'unda {{context}} yok"

    def test_risk_prompt_has_json_structure(self) -> None:
        """Risk prompt'u JSON yapısı göstermeli / Should show JSON structure."""
        assert "genel_risk_seviyesi" in RISK_ANALYSIS_PROMPT
        assert "riskler" in RISK_ANALYSIS_PROMPT
        assert "risk_skoru" in RISK_ANALYSIS_PROMPT

    def test_documents_prompt_has_categories(self) -> None:
        """Belge prompt'u kategorileri içermeli / Should contain categories."""
        assert "zorunlu_belgeler" in REQUIRED_DOCUMENTS_PROMPT
        assert "istege_bagli_belgeler" in REQUIRED_DOCUMENTS_PROMPT

    def test_penalty_prompt_has_structure(self) -> None:
        """Ceza prompt'u yapısı doğru olmalı / Should have correct structure."""
        assert "cezalar" in PENALTY_CLAUSES_PROMPT
        assert "ceza_turu" in PENALTY_CLAUSES_PROMPT

    def test_financial_prompt_has_structure(self) -> None:
        """Mali prompt yapısı doğru olmalı / Should have correct structure."""
        assert "tahmini_ihale_bedeli" in FINANCIAL_SUMMARY_PROMPT
        assert "gecici_teminat" in FINANCIAL_SUMMARY_PROMPT

    def test_timeline_prompt_has_structure(self) -> None:
        """Süre prompt yapısı doğru olmalı / Should have correct structure."""
        assert "toplam_is_suresi" in TIMELINE_ANALYSIS_PROMPT
        assert "milestones" in TIMELINE_ANALYSIS_PROMPT

    def test_executive_prompt_has_analysis_results(self) -> None:
        """Yönetici prompt'u {analysis_results} içermeli / Should contain {analysis_results}."""
        assert "{analysis_results}" in EXECUTIVE_SUMMARY_PROMPT
        assert "tavsiye" in EXECUTIVE_SUMMARY_PROMPT

    def test_system_role_is_defined(self) -> None:
        """System role tanımlı ve anlamlı olmalı / Should be defined and meaningful."""
        assert isinstance(SYSTEM_ROLE, str)
        assert "ihale" in SYSTEM_ROLE.lower()
        assert "4734" in SYSTEM_ROLE
        assert "JSON" in SYSTEM_ROLE

    def test_get_all_prompt_names(self) -> None:
        """get_all_prompt_names 6 isim döndürmeli / Should return 6 names."""
        names = get_all_prompt_names()
        assert len(names) == 6
        assert "risk_analysis" in names
        assert "executive_summary" in names


class TestAnalysisQueries:
    """RAG sorgu testleri / RAG query tests."""

    def test_all_queries_exist(self) -> None:
        """Tüm analiz sorguları tanımlı olmalı / All analysis queries should exist."""
        for name in get_all_prompt_names():
            query = get_query(name)
            assert isinstance(query, str)
            assert len(query) > 10

    def test_get_query_invalid_name(self) -> None:
        """Geçersiz sorgu adı ValueError fırlatmalı / Invalid name should raise ValueError."""
        with pytest.raises(ValueError):
            get_query("nonexistent_query")

    def test_risk_query_has_keywords(self) -> None:
        """Risk sorgusu ilgili anahtar kelimeler içermeli / Should contain relevant keywords."""
        query = get_query("risk_analysis")
        assert "risk" in query
        assert "ceza" in query


# ============================================================
# AnalysisResult Dataclass Testleri
# ============================================================


class TestAnalysisResult:
    """AnalysisResult dataclass testleri / AnalysisResult tests."""

    def test_defaults(self) -> None:
        """Varsayılan değerler doğru olmalı / Default values should be correct."""
        result = AnalysisResult()
        assert result.risk_analysis == {}
        assert result.required_documents == {}
        assert result.penalty_clauses == {}
        assert result.financial_summary == {}
        assert result.timeline_analysis == {}
        assert result.executive_summary == {}
        assert result.risk_score == 0
        assert result.risk_level == "DÜŞÜK"
        assert result.total_tokens_used == 0
        assert result.estimated_cost_usd == 0.0
        assert isinstance(result.analyzed_at, datetime)

    def test_creation_with_values(self) -> None:
        """Değerlerle oluşturma / Creation with values."""
        result = AnalysisResult(
            risk_score=72,
            risk_level="YÜKSEK",
            total_tokens_used=15000,
            estimated_cost_usd=0.15,
        )
        assert result.risk_score == 72
        assert result.risk_level == "YÜKSEK"


# ============================================================
# IhaleAnalizAI — JSON Parse Testleri
# ============================================================


class TestJsonParsing:
    """JSON parse testleri / JSON parsing tests."""

    @patch("src.ai_engine.analyzer.ChatOpenAI")
    @patch("src.ai_engine.analyzer.OpenAIEmbeddings")
    def _create_analyzer(self, mock_embeddings, mock_llm):
        """Mock ile analyzer oluştur / Create analyzer with mocks."""
        return IhaleAnalizAI(openai_api_key="test-key")

    def test_parse_valid_json(self) -> None:
        """Geçerli JSON parse / Parse valid JSON."""
        analyzer = self._create_analyzer()
        data = '{"risk_skoru": 65, "riskler": []}'
        result = analyzer._parse_json_response(data)
        assert result["risk_skoru"] == 65

    def test_parse_json_in_code_block(self) -> None:
        """Kod bloğu içindeki JSON / JSON in code block."""
        analyzer = self._create_analyzer()
        data = '```json\n{"risk_skoru": 42}\n```'
        result = analyzer._parse_json_response(data)
        assert result["risk_skoru"] == 42

    def test_parse_json_with_surrounding_text(self) -> None:
        """Çevreleyen metin içindeki JSON / JSON with surrounding text."""
        analyzer = self._create_analyzer()
        data = 'İşte analiz sonucu:\n{"risk_skoru": 55}\nBu sonuçlara göre...'
        result = analyzer._parse_json_response(data)
        assert result["risk_skoru"] == 55

    def test_parse_empty_response(self) -> None:
        """Boş yanıt / Empty response."""
        analyzer = self._create_analyzer()
        result = analyzer._parse_json_response("")
        assert result == {}

    def test_parse_invalid_json_returns_raw(self) -> None:
        """Geçersiz JSON raw döndürmeli / Invalid JSON should return raw."""
        analyzer = self._create_analyzer()
        result = analyzer._parse_json_response("bu json değil")
        assert "parse_error" in result or "raw_response" in result

    def test_parse_json_with_trailing_comma(self) -> None:
        """Sondaki virgül olan JSON / JSON with trailing comma."""
        analyzer = self._create_analyzer()
        data = '{"a": 1, "b": 2,}'
        result = analyzer._parse_json_response(data)
        assert result.get("a") == 1


# ============================================================
# IhaleAnalizAI — Risk Skoru Hesaplama Testleri
# ============================================================


class TestRiskScoreCalculation:
    """Risk skoru hesaplama testleri / Risk score calculation tests."""

    @patch("src.ai_engine.analyzer.ChatOpenAI")
    @patch("src.ai_engine.analyzer.OpenAIEmbeddings")
    def _create_analyzer(self, mock_embeddings, mock_llm):
        """Mock ile analyzer oluştur / Create analyzer with mocks."""
        return IhaleAnalizAI(openai_api_key="test-key")

    def test_empty_results_returns_default(self) -> None:
        """Boş sonuçlar varsayılan skor döndürmeli / Empty results should return default score."""
        analyzer = self._create_analyzer()
        score = analyzer.calculate_risk_score({})
        assert 0 <= score <= 100

    def test_high_risk_results_return_high_score(self) -> None:
        """Yüksek riskli sonuçlar yüksek skor vermeli / High risk should give high score."""
        analyzer = self._create_analyzer()
        results = {
            "penalty_clauses": {
                "cezalar": [
                    {"risk_seviyesi": "KRİTİK"},
                    {"risk_seviyesi": "YÜKSEK"},
                    {"risk_seviyesi": "KRİTİK"},
                ]
            },
            "financial_summary": {
                "mali_riskler": ["risk1", "risk2", "risk3", "risk4", "risk5"]
            },
            "timeline_analysis": {
                "gecikme_riski_degerlendirmesi": "Çok yüksek gecikme riski"
            },
            "risk_analysis": {
                "risk_skoru": 85,
                "riskler": [{"seviye": "YÜKSEK"}],
            },
            "required_documents": {
                "zorunlu_belgeler": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "onemli_uyarilar": ["uyarı1", "uyarı2"],
            },
        }
        score = analyzer.calculate_risk_score(results)
        assert score >= 60  # Yüksek riskli sonuçlar

    def test_low_risk_results_return_low_score(self) -> None:
        """Düşük riskli sonuçlar düşük skor vermeli / Low risk should give low score."""
        analyzer = self._create_analyzer()
        results = {
            "penalty_clauses": {
                "cezalar": [{"risk_seviyesi": "DÜŞÜK"}]
            },
            "financial_summary": {
                "mali_riskler": []
            },
            "timeline_analysis": {
                "gecikme_riski_degerlendirmesi": "Düşük risk, sorunsuz"
            },
            "risk_analysis": {
                "risk_skoru": 20,
                "riskler": [{"seviye": "DÜŞÜK"}],
            },
            "required_documents": {
                "zorunlu_belgeler": [1, 2, 3],
                "onemli_uyarilar": [],
            },
        }
        score = analyzer.calculate_risk_score(results)
        assert score <= 50

    def test_score_in_valid_range(self) -> None:
        """Skor 0-100 aralığında olmalı / Score should be in 0-100 range."""
        analyzer = self._create_analyzer()
        # Çeşitli girdilerle test / Test with various inputs
        for results in [{}, {"risk_analysis": {}}, {"penalty_clauses": {"cezalar": []}}]:
            score = analyzer.calculate_risk_score(results)
            assert 0 <= score <= 100


class TestScoreToLevel:
    """Skor -> seviye dönüşüm testleri / Score -> level conversion tests."""

    @patch("src.ai_engine.analyzer.ChatOpenAI")
    @patch("src.ai_engine.analyzer.OpenAIEmbeddings")
    def _create_analyzer(self, mock_embeddings, mock_llm):
        return IhaleAnalizAI(openai_api_key="test-key")

    def test_low_score(self) -> None:
        assert IhaleAnalizAI._score_to_level(10) == "DÜŞÜK"
        assert IhaleAnalizAI._score_to_level(25) == "DÜŞÜK"

    def test_medium_score(self) -> None:
        assert IhaleAnalizAI._score_to_level(30) == "ORTA"
        assert IhaleAnalizAI._score_to_level(50) == "ORTA"

    def test_high_score(self) -> None:
        assert IhaleAnalizAI._score_to_level(55) == "YÜKSEK"
        assert IhaleAnalizAI._score_to_level(75) == "YÜKSEK"

    def test_very_high_score(self) -> None:
        assert IhaleAnalizAI._score_to_level(80) == "ÇOK YÜKSEK"
        assert IhaleAnalizAI._score_to_level(100) == "ÇOK YÜKSEK"


# ============================================================
# IhaleAnalizAI — Başlatma ve Edge Case Testleri
# ============================================================


class TestAnalyzerInit:
    """Analyzer başlatma testleri / Analyzer initialization tests."""

    @patch("src.ai_engine.analyzer.ChatOpenAI")
    @patch("src.ai_engine.analyzer.OpenAIEmbeddings")
    def test_init_with_defaults(self, mock_embeddings, mock_llm) -> None:
        """Varsayılan değerlerle başlatma / Init with defaults."""
        analyzer = IhaleAnalizAI(openai_api_key="test-key")
        assert analyzer.api_key == "test-key"
        assert analyzer.model == "gpt-4o"
        assert analyzer.temperature == 0.1
        assert analyzer.chunk_size == 1500
        assert analyzer.chunk_overlap == 200
        assert analyzer.top_k == 15

    @patch("src.ai_engine.analyzer.ChatOpenAI")
    @patch("src.ai_engine.analyzer.OpenAIEmbeddings")
    def test_init_with_custom_params(self, mock_embeddings, mock_llm) -> None:
        """Özel parametrelerle başlatma / Init with custom params."""
        analyzer = IhaleAnalizAI(
            openai_api_key="key",
            model="gpt-4-turbo",
            temperature=0.5,
            chunk_size=2000,
            chunk_overlap=300,
            top_k=20,
        )
        assert analyzer.model == "gpt-4-turbo"
        assert analyzer.temperature == 0.5
        assert analyzer.chunk_size == 2000
        assert analyzer.top_k == 20


class TestVectorStoreCreation:
    """Vektör store oluşturma testleri / Vector store creation tests."""

    @patch("src.ai_engine.analyzer.ChatOpenAI")
    @patch("src.ai_engine.analyzer.OpenAIEmbeddings")
    def test_empty_text_raises_error(self, mock_embeddings, mock_llm) -> None:
        """Boş metin ValueError fırlatmalı / Empty text should raise ValueError."""
        analyzer = IhaleAnalizAI(openai_api_key="test-key")
        with pytest.raises(ValueError, match="boş olamaz"):
            analyzer.create_vector_store("")

    @patch("src.ai_engine.analyzer.ChatOpenAI")
    @patch("src.ai_engine.analyzer.OpenAIEmbeddings")
    def test_whitespace_text_raises_error(self, mock_embeddings, mock_llm) -> None:
        """Sadece boşluk ValueError fırlatmalı / Whitespace-only should raise ValueError."""
        analyzer = IhaleAnalizAI(openai_api_key="test-key")
        with pytest.raises(ValueError):
            analyzer.create_vector_store("   \n\n   ")


class TestAnalyzeEmptyDocument:
    """Boş doküman analizi testleri / Empty document analysis tests."""

    @patch("src.ai_engine.analyzer.ChatOpenAI")
    @patch("src.ai_engine.analyzer.OpenAIEmbeddings")
    @pytest.mark.asyncio
    async def test_empty_document_returns_empty_result(self, mock_embeddings, mock_llm) -> None:
        """Boş doküman boş sonuç döndürmeli / Empty document should return empty result."""
        analyzer = IhaleAnalizAI(openai_api_key="test-key")
        doc = ParsedDocument(full_text="", pages=[], metadata=DocumentMetadata())
        result = await analyzer.analyze(doc)
        assert isinstance(result, AnalysisResult)
        assert result.risk_analysis == {}
