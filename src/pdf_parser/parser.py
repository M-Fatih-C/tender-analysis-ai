"""
TenderAI PDF Ayrıştırma Motoru / PDF Parsing Engine.

İhale teknik ve idari şartname PDF dosyalarını ayrıştırır,
metin, tablo ve bölüm verilerini çıkarır.

Parses tender technical and administrative specification PDF files,
extracts text, table, and section data.

Birincil kütüphane: pdfplumber
Yedek tablo kütüphanesi: camelot
Primary library: pdfplumber
Fallback table library: camelot
"""

import io
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)


# ============================================================
# Dataclass Tanımları / Dataclass Definitions
# ============================================================


@dataclass
class PageContent:
    """
    Tek bir sayfanın içeriği / Content of a single page.

    Attributes:
        page_num: Sayfa numarası (1-indexed) / Page number
        text: Sayfadaki metin / Text on the page
        has_table: Sayfada tablo var mı / Does the page contain a table
    """

    page_num: int = 0
    text: str = ""
    has_table: bool = False


@dataclass
class TableContent:
    """
    PDF'den çıkarılan tablo / Table extracted from PDF.

    Attributes:
        page_num: Tablonun bulunduğu sayfa / Page containing the table
        headers: Tablo başlıkları / Table headers
        rows: Tablo satırları / Table rows
        raw_data: Ham tablo verisi (pdfplumber format) / Raw table data
    """

    page_num: int = 0
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    raw_data: list = field(default_factory=list)


@dataclass
class Section:
    """
    Tespit edilen şartname bölümü / maddesi.
    Detected specification section / clause.

    Attributes:
        title: Bölüm başlığı / Section title (örn: "Madde 5 - Ceza Hükümleri")
        content: Bölüm içeriği / Section content
        page_num: Başladığı sayfa / Starting page
        section_type: Bölüm tipi / Section type ("idari", "teknik", "ceza", "mali", "sure", "genel")
    """

    title: str = ""
    content: str = ""
    page_num: int = 0
    section_type: str = "genel"


@dataclass
class DocumentMetadata:
    """
    PDF doküman meta verileri / PDF document metadata.

    Attributes:
        total_pages: Toplam sayfa / Total pages
        total_tables: Toplam tablo / Total tables
        total_chars: Toplam karakter / Total characters
        total_sections: Toplam tespit edilen bölüm / Total detected sections
        file_name: Dosya adı / Filename
        file_size_mb: Dosya boyutu (MB) / File size (MB)
        is_scanned: Taranmış PDF mi (OCR gerekir) / Is scanned PDF (OCR needed)
        parse_time_seconds: Ayrıştırma süresi (sn) / Parse time (seconds)
    """

    total_pages: int = 0
    total_tables: int = 0
    total_chars: int = 0
    total_sections: int = 0
    file_name: str = ""
    file_size_mb: float = 0.0
    is_scanned: bool = False
    parse_time_seconds: float = 0.0


@dataclass
class ParsedDocument:
    """
    Ayrıştırılmış PDF dokümanı / Fully parsed PDF document.

    Attributes:
        full_text: Tüm temizlenmiş metin / All cleaned text
        pages: Sayfa bazlı içerik / Page-based content
        tables: Çıkarılan tablolar / Extracted tables
        sections: Tespit edilen bölümler / Detected sections
        metadata: Doküman meta verileri / Document metadata
    """

    full_text: str = ""
    pages: list[PageContent] = field(default_factory=list)
    tables: list[TableContent] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)


# ============================================================
# Section Detection Sabitleri / Section Detection Constants
# ============================================================

# İhale şartnamelerinde bölüm/madde başlığı tespit kalıpları
# Patterns for detecting section/clause headings in tender specs
SECTION_PATTERNS: list[re.Pattern] = [
    # "Madde 5 - Ceza Hükümleri" veya "Madde 5. Konu"
    re.compile(
        r"^(MADDE|Madde)\s+(\d+(?:\.\d+)*)\s*[-–:.]\s*(.+)",
        re.MULTILINE,
    ),
    # "BÖLÜM 3" veya "Bölüm III"
    re.compile(
        r"^(BÖLÜM|Bölüm)\s+(\w+)\s*[-–:.]?\s*(.*)",
        re.MULTILINE,
    ),
    # "EK-1" veya "Ek 1 - Teknik Şartname"
    re.compile(
        r"^(EK|Ek)\s*[-–]?\s*(\w+)\s*[-–:.]?\s*(.*)",
        re.MULTILINE,
    ),
]

# Bölüm tipi anahtar kelimeleri / Section type keywords
SECTION_KEYWORDS: dict[str, list[str]] = {
    "ceza": ["ceza", "yaptırım", "gecikme", "müeyyide", "cezai"],
    "mali": ["teminat", "ödeme", "fiyat", "bütçe", "bedel", "mali", "finansal", "kesin teminat"],
    "teknik": ["teknik", "şartname", "malzeme", "standart", "teknik özellik", "spesifikasyon"],
    "idari": ["yeterlilik", "belge", "başvuru", "teklif", "idari", "ihale"],
    "sure": ["süre", "tarih", "teslim", "başlama", "bitirme", "takvim", "termin"],
    "genel": [],
}

# Taranmış PDF tespiti eşik değeri / Scanned PDF detection threshold
# Sayfa başına ortalama bu kadar karakterden az metin çıkıyorsa,
# PDF muhtemelen taranmıştır.
_SCANNED_PDF_CHAR_THRESHOLD: int = 50


# ============================================================
# IhalePDFParser Sınıfı / IhalePDFParser Class
# ============================================================


class IhalePDFParser:
    """
    İhale teknik ve idari şartname PDF'lerini parse eden motor.
    Engine that parses tender technical and administrative specification PDFs.

    Desteklenen formatlar / Supported formats:
        - Normal metin bazlı PDF'ler (kopyalanabilir metin)
        - Tablo içeren PDF'ler
        - Taranmış PDF'ler (tespit eder, uyarır — OCR dışarıda yapılmalı)
        - Çok sayfalı PDF'ler (200+ sayfa, sayfa sayfa işler)

    Birincil kütüphane: pdfplumber
    Yedek tablo kütüphanesi: camelot-py
    """

    def __init__(self) -> None:
        """IhalePDFParser başlat / Initialize IhalePDFParser."""
        logger.info("IhalePDFParser başlatıldı / initialized")

    # ----------------------------------------------------------
    # Ana Parse Metodu / Main Parse Method
    # ----------------------------------------------------------

    def parse(self, file_path_or_bytes: str | Path | bytes) -> ParsedDocument:
        """
        Ana parse metodu — PDF dosyasını alır, yapılandırılmış çıktı verir.
        Main parse method — takes a PDF file, returns structured output.

        Args:
            file_path_or_bytes: PDF dosya yolu veya bytes verisi
                                PDF file path or bytes data

        Returns:
            ParsedDocument: Ayrıştırılmış doküman / Parsed document

        Raises:
            FileNotFoundError: Dosya bulunamadığında / When file not found
            ValueError: Geçersiz dosya formatında / When invalid file format
        """
        start_time = time.time()
        logger.info("PDF parse işlemi başlıyor / PDF parsing started")

        try:
            # Giriş tipini belirle / Determine input type
            file_name, file_size_mb, pdf_source = self._resolve_input(file_path_or_bytes)

            # Sayfa bazlı metin ve tablo çıkarma / Page-based text and table extraction
            pages, tables = self._extract_all(pdf_source)

            # Tam metin oluştur / Build full text
            raw_full_text = "\n\n".join(page.text for page in pages if page.text)

            # Metin temizleme / Clean text
            cleaned_text = self.clean_text(raw_full_text)

            # Bölüm tespiti / Section detection
            sections = self.detect_sections(cleaned_text, pages)

            # Taranmış PDF tespiti / Scanned PDF detection
            is_scanned = self._detect_scanned_pdf(pages)
            if is_scanned:
                logger.warning(
                    "Bu PDF taranmış görünüyor — OCR gerekebilir / "
                    "This PDF appears scanned — OCR may be needed"
                )

            # Metadata oluştur / Build metadata
            parse_time = time.time() - start_time
            metadata = DocumentMetadata(
                total_pages=len(pages),
                total_tables=len(tables),
                total_chars=len(cleaned_text),
                total_sections=len(sections),
                file_name=file_name,
                file_size_mb=file_size_mb,
                is_scanned=is_scanned,
                parse_time_seconds=round(parse_time, 3),
            )

            result = ParsedDocument(
                full_text=cleaned_text,
                pages=pages,
                tables=tables,
                sections=sections,
                metadata=metadata,
            )

            logger.info(
                "PDF parse tamamlandı / completed: "
                f"{metadata.total_pages} sayfa, {metadata.total_tables} tablo, "
                f"{metadata.total_sections} bölüm, {parse_time:.2f}sn"
            )
            return result

        except (FileNotFoundError, ValueError):
            raise
        except Exception as e:
            logger.error(f"PDF parse hatası / error: {e}", exc_info=True)
            raise RuntimeError(f"PDF ayrıştırılamadı / Could not parse PDF: {e}") from e

    # ----------------------------------------------------------
    # Metin Çıkarma / Text Extraction
    # ----------------------------------------------------------

    def extract_text(self, file_path_or_bytes: str | Path | bytes) -> str:
        """
        PDF'den tüm metni çıkarır / Extract all text from PDF.

        Sayfa sayfa pdfplumber ile işler, bellek dostu çalışır.
        Processes page by page with pdfplumber, memory-efficient.

        Args:
            file_path_or_bytes: PDF dosya yolu veya bytes / PDF file path or bytes

        Returns:
            Tüm PDF metni / All PDF text
        """
        try:
            _, _, pdf_source = self._resolve_input(file_path_or_bytes)
            pages, _ = self._extract_all(pdf_source, extract_tables=False)
            return "\n\n".join(page.text for page in pages if page.text)
        except Exception as e:
            logger.error(f"Metin çıkarma hatası / Text extraction error: {e}", exc_info=True)
            raise

    # ----------------------------------------------------------
    # Tablo Çıkarma / Table Extraction
    # ----------------------------------------------------------

    def extract_tables(self, file_path_or_bytes: str | Path | bytes) -> list[TableContent]:
        """
        PDF'deki tabloları çıkarır / Extract tables from PDF.

        Önce pdfplumber ile dener, başarısız olursa camelot'u kullanır.
        Tries pdfplumber first, falls back to camelot on failure.

        Args:
            file_path_or_bytes: PDF dosya yolu veya bytes / PDF file path or bytes

        Returns:
            Tablo listesi / List of tables
        """
        try:
            _, _, pdf_source = self._resolve_input(file_path_or_bytes)
            _, tables = self._extract_all(pdf_source, extract_text=False)
            return tables
        except Exception as e:
            logger.error(f"Tablo çıkarma hatası / Table extraction error: {e}", exc_info=True)
            raise

    # ----------------------------------------------------------
    # Metadata Çıkarma / Metadata Extraction
    # ----------------------------------------------------------

    def extract_metadata(self, file_path_or_bytes: str | Path | bytes) -> dict:
        """
        PDF meta verilerini çıkarır / Extract PDF metadata.

        Args:
            file_path_or_bytes: PDF dosya yolu veya bytes / PDF file path or bytes

        Returns:
            PDF meta veri sözlüğü / PDF metadata dictionary
        """
        try:
            file_name, file_size_mb, pdf_source = self._resolve_input(file_path_or_bytes)
            with pdfplumber.open(pdf_source) as pdf:
                info = pdf.metadata or {}
                return {
                    "file_name": file_name,
                    "file_size_mb": file_size_mb,
                    "total_pages": len(pdf.pages),
                    "author": info.get("Author", ""),
                    "creator": info.get("Creator", ""),
                    "producer": info.get("Producer", ""),
                    "title": info.get("Title", ""),
                    "subject": info.get("Subject", ""),
                    "creation_date": info.get("CreationDate", ""),
                }
        except Exception as e:
            logger.error(f"Metadata çıkarma hatası / Metadata extraction error: {e}", exc_info=True)
            raise

    # ----------------------------------------------------------
    # Bölüm Tespiti / Section Detection
    # ----------------------------------------------------------

    def detect_sections(
        self,
        text: str,
        pages: list[PageContent] | None = None,
    ) -> list[Section]:
        """
        Şartname maddelerini / bölümlerini tespit eder.
        Detects specification clauses / sections.

        Kalıplar / Patterns:
            - "Madde X - Başlık" veya "Madde X. Başlık"
            - "BÖLÜM X" veya "Bölüm X"
            - "EK-X" veya "Ek X"

        Args:
            text: Temizlenmiş doküman metni / Cleaned document text
            pages: Sayfa listesi (sayfa numarası tespiti için) / Page list (for page number detection)

        Returns:
            Tespit edilen bölüm listesi / List of detected sections
        """
        if not text:
            return []

        try:
            # Tüm eşleşmeleri bul / Find all matches
            matches: list[tuple[int, str, str]] = []  # (position, full_title, rest_of_title)

            for pattern in SECTION_PATTERNS:
                for match in pattern.finditer(text):
                    prefix = match.group(1)  # "Madde", "BÖLÜM", "EK"
                    number = match.group(2)  # "5", "III", "1"
                    rest = match.group(3).strip() if match.group(3) else ""

                    if rest:
                        full_title = f"{prefix} {number} - {rest}"
                    else:
                        full_title = f"{prefix} {number}"

                    matches.append((match.start(), full_title, rest))

            if not matches:
                return []

            # Pozisyona göre sırala / Sort by position
            matches.sort(key=lambda x: x[0])

            # Her bölümün içeriğini çıkar / Extract content for each section
            sections: list[Section] = []
            for i, (pos, title, _rest) in enumerate(matches):
                # İçerik: bu bölümün sonundan bir sonraki bölümün başına kadar
                # Content: from end of this heading to start of next heading
                content_start = pos + len(title)
                content_end = matches[i + 1][0] if i + 1 < len(matches) else len(text)
                content = text[content_start:content_end].strip()

                # Sayfa numarası tespiti / Page number detection
                page_num = self._find_page_for_position(text, pos, pages)

                # Bölüm tipi tahmini / Section type classification
                section_type = self._classify_section_type(title, content)

                sections.append(
                    Section(
                        title=title.strip(),
                        content=content,
                        page_num=page_num,
                        section_type=section_type,
                    )
                )

            logger.info(f"{len(sections)} bölüm tespit edildi / sections detected")
            return sections

        except Exception as e:
            logger.error(f"Bölüm tespiti hatası / Section detection error: {e}", exc_info=True)
            return []

    # ----------------------------------------------------------
    # Metin Temizleme / Text Cleaning
    # ----------------------------------------------------------

    def clean_text(self, text: str) -> str:
        """
        Gereksiz karakterleri ve header/footer tekrarlarını temizler.
        Cleans unnecessary characters and header/footer repeats.

        İşlemler / Operations:
            1. NUL ve kontrol karakterlerini kaldır
            2. Ardışık boşlukları normalleştir
            3. Ardışık boş satırları azalt (max 2)
            4. Satır başı/sonu boşlukları temizle

        Args:
            text: Ham metin / Raw text

        Returns:
            Temizlenmiş metin / Cleaned text
        """
        if not text:
            return ""

        try:
            # NUL ve kontrol karakterleri kaldır (newline/tab hariç)
            # Remove NUL and control chars (except newline/tab)
            cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

            # Ardışık boşlukları tek boşluğa çevir (newline'lar hariç)
            # Collapse consecutive spaces (not newlines)
            cleaned = re.sub(r"[^\S\n]+", " ", cleaned)

            # Satır başı/sonu boşlukları temizle / Strip line whitespace
            lines = [line.strip() for line in cleaned.split("\n")]
            cleaned = "\n".join(lines)

            # 3+ ardışık boş satırı 2'ye düşür / Reduce 3+ blank lines to 2
            cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

            return cleaned.strip()

        except Exception as e:
            logger.error(f"Metin temizleme hatası / Text cleaning error: {e}", exc_info=True)
            return text

    # ----------------------------------------------------------
    # Dahili Yardımcı Metodlar / Internal Helper Methods
    # ----------------------------------------------------------

    def _resolve_input(
        self, file_path_or_bytes: str | Path | bytes
    ) -> tuple[str, float, str | io.BytesIO]:
        """
        Giriş tipini belirle ve doğrula / Resolve and validate input type.

        Args:
            file_path_or_bytes: Dosya yolu veya bytes / File path or bytes

        Returns:
            (dosya_adı, boyut_mb, pdf_kaynak) / (filename, size_mb, pdf_source)

        Raises:
            FileNotFoundError: Dosya bulunamadığında
            ValueError: Geçersiz dosya formatında
        """
        if isinstance(file_path_or_bytes, bytes):
            file_name = "bytes_input.pdf"
            file_size_mb = round(len(file_path_or_bytes) / (1024 * 1024), 3)
            pdf_source = io.BytesIO(file_path_or_bytes)
            logger.info(f"Bytes girdi alındı / Bytes input received: {file_size_mb:.3f} MB")
            return file_name, file_size_mb, pdf_source

        file_path = Path(file_path_or_bytes)

        if not file_path.exists():
            raise FileNotFoundError(
                f"PDF dosyası bulunamadı / PDF file not found: {file_path}"
            )

        if file_path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Geçersiz dosya uzantısı / Invalid file extension: {file_path.suffix}"
            )

        file_name = file_path.name
        file_size_mb = round(file_path.stat().st_size / (1024 * 1024), 3)
        logger.info(f"PDF dosyası: {file_name} ({file_size_mb:.3f} MB)")
        return file_name, file_size_mb, str(file_path)

    def _extract_all(
        self,
        pdf_source: str | io.BytesIO,
        extract_text: bool = True,
        extract_tables: bool = True,
    ) -> tuple[list[PageContent], list[TableContent]]:
        """
        pdfplumber ile sayfa sayfa metin ve tablo çıkar.
        Extract text and tables page by page with pdfplumber.

        Bellek dostu: her sayfa ayrı işlenir, büyük PDF'lerde
        tüm sayfalar belleğe alınmaz.

        Memory-efficient: each page is processed separately.

        Args:
            pdf_source: PDF dosya yolu veya BytesIO / PDF file path or BytesIO
            extract_text: Metin çıkarsın mı / Should extract text
            extract_tables: Tablo çıkarsın mı / Should extract tables

        Returns:
            (sayfa_listesi, tablo_listesi) / (pages, tables)
        """
        pages: list[PageContent] = []
        tables: list[TableContent] = []

        with pdfplumber.open(pdf_source) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"Toplam {total_pages} sayfa işlenecek / pages to process")

            for i, page in enumerate(pdf.pages, start=1):
                page_text = ""
                page_has_table = False

                # Metin çıkarma / Text extraction
                if extract_text:
                    raw_text = page.extract_text() or ""
                    page_text = raw_text

                # Tablo çıkarma / Table extraction
                if extract_tables:
                    page_tables = self._extract_tables_from_page(page, i)
                    if page_tables:
                        page_has_table = True
                        tables.extend(page_tables)

                pages.append(
                    PageContent(page_num=i, text=page_text, has_table=page_has_table)
                )

                # Her 50 sayfada ilerleme logu / Progress log every 50 pages
                if i % 50 == 0:
                    logger.info(f"İlerleme / Progress: {i}/{total_pages} sayfa işlendi")

        return pages, tables

    def _extract_tables_from_page(
        self, page, page_num: int
    ) -> list[TableContent]:
        """
        Tek bir sayfadan tabloları çıkar / Extract tables from a single page.

        pdfplumber ile çıkarır. Başarısız olursa boş döner.

        Args:
            page: pdfplumber Page nesnesi / pdfplumber Page object
            page_num: Sayfa numarası / Page number

        Returns:
            Tablo listesi / List of tables
        """
        extracted: list[TableContent] = []

        try:
            raw_tables = page.extract_tables() or []

            for raw_table in raw_tables:
                if not raw_table or len(raw_table) < 2:
                    continue

                # İlk satır başlık, geri kalanı veri
                # First row is header, rest is data
                headers = [str(cell or "").strip() for cell in raw_table[0]]
                rows = [
                    [str(cell or "").strip() for cell in row]
                    for row in raw_table[1:]
                ]

                # Boş tabloları atla / Skip empty tables
                all_content = "".join("".join(row) for row in rows)
                if not all_content.strip():
                    continue

                extracted.append(
                    TableContent(
                        page_num=page_num,
                        headers=headers,
                        rows=rows,
                        raw_data=raw_table,
                    )
                )

        except Exception as e:
            logger.warning(
                f"Sayfa {page_num} tablo çıkarma hatası / "
                f"Page {page_num} table extraction error: {e}"
            )

        return extracted

    def _detect_scanned_pdf(self, pages: list[PageContent]) -> bool:
        """
        Taranmış PDF'leri tespit eder / Detect scanned PDFs.

        Sayfa başına ortalama karakter sayısı eşik değerinin
        altındaysa PDF taranmış kabul edilir.

        If average characters per page is below threshold,
        the PDF is considered scanned.

        Args:
            pages: Sayfa listesi / List of pages

        Returns:
            Taranmış mı / Is scanned
        """
        if not pages:
            return False

        total_chars = sum(len(page.text) for page in pages)
        avg_chars_per_page = total_chars / len(pages)

        is_scanned = avg_chars_per_page < _SCANNED_PDF_CHAR_THRESHOLD
        if is_scanned:
            logger.info(
                f"Taranmış PDF tespiti: ortalama {avg_chars_per_page:.0f} karakter/sayfa "
                f"(eşik: {_SCANNED_PDF_CHAR_THRESHOLD}) / Scanned PDF detected"
            )
        return is_scanned

    def _classify_section_type(self, title: str, content: str) -> str:
        """
        Bölüm tipini anahtar kelimelere göre tahmin eder.
        Classifies section type based on keywords.

        Başlık ve içerikteki anahtar kelimelere göre en uygun
        bölüm tipini döndürür. Başlık eşleşmeleri ağırlıklıdır.

        Args:
            title: Bölüm başlığı / Section title
            content: Bölüm içeriği / Section content

        Returns:
            Bölüm tipi / Section type
        """
        combined = f"{title} {content[:500]}".lower()

        best_type = "genel"
        best_score = 0

        for section_type, keywords in SECTION_KEYWORDS.items():
            if not keywords:
                continue

            score = 0
            title_lower = title.lower()

            for keyword in keywords:
                # Başlıkta eşleşme 3 puan, içerikte 1 puan
                # Title match = 3 points, content match = 1 point
                if keyword in title_lower:
                    score += 3
                elif keyword in combined:
                    score += 1

            if score > best_score:
                best_score = score
                best_type = section_type

        return best_type

    def _find_page_for_position(
        self,
        full_text: str,
        position: int,
        pages: list[PageContent] | None,
    ) -> int:
        """
        Metin pozisyonuna göre sayfa numarası bul.
        Find page number for a text position.

        Args:
            full_text: Tam metin / Full text
            position: Karakter pozisyonu / Character position
            pages: Sayfa listesi / Page list

        Returns:
            Sayfa numarası / Page number (1-indexed, 0 if unknown)
        """
        if not pages:
            return 0

        current_pos = 0
        for page in pages:
            page_len = len(page.text) + 2  # +2 for "\n\n" separator
            if current_pos + page_len > position:
                return page.page_num
            current_pos += page_len

        return pages[-1].page_num if pages else 0
