"""
TenderAI PDF Parser Testleri / PDF Parser Tests.

PDFParser sınıfı için birim testleri.
Unit tests for PDFParser class.
"""

import pytest
from pathlib import Path

from src.pdf_parser.parser import PDFParser, ParsedDocument


class TestPDFParser:
    """PDFParser sınıfı testleri / PDFParser class tests."""

    def test_parser_init_with_valid_pdf(self, tmp_path: Path) -> None:
        """Geçerli PDF dosyasıyla başlatma / Initialize with valid PDF file."""
        # Geçici test PDF oluştur / Create temporary test PDF
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test content")

        parser = PDFParser(pdf_file)
        assert parser.file_path == pdf_file

    def test_parser_init_file_not_found(self) -> None:
        """Dosya bulunamadığında hata / Error when file not found."""
        with pytest.raises(FileNotFoundError):
            PDFParser("/nonexistent/file.pdf")

    def test_parser_init_invalid_extension(self, tmp_path: Path) -> None:
        """Geçersiz uzantıda hata / Error with invalid extension."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not a pdf")

        with pytest.raises(ValueError):
            PDFParser(txt_file)

    def test_extract_text_not_implemented(self, tmp_path: Path) -> None:
        """extract_text henüz implement edilmemeli / extract_text should not be implemented yet."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        parser = PDFParser(pdf_file)
        with pytest.raises(NotImplementedError):
            parser.extract_text()

    def test_extract_tables_not_implemented(self, tmp_path: Path) -> None:
        """extract_tables henüz implement edilmemeli / extract_tables should not be implemented yet."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        parser = PDFParser(pdf_file)
        with pytest.raises(NotImplementedError):
            parser.extract_tables()

    def test_parse_not_implemented(self, tmp_path: Path) -> None:
        """parse henüz implement edilmemeli / parse should not be implemented yet."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test")

        parser = PDFParser(pdf_file)
        with pytest.raises(NotImplementedError):
            parser.parse()

    def test_parsed_document_defaults(self) -> None:
        """ParsedDocument varsayılan değerleri / ParsedDocument default values."""
        doc = ParsedDocument()
        assert doc.filename == ""
        assert doc.total_pages == 0
        assert doc.text_content == {}
        assert doc.tables == []
        assert doc.metadata == {}
