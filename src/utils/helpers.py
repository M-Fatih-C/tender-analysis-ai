"""
TenderAI Yardımcı Fonksiyonlar / Helper Functions.

Projede sıkça kullanılan yardımcı fonksiyonları içerir.
Contains frequently used helper functions throughout the project.
"""

import re
import uuid
from datetime import datetime
from pathlib import Path


def format_file_size(size_bytes: int) -> str:
    """
    Dosya boyutunu okunabilir formata çevir / Convert file size to human-readable format.

    Args:
        size_bytes: Bayt cinsinden dosya boyutu / File size in bytes

    Returns:
        Okunabilir dosya boyutu / Human-readable file size

    Examples:
        >>> format_file_size(1024)
        '1.00 KB'
        >>> format_file_size(1048576)
        '1.00 MB'
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def generate_unique_filename(original_filename: str) -> str:
    """
    Benzersiz dosya adı oluştur / Generate unique filename.

    Orijinal dosya adına UUID ve zaman damgası ekler.
    Appends UUID and timestamp to the original filename.

    Args:
        original_filename: Orijinal dosya adı / Original filename

    Returns:
        Benzersiz dosya adı / Unique filename

    Examples:
        >>> generate_unique_filename("sartname.pdf")
        '20260220_143052_a1b2c3d4_sartname.pdf'
    """
    stem = Path(original_filename).stem
    suffix = Path(original_filename).suffix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{timestamp}_{unique_id}_{stem}{suffix}"


def validate_pdf_file(file_path: str | Path, max_size_mb: int = 50) -> tuple[bool, str]:
    """
    PDF dosyasını doğrula / Validate PDF file.

    Dosya varlığını, uzantısını ve boyutunu kontrol eder.
    Checks file existence, extension, and size.

    Args:
        file_path: Dosya yolu / File path
        max_size_mb: Maksimum dosya boyutu (MB) / Maximum file size (MB)

    Returns:
        (geçerli mi, hata mesajı) / (is valid, error message)

    Examples:
        >>> validate_pdf_file("sartname.pdf")
        (True, '')
    """
    path = Path(file_path)

    if not path.exists():
        return False, "Dosya bulunamadı / File not found"

    if path.suffix.lower() != ".pdf":
        return False, "Sadece PDF dosyaları kabul edilir / Only PDF files are accepted"

    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False, f"Dosya boyutu {max_size_mb}MB'ı aşıyor / File size exceeds {max_size_mb}MB"

    return True, ""


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Metni belirtilen uzunlukta kes / Truncate text to specified length.

    Args:
        text: Kesilecek metin / Text to truncate
        max_length: Maksimum uzunluk / Maximum length
        suffix: Kesme soneki / Truncation suffix

    Returns:
        Kesilmiş metin / Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Dosya adını güvenli hale getir / Sanitize filename.

    Özel karakterleri ve Türkçe karakterleri düzenler.
    Handles special characters and Turkish characters.

    Args:
        filename: Ham dosya adı / Raw filename

    Returns:
        Güvenli dosya adı / Sanitized filename
    """
    # Türkçe karakter dönüşümü / Turkish character mapping
    tr_map = str.maketrans(
        "çğıöşüÇĞİÖŞÜ",
        "cgiosuCGIOSU",
    )
    filename = filename.translate(tr_map)

    # Güvenli olmayan karakterleri kaldır / Remove unsafe characters
    filename = re.sub(r'[^\w\s\-.]', '', filename)
    filename = re.sub(r'\s+', '_', filename)

    return filename


def get_current_timestamp() -> str:
    """
    Şu anki zaman damgasını döndür / Return current timestamp.

    Returns:
        ISO 8601 formatında zaman damgası / Timestamp in ISO 8601 format
    """
    return datetime.now().isoformat()


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Tahmini okuma süresini hesapla / Calculate estimated reading time.

    Args:
        text: Metin / Text
        words_per_minute: Dakika başına kelime / Words per minute

    Returns:
        Tahmini okuma süresi (dakika) / Estimated reading time (minutes)
    """
    word_count = len(text.split())
    return max(1, round(word_count / words_per_minute))
