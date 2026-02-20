"""
TenderAI PDF Rapor Üretici Testleri / PDF Report Generator Tests.

ReportGenerator sınıfı için birim testleri.
Unit tests for ReportGenerator class.
"""

import pytest
from src.report.generator import ReportGenerator, TenderPDF, _COLORS


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def generator():
    """ReportGenerator instance."""
    return ReportGenerator()


@pytest.fixture
def sample_result():
    """Örnek analiz sonucu / Sample analysis result."""
    return {
        "risk_score": 65,
        "risk_level": "YÜKSEK",
        "risk_analysis": {
            "ozet": "Orta-yüksek riskli bir ihale.",
            "riskler": [
                {
                    "kategori": "Mali",
                    "baslik": "Yüksek teminat oranı",
                    "seviye": "YÜKSEK",
                    "aciklama": "Geçici teminat %5 üzerinde",
                    "madde_referans": "Madde 12",
                    "oneri": "Teminat maliyetini hesaplayın",
                },
                {
                    "kategori": "Teknik",
                    "baslik": "Uzman personel gereksinimi",
                    "seviye": "ORTA",
                    "aciklama": "3 mühendis istiyor",
                    "madde_referans": "Madde 8",
                    "oneri": "Kadroyu kontrol edin",
                },
            ],
        },
        "required_documents": {
            "zorunlu_belgeler": [
                {"belge_adi": "İş Bitirme Belgesi", "aciklama": "Son 5 yıl"},
                {"belge_adi": "Bilanço", "aciklama": "Son 3 yıl"},
            ],
            "istege_bagli_belgeler": [
                {"belge_adi": "ISO 9001 Belgesi"},
            ],
            "onemli_uyarilar": ["Eksik belge ihaleden elenme sebebidir"],
        },
        "penalty_clauses": {
            "cezalar": [
                {
                    "ceza_turu": "Gecikme Cezası",
                    "miktar_oran": "%0.5/gün",
                    "risk_seviyesi": "YÜKSEK",
                    "madde_referans": "Madde 35",
                    "aciklama": "Günlük gecikme cezası",
                },
            ],
        },
        "financial_summary": {
            "tahmini_ihale_bedeli": "5.000.000 TL",
            "gecici_teminat": "150.000 TL",
            "kesin_teminat": "300.000 TL",
            "odeme_kosullari": "Hakediş karşılığı 30 gün içinde",
            "mali_riskler": ["Fiyat farkı hesaplanmıyor"],
        },
        "timeline_analysis": {
            "toplam_is_suresi": "180 gün",
            "ise_baslama_suresi": "Sözleşmeden itibaren 10 gün",
            "milestones": [
                {"asama": "Yer teslimi", "sure": "10 gün"},
                {"asama": "İş bitimi", "sure": "180 gün"},
            ],
            "gecikme_riski_degerlendirmesi": "Süre sıkı ancak uygulanabilir.",
        },
        "executive_summary": {
            "ozet": "Bu ihale orta-yüksek risk taşımaktadır.",
            "guclu_yanlar": ["Net teknik şartname", "Makul süre"],
            "riskli_alanlar": ["Yüksek teminat", "Ceza oranı"],
            "tavsiye": "Dikkatli girilmeli, teminat maliyetleri hesaplanmalı.",
        },
    }


# ============================================================
# ReportGenerator Testleri
# ============================================================


class TestReportGenerator:
    """ReportGenerator testleri."""

    def test_init(self, generator) -> None:
        """Generator oluşturulabilmeli / Should initialize."""
        assert generator is not None

    def test_generate_returns_bytes(self, generator, sample_result) -> None:
        """generate bytes döndürmeli / Should return bytes."""
        pdf_bytes = generator.generate(sample_result, "test_sartname.pdf")
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 1000  # Anlamlı boyutta olmalı

    def test_pdf_starts_with_header(self, generator, sample_result) -> None:
        """PDF başlığı doğru olmalı / PDF header should be correct."""
        pdf_bytes = generator.generate(sample_result, "test.pdf")
        assert pdf_bytes[:5] == b"%PDF-"

    def test_generate_with_empty_result(self, generator) -> None:
        """Boş sonuçla rapor üretebilmeli / Should handle empty results."""
        result = {
            "risk_score": 0,
            "risk_level": "DÜŞÜK",
            "risk_analysis": {},
            "required_documents": {},
            "penalty_clauses": {},
            "financial_summary": {},
            "timeline_analysis": {},
            "executive_summary": {},
        }
        pdf_bytes = generator.generate(result, "bos_test.pdf")
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 500

    def test_generate_with_missing_sections(self, generator) -> None:
        """Eksik bölümlerle rapor üretebilmeli / Should handle missing sections."""
        result = {"risk_score": 42, "risk_level": "ORTA"}
        pdf_bytes = generator.generate(result)
        assert isinstance(pdf_bytes, bytes)

    def test_generate_with_long_filename(self, generator, sample_result) -> None:
        """Uzun dosya adıyla rapor üretebilmeli / Should handle long filenames."""
        long_name = "A" * 200 + ".pdf"
        pdf_bytes = generator.generate(sample_result, long_name)
        assert isinstance(pdf_bytes, bytes)


# ============================================================
# Risk Renk Testleri
# ============================================================


class TestRiskColors:
    """Risk renk fonksiyonları testleri."""

    def test_low_score_green(self) -> None:
        color = ReportGenerator._risk_color_rgb(25)
        assert color == _COLORS["success"]

    def test_medium_score_warning(self) -> None:
        color = ReportGenerator._risk_color_rgb(55)
        assert color == _COLORS["warning"]

    def test_high_score_danger(self) -> None:
        color = ReportGenerator._risk_color_rgb(85)
        assert color == _COLORS["danger"]

    def test_risk_text_kritik(self) -> None:
        color = ReportGenerator._risk_color_text("KRİTİK")
        assert color == (180, 0, 0)

    def test_risk_text_yuksek(self) -> None:
        color = ReportGenerator._risk_color_text("YÜKSEK")
        assert color == _COLORS["danger"]

    def test_risk_text_orta(self) -> None:
        color = ReportGenerator._risk_color_text("ORTA")
        assert color == _COLORS["warning"]

    def test_risk_text_dusuk(self) -> None:
        color = ReportGenerator._risk_color_text("DÜŞÜK")
        assert color == _COLORS["success"]


# ============================================================
# TenderPDF Testleri
# ============================================================


class TestTenderPDF:
    """TenderPDF testleri."""

    def test_init(self) -> None:
        pdf = TenderPDF(file_name="Test")
        assert pdf._file_name == "Test"
        assert pdf._is_cover is True

    def test_cover_page_no_header(self) -> None:
        """Kapak sayfasında header olmamalı / No header on cover page."""
        pdf = TenderPDF()
        pdf.add_font("DejaVu", "", str(ReportGenerator()._font_regular))
        pdf.add_font("DejaVu", "B", str(ReportGenerator()._font_bold))
        pdf._is_cover = True
        pdf.add_page()
        # Header çağrılır ama is_cover True olduğu için boş kalır
        # Bu sadece crash etmediğini test eder
        assert pdf.page_no() == 1
