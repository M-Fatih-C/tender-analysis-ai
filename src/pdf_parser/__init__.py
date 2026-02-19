"""
TenderAI PDF Ayrıştırma Paketi / PDF Parsing Package.

İhale şartname PDF'lerini ayrıştırır ve metin çıkarır.
Parses tender specification PDFs and extracts text.
"""

from src.pdf_parser.parser import (
    IhalePDFParser,
    ParsedDocument,
    PageContent,
    TableContent,
    Section,
    DocumentMetadata,
)

__all__ = [
    "IhalePDFParser",
    "ParsedDocument",
    "PageContent",
    "TableContent",
    "Section",
    "DocumentMetadata",
]
