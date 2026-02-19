"""
TenderAI PDF Ayrıştırma Paketi / PDF Parsing Package.

İhale şartname PDF'lerini ayrıştırır ve metin çıkarır.
Parses tender specification PDFs and extracts text.
"""

from src.pdf_parser.parser import PDFParser

__all__ = ["PDFParser"]
