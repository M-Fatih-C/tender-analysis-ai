"""
TenderAI Analyzer Testleri / Analyzer Tests.

TenderAnalyzer sınıfı için birim testleri.
Unit tests for TenderAnalyzer class.
"""

import pytest

from src.ai_engine.analyzer import TenderAnalyzer, AnalysisResult, RiskItem, RiskLevel


class TestTenderAnalyzer:
    """TenderAnalyzer sınıfı testleri / TenderAnalyzer class tests."""

    def test_analyzer_init(self) -> None:
        """Analyzer başlatma / Initialize analyzer."""
        analyzer = TenderAnalyzer(api_key="test-key")
        assert analyzer.api_key == "test-key"
        assert analyzer._llm is None

    def test_analyzer_init_default(self) -> None:
        """Varsayılan değerlerle başlatma / Initialize with defaults."""
        analyzer = TenderAnalyzer()
        assert analyzer.api_key is None

    def test_analyze_risks_not_implemented(self) -> None:
        """analyze_risks henüz implement edilmemeli / should not be implemented yet."""
        analyzer = TenderAnalyzer()
        with pytest.raises(NotImplementedError):
            analyzer.analyze_risks("test text")

    def test_extract_required_documents_not_implemented(self) -> None:
        """extract_required_documents henüz implement edilmemeli."""
        analyzer = TenderAnalyzer()
        with pytest.raises(NotImplementedError):
            analyzer.extract_required_documents("test text")

    def test_extract_penalty_clauses_not_implemented(self) -> None:
        """extract_penalty_clauses henüz implement edilmemeli."""
        analyzer = TenderAnalyzer()
        with pytest.raises(NotImplementedError):
            analyzer.extract_penalty_clauses("test text")

    def test_full_analysis_not_implemented(self) -> None:
        """full_analysis henüz implement edilmemeli."""
        analyzer = TenderAnalyzer()
        with pytest.raises(NotImplementedError):
            analyzer.full_analysis("test text")

    def test_analysis_result_defaults(self) -> None:
        """AnalysisResult varsayılan değerleri / AnalysisResult default values."""
        result = AnalysisResult()
        assert result.risk_analysis == []
        assert result.required_documents == []
        assert result.penalty_clauses == []
        assert result.financial_summary == {}
        assert result.timeline_analysis == {}
        assert result.overall_risk_score == 0.0

    def test_risk_item_creation(self) -> None:
        """RiskItem oluşturma / RiskItem creation."""
        risk = RiskItem(
            clause="Madde 5.3",
            description="Gecikme cezası yüksek",
            level=RiskLevel.HIGH,
            recommendation="Süre planlaması yapılmalı",
        )
        assert risk.clause == "Madde 5.3"
        assert risk.level == RiskLevel.HIGH

    def test_risk_level_values(self) -> None:
        """Risk seviyesi değerleri / Risk level values."""
        assert RiskLevel.LOW.value == "düşük"
        assert RiskLevel.MEDIUM.value == "orta"
        assert RiskLevel.HIGH.value == "yüksek"
        assert RiskLevel.CRITICAL.value == "kritik"
