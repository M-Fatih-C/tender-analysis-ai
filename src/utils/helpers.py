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


# ============================================================
# Modül 2'de eklenen fonksiyonlar / Functions added in Module 2
# ============================================================


def normalize_whitespace(text: str) -> str:
    """
    Ardışık boşluk ve newline'ları normalleştir / Normalize consecutive whitespace and newlines.

    Birden fazla ardışık boşluğu tek boşluğa,
    birden fazla ardışık boş satırı tek boş satıra dönüştürür.

    Collapses multiple consecutive spaces into one space,
    and multiple consecutive blank lines into a single blank line.

    Args:
        text: Ham metin / Raw text

    Returns:
        Normalleştirilmiş metin / Normalized text

    Examples:
        >>> normalize_whitespace("merhaba    dünya")
        'merhaba dünya'
        >>> normalize_whitespace("satır1\\n\\n\\n\\nsatır2")
        'satır1\\n\\nsatır2'
    """
    if not text:
        return ""

    # Ardışık boşlukları tek boşluğa (newline hariç)
    # Collapse consecutive spaces (not newlines)
    normalized = re.sub(r"[^\S\n]+", " ", text)

    # 3+ ardışık newline'ı 2'ye düşür / Reduce 3+ newlines to 2
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)

    return normalized.strip()


def remove_header_footer_repeats(
    pages_text: list[str],
    min_repeat_ratio: float = 0.6,
    max_line_length: int = 120,
) -> list[str]:
    """
    Sayfalarda tekrar eden header/footer satırlarını kaldırır.
    Removes header/footer lines that repeat across pages.

    Her sayfanın ilk ve son birkaç satırını kontrol eder.
    Sayfaların belirli bir oranında (varsayılan %60) aynı satır
    tekrar ediyorsa, header/footer olarak kabul edilir ve kaldırılır.

    Checks first and last few lines of each page. If the same line
    repeats in a certain ratio of pages (default 60%), it's considered
    a header/footer and removed.

    Args:
        pages_text: Sayfa metinleri listesi / List of page texts
        min_repeat_ratio: Minimum tekrar oranı (0-1) / Minimum repeat ratio
        max_line_length: Bu uzunluktan uzun satırlar atlanır / Lines longer than this are skipped

    Returns:
        Temizlenmiş sayfa metinleri / Cleaned page texts

    Examples:
        >>> pages = ["Header\\nİçerik 1\\nFooter", "Header\\nİçerik 2\\nFooter"]
        >>> remove_header_footer_repeats(pages, min_repeat_ratio=0.5)
        ['İçerik 1', 'İçerik 2']
    """
    if len(pages_text) < 3:
        # Çok az sayfa varsa güvenilir tespit yapılamaz
        # Too few pages for reliable detection
        return pages_text

    # Her sayfanın ilk 3 ve son 3 satırını topla / Collect first/last 3 lines
    check_lines = 3
    candidate_lines: dict[str, int] = {}

    for page_text in pages_text:
        lines = page_text.strip().split("\n")
        check_from = lines[:check_lines] + lines[-check_lines:]

        seen_on_this_page: set[str] = set()
        for line in check_from:
            stripped = line.strip()
            if (
                stripped
                and len(stripped) <= max_line_length
                and stripped not in seen_on_this_page
            ):
                seen_on_this_page.add(stripped)
                candidate_lines[stripped] = candidate_lines.get(stripped, 0) + 1

    # Eşik üstündeki satırları header/footer olarak işaretle
    # Mark lines above threshold as header/footer
    total_pages = len(pages_text)
    repeating_lines: set[str] = {
        line
        for line, count in candidate_lines.items()
        if count / total_pages >= min_repeat_ratio
    }

    if not repeating_lines:
        return pages_text

    # Tekrar eden satırları kaldır / Remove repeating lines
    cleaned_pages: list[str] = []
    for page_text in pages_text:
        lines = page_text.strip().split("\n")
        filtered = [line for line in lines if line.strip() not in repeating_lines]
        cleaned_pages.append("\n".join(filtered).strip())

    return cleaned_pages


# ============================================================
# Modül 9'da eklenen fonksiyonlar / Functions added in Module 9
# ============================================================


def format_risk_score(score: int | None) -> str:
    """
    Risk skorunu emoji ile formatla / Format risk score with emoji.

    Args:
        score: Risk skoru (0-100) / Risk score (0-100)

    Returns:
        Formatlı skor / Formatted score

    Examples:
        >>> format_risk_score(78)
        '78 🔴'
        >>> format_risk_score(45)
        '45 🟡'
        >>> format_risk_score(20)
        '20 🟢'
    """
    if score is None:
        return "— ⚪"
    if score <= 40:
        return f"{score} 🟢"
    elif score <= 70:
        return f"{score} 🟡"
    else:
        return f"{score} 🔴"


def risk_color(score: int | None) -> str:
    """
    Risk skoruna göre hex renk döndür / Return hex color for risk score.

    Args:
        score: Risk skoru (0-100) / Risk score

    Returns:
        Hex renk kodu / Hex color code

    Examples:
        >>> risk_color(20)
        '#27ae60'
        >>> risk_color(55)
        '#f39c12'
        >>> risk_color(85)
        '#e74c3c'
    """
    if score is None:
        return "#95a5a6"
    if score <= 40:
        return "#27ae60"
    elif score <= 70:
        return "#f39c12"
    else:
        return "#e74c3c"


_TURKISH_MONTHS = [
    "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
]
_TURKISH_DAYS = [
    "Pazartesi", "Salı", "Çarşamba", "Perşembe",
    "Cuma", "Cumartesi", "Pazar",
]


def format_date_turkish(dt: datetime | None) -> str:
    """
    Türkçe tarih formatı / Turkish date format.

    Args:
        dt: datetime nesnesi / datetime object

    Returns:
        '12 Haziran 2025, Perşembe' formatı

    Examples:
        >>> from datetime import datetime
        >>> format_date_turkish(datetime(2025, 6, 12))
        '12 Haziran 2025, Perşembe'
    """
    if dt is None:
        return "—"
    day_name = _TURKISH_DAYS[dt.weekday()]
    month_name = _TURKISH_MONTHS[dt.month]
    return f"{dt.day} {month_name} {dt.year}, {day_name}"


def format_file_size_mb(size_mb: float | None) -> str:
    """
    MB cinsinden dosya boyutunu formatla / Format file size in MB.

    Args:
        size_mb: Boyut (MB) / Size in MB

    Returns:
        Formatlı boyut / Formatted size

    Examples:
        >>> format_file_size_mb(1.567)
        '1.6 MB'
        >>> format_file_size_mb(0.003)
        '3 KB'
    """
    if size_mb is None:
        return "—"
    if size_mb < 0.01:
        return f"{size_mb * 1024:.0f} KB"
    elif size_mb < 1:
        return f"{size_mb * 1024:.0f} KB"
    else:
        return f"{size_mb:.1f} MB"


def time_ago(dt: datetime | None) -> str:
    """
    Geçen süreyi Türkçe olarak döndür / Return elapsed time in Turkish.

    Args:
        dt: Geçmiş zaman / Past datetime

    Returns:
        '2 saat önce', '3 gün önce' gibi / Like '2 hours ago'

    Examples:
        >>> from datetime import datetime, timedelta
        >>> time_ago(datetime.now() - timedelta(hours=2))
        '2 saat önce'
    """
    if dt is None:
        return "—"

    now = datetime.now(dt.tzinfo)
    diff = now - dt

    seconds = int(diff.total_seconds())
    if seconds < 0:
        return "az önce"

    if seconds < 60:
        return "az önce"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} dakika önce"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} saat önce"
    elif seconds < 2592000:  # 30 gün
        days = seconds // 86400
        return f"{days} gün önce"
    elif seconds < 31536000:  # 365 gün
        months = seconds // 2592000
        return f"{months} ay önce"
    else:
        years = seconds // 31536000
        return f"{years} yıl önce"
