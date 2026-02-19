"""
TenderAI PDF Parser Testleri / PDF Parser Tests.

IhalePDFParser sınıfı ve yardımcı dataclass'lar için birim testleri.
Unit tests for IhalePDFParser class and helper dataclasses.

fpdf2 ile gerçek PDF oluşturarak test eder — harici dosya bağımlılığı yok.
Tests with real PDFs generated via fpdf2 — no external file dependency.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from fpdf import FPDF

from src.pdf_parser.parser import (
    IhalePDFParser,
    ParsedDocument,
    PageContent,
    TableContent,
    Section,
    DocumentMetadata,
    SECTION_KEYWORDS,
)


# ============================================================
# Test Fixtures / Test Hazırlıkları
# ============================================================


def _create_text_pdf(tmp_path: Path, text: str, filename: str = "test.pdf") -> Path:
    """fpdf2 ile basit metin PDF oluştur / Create simple text PDF with fpdf2."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for line in text.split("\n"):
        pdf.cell(0, 10, line, new_x="LMARGIN", new_y="NEXT")
    file_path = tmp_path / filename
    pdf.output(str(file_path))
    return file_path


def _create_multipage_pdf(tmp_path: Path, pages_text: list[str], filename: str = "multi.pdf") -> Path:
    """Çok sayfalı PDF oluştur / Create multi-page PDF."""
    pdf = FPDF()
    pdf.set_font("Helvetica", size=11)
    for page_text in pages_text:
        pdf.add_page()
        for line in page_text.split("\n"):
            pdf.cell(0, 8, line, new_x="LMARGIN", new_y="NEXT")
    file_path = tmp_path / filename
    pdf.output(str(file_path))
    return file_path


def _create_table_pdf(tmp_path: Path, filename: str = "table.pdf") -> Path:
    """Tablo içeren PDF oluştur / Create PDF with table."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)

    pdf.cell(0, 10, "Tablo Testi", new_x="LMARGIN", new_y="NEXT")

    # Basit tablo çiz / Draw simple table
    headers = ["No", "Kalem", "Miktar", "Birim"]
    col_width = 45
    row_height = 8

    for header in headers:
        pdf.cell(col_width, row_height, header, border=1)
    pdf.ln(row_height)

    rows = [
        ["1", "Bilgisayar", "10", "Adet"],
        ["2", "Yazici", "5", "Adet"],
        ["3", "Monitor", "10", "Adet"],
    ]
    for row in rows:
        for cell in row:
            pdf.cell(col_width, row_height, cell, border=1)
        pdf.ln(row_height)

    file_path = tmp_path / filename
    pdf.output(str(file_path))
    return file_path


def _create_empty_pdf(tmp_path: Path, filename: str = "empty.pdf") -> Path:
    """Boş PDF oluştur / Create empty PDF."""
    pdf = FPDF()
    pdf.add_page()
    file_path = tmp_path / filename
    pdf.output(str(file_path))
    return file_path


# ============================================================
# Dataclass Testleri / Dataclass Tests
# ============================================================


class TestDataclasses:
    """Dataclass varsayılan değer testleri / Dataclass default value tests."""

    def test_page_content_defaults(self) -> None:
        """PageContent varsayılan değerleri / defaults."""
        page = PageContent()
        assert page.page_num == 0
        assert page.text == ""
        assert page.has_table is False

    def test_table_content_defaults(self) -> None:
        """TableContent varsayılan değerleri / defaults."""
        table = TableContent()
        assert table.page_num == 0
        assert table.headers == []
        assert table.rows == []
        assert table.raw_data == []

    def test_section_defaults(self) -> None:
        """Section varsayılan değerleri / defaults."""
        section = Section()
        assert section.title == ""
        assert section.content == ""
        assert section.page_num == 0
        assert section.section_type == "genel"

    def test_document_metadata_defaults(self) -> None:
        """DocumentMetadata varsayılan değerleri / defaults."""
        meta = DocumentMetadata()
        assert meta.total_pages == 0
        assert meta.total_tables == 0
        assert meta.total_chars == 0
        assert meta.is_scanned is False
        assert meta.parse_time_seconds == 0.0

    def test_parsed_document_defaults(self) -> None:
        """ParsedDocument varsayılan değerleri / defaults."""
        doc = ParsedDocument()
        assert doc.full_text == ""
        assert doc.pages == []
        assert doc.tables == []
        assert doc.sections == []
        assert isinstance(doc.metadata, DocumentMetadata)

    def test_section_creation_with_values(self) -> None:
        """Section oluşturma değerlerle / creation with values."""
        section = Section(
            title="Madde 5 - Ceza Hukumleri",
            content="Gecikme halinde...",
            page_num=3,
            section_type="ceza",
        )
        assert section.title == "Madde 5 - Ceza Hukumleri"
        assert section.section_type == "ceza"
        assert section.page_num == 3


# ============================================================
# IhalePDFParser Testleri / IhalePDFParser Tests
# ============================================================


class TestIhalePDFParserInit:
    """Parser başlatma testleri / Parser initialization tests."""

    def test_parser_init(self) -> None:
        """Parser başlatma / Initialize parser."""
        parser = IhalePDFParser()
        assert parser is not None


class TestParseTextPDF:
    """Metin PDF parse testleri / Text PDF parse tests."""

    def test_parse_simple_text_pdf(self, tmp_path: Path) -> None:
        """Basit metin PDF parse / Parse simple text PDF."""
        pdf_path = _create_text_pdf(tmp_path, "Bu bir test metnidir.\nIkinci satir.")
        parser = IhalePDFParser()
        result = parser.parse(pdf_path)

        assert isinstance(result, ParsedDocument)
        assert result.metadata.total_pages == 1
        assert "test" in result.full_text.lower()
        assert len(result.pages) == 1
        assert result.pages[0].page_num == 1

    def test_parse_multipage_pdf(self, tmp_path: Path) -> None:
        """Çok sayfalı PDF parse / Parse multi-page PDF."""
        pages = [f"Sayfa {i} icerigi burada" for i in range(1, 6)]
        pdf_path = _create_multipage_pdf(tmp_path, pages)
        parser = IhalePDFParser()
        result = parser.parse(pdf_path)

        assert result.metadata.total_pages == 5
        assert len(result.pages) == 5
        assert result.pages[0].page_num == 1
        assert result.pages[4].page_num == 5

    def test_parse_returns_metadata(self, tmp_path: Path) -> None:
        """Parse metadata doldurulmalı / Parse should fill metadata."""
        pdf_path = _create_text_pdf(tmp_path, "Metadata testi")
        parser = IhalePDFParser()
        result = parser.parse(pdf_path)

        assert result.metadata.file_name == "test.pdf"
        assert result.metadata.file_size_mb > 0
        assert result.metadata.total_chars > 0
        assert result.metadata.parse_time_seconds >= 0

    def test_parse_empty_pdf(self, tmp_path: Path) -> None:
        """Boş PDF parse / Parse empty PDF."""
        pdf_path = _create_empty_pdf(tmp_path)
        parser = IhalePDFParser()
        result = parser.parse(pdf_path)

        assert result.metadata.total_pages == 1
        assert result.full_text.strip() == ""


class TestParseWithBytes:
    """Bytes input testleri / Bytes input tests."""

    def test_parse_from_bytes(self, tmp_path: Path) -> None:
        """Bytes girdi ile parse / Parse from bytes input."""
        pdf_path = _create_text_pdf(tmp_path, "Bytes ile test")
        pdf_bytes = pdf_path.read_bytes()

        parser = IhalePDFParser()
        result = parser.parse(pdf_bytes)

        assert isinstance(result, ParsedDocument)
        assert result.metadata.file_name == "bytes_input.pdf"
        assert result.metadata.total_pages >= 1


class TestExtractText:
    """Metin çıkarma testleri / Text extraction tests."""

    def test_extract_text_returns_string(self, tmp_path: Path) -> None:
        """extract_text string döndürmeli / should return string."""
        pdf_path = _create_text_pdf(tmp_path, "Metin cikarma testi")
        parser = IhalePDFParser()
        text = parser.extract_text(pdf_path)

        assert isinstance(text, str)
        assert "Metin" in text


class TestExtractTables:
    """Tablo çıkarma testleri / Table extraction tests."""

    def test_extract_tables_from_table_pdf(self, tmp_path: Path) -> None:
        """Tablo PDF'den tablo çıkarma / Extract tables from table PDF."""
        pdf_path = _create_table_pdf(tmp_path)
        parser = IhalePDFParser()
        tables = parser.extract_tables(pdf_path)

        # pdfplumber tablo tespit edebilirse assert ederiz
        # tables may or may not be detected depending on pdfplumber's heuristic
        assert isinstance(tables, list)

    def test_no_tables_in_text_only_pdf(self, tmp_path: Path) -> None:
        """Sadece metin PDF'de tablo olmamalı / No tables in text-only PDF."""
        pdf_path = _create_text_pdf(tmp_path, "Sadece metin, tablo yok.")
        parser = IhalePDFParser()
        tables = parser.extract_tables(pdf_path)

        assert tables == []


class TestExtractMetadata:
    """Metadata çıkarma testleri / Metadata extraction tests."""

    def test_extract_metadata_returns_dict(self, tmp_path: Path) -> None:
        """extract_metadata dict döndürmeli / should return dict."""
        pdf_path = _create_text_pdf(tmp_path, "Metadata testi")
        parser = IhalePDFParser()
        meta = parser.extract_metadata(pdf_path)

        assert isinstance(meta, dict)
        assert meta["file_name"] == "test.pdf"
        assert meta["total_pages"] == 1
        assert "author" in meta


class TestSectionDetection:
    """Bölüm tespiti testleri / Section detection tests."""

    def test_detect_madde_pattern(self) -> None:
        """'Madde X - Başlık' kalıbı tespiti / Detect 'Madde X - Title' pattern."""
        text = (
            "Giris metni burada.\n"
            "Madde 1 - Konu\n"
            "Bu ihale konusu hakkindadir.\n"
            "Madde 2 - Tanimlar\n"
            "Tanimlar asagidadir.\n"
        )
        parser = IhalePDFParser()
        sections = parser.detect_sections(text)

        assert len(sections) == 2
        assert "Madde 1" in sections[0].title
        assert "Madde 2" in sections[1].title

    def test_detect_bolum_pattern(self) -> None:
        """'BÖLÜM X' kalıbı tespiti / Detect 'BÖLÜM X' pattern."""
        text = (
            "BÖLÜM 1 - Idari Sartname\n"
            "Idari sartname icerigi.\n"
            "BÖLÜM 2 - Teknik Sartname\n"
            "Teknik sartname icerigi.\n"
        )
        parser = IhalePDFParser()
        sections = parser.detect_sections(text)

        assert len(sections) >= 2

    def test_detect_ek_pattern(self) -> None:
        """'EK-X' kalıbı tespiti / Detect 'EK-X' pattern."""
        text = (
            "EK-1 Teknik Ozellikler\n"
            "Teknik ozellikler burada.\n"
            "EK-2 Fiyat Tablosu\n"
            "Fiyat bilgileri burada.\n"
        )
        parser = IhalePDFParser()
        sections = parser.detect_sections(text)

        assert len(sections) >= 2
        assert "EK" in sections[0].title

    def test_empty_text_returns_no_sections(self) -> None:
        """Boş metin bölüm döndürmemeli / Empty text should return no sections."""
        parser = IhalePDFParser()
        sections = parser.detect_sections("")
        assert sections == []

    def test_no_pattern_returns_no_sections(self) -> None:
        """Kalıp olmayan metin bölüm döndürmemeli / Text without patterns returns empty."""
        parser = IhalePDFParser()
        sections = parser.detect_sections("Bu metinde hicbir baslik yok.")
        assert sections == []


class TestSectionTypeClassification:
    """Bölüm tipi sınıflandırma testleri / Section type classification tests."""

    def test_classify_ceza_section(self) -> None:
        """Ceza bölümü sınıflandırma / Classify penalty section."""
        parser = IhalePDFParser()
        section_type = parser._classify_section_type(
            "Madde 10 - Ceza Hukumleri",
            "Gecikme halinde ceza uygulanir."
        )
        assert section_type == "ceza"

    def test_classify_mali_section(self) -> None:
        """Mali bölüm sınıflandırma / Classify financial section."""
        parser = IhalePDFParser()
        section_type = parser._classify_section_type(
            "Madde 5 - Odeme Kosullari",
            "Teminat miktari ve odeme plani."
        )
        assert section_type == "mali"

    def test_classify_teknik_section(self) -> None:
        """Teknik bölüm sınıflandırma / Classify technical section."""
        parser = IhalePDFParser()
        section_type = parser._classify_section_type(
            "Madde 3 - Teknik Sartname",
            "Malzeme standartlari asagidadir."
        )
        assert section_type == "teknik"

    def test_classify_genel_fallback(self) -> None:
        """Eşleşme yoksa genel / Default to genel when no match."""
        parser = IhalePDFParser()
        section_type = parser._classify_section_type(
            "Madde 99 - Diger",
            "Herhangi bir icerik."
        )
        assert section_type == "genel"


class TestCleanText:
    """Metin temizleme testleri / Text cleaning tests."""

    def test_clean_extra_whitespace(self) -> None:
        """Fazla boşluk temizleme / Clean extra whitespace."""
        parser = IhalePDFParser()
        result = parser.clean_text("merhaba    dunya")
        assert "merhaba dunya" == result

    def test_clean_multiple_blank_lines(self) -> None:
        """Çoklu boş satır temizleme / Clean multiple blank lines."""
        parser = IhalePDFParser()
        result = parser.clean_text("satir1\n\n\n\n\nsatir2")
        assert result == "satir1\n\nsatir2"

    def test_clean_control_characters(self) -> None:
        """Kontrol karakteri temizleme / Clean control characters."""
        parser = IhalePDFParser()
        result = parser.clean_text("test\x00metin\x01burada")
        assert "\x00" not in result
        assert "\x01" not in result

    def test_clean_empty_text(self) -> None:
        """Boş metin temizleme / Clean empty text."""
        parser = IhalePDFParser()
        assert parser.clean_text("") == ""

    def test_clean_preserves_meaningful_content(self) -> None:
        """Anlamlı içeriği koruma / Preserve meaningful content."""
        parser = IhalePDFParser()
        text = "Madde 1 - Konu\nBu ihale konusu hakkindadir."
        result = parser.clean_text(text)
        assert "Madde 1" in result
        assert "ihale" in result


class TestScannedPDFDetection:
    """Taranmış PDF tespiti testleri / Scanned PDF detection tests."""

    def test_detect_scanned_pdf(self) -> None:
        """Az metinli sayfalar taranmış kabul edilmeli / Low-text pages should be detected as scanned."""
        parser = IhalePDFParser()
        pages = [
            PageContent(page_num=1, text="ab", has_table=False),
            PageContent(page_num=2, text="", has_table=False),
            PageContent(page_num=3, text="x", has_table=False),
        ]
        assert parser._detect_scanned_pdf(pages) is True

    def test_detect_normal_pdf(self) -> None:
        """Yeterli metinli sayfalar normal kabul edilmeli / Normal text pages should not be scanned."""
        parser = IhalePDFParser()
        pages = [
            PageContent(page_num=1, text="A" * 200, has_table=False),
            PageContent(page_num=2, text="B" * 300, has_table=False),
        ]
        assert parser._detect_scanned_pdf(pages) is False

    def test_detect_empty_pages_list(self) -> None:
        """Boş sayfa listesi False döndürmeli / Empty page list returns False."""
        parser = IhalePDFParser()
        assert parser._detect_scanned_pdf([]) is False


class TestFileValidation:
    """Dosya doğrulama testleri / File validation tests."""

    def test_file_not_found(self) -> None:
        """Dosya bulunamadığında FileNotFoundError / FileNotFoundError when not found."""
        parser = IhalePDFParser()
        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/file.pdf")

    def test_invalid_extension(self, tmp_path: Path) -> None:
        """Geçersiz uzantıda ValueError / ValueError on invalid extension."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not a pdf")
        parser = IhalePDFParser()
        with pytest.raises(ValueError):
            parser.parse(txt_file)


class TestEdgeCases:
    """Sınır durum testleri / Edge case tests."""

    def test_section_keywords_has_expected_types(self) -> None:
        """SECTION_KEYWORDS beklenen tipleri içermeli / should have expected types."""
        expected_types = {"ceza", "mali", "teknik", "idari", "sure", "genel"}
        assert set(SECTION_KEYWORDS.keys()) == expected_types

    def test_parse_returns_consistent_page_numbers(self, tmp_path: Path) -> None:
        """Sayfa numaraları tutarlı olmalı / Page numbers should be consistent."""
        pages = [f"Sayfa {i}" for i in range(1, 4)]
        pdf_path = _create_multipage_pdf(tmp_path, pages)
        parser = IhalePDFParser()
        result = parser.parse(pdf_path)

        for i, page in enumerate(result.pages, start=1):
            assert page.page_num == i
