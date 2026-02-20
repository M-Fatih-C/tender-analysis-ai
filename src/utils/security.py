"""
TenderAI Güvenlik Modülü / Security Module.

Input sanitization, XSS koruması, dosya güvenliği.
"""

import hashlib
import html
import logging
import re
import struct

logger = logging.getLogger(__name__)

# İzin verilen MIME tipleri
ALLOWED_MIME_TYPES = {
    "application/pdf": [b"%PDF"],
}

# Zararlı pattern'ler
_DANGEROUS_PATTERNS = [
    r"<script[^>]*>",
    r"javascript:",
    r"on\w+\s*=",
    r"data:text/html",
    r"vbscript:",
    r"expression\s*\(",
]
_DANGEROUS_RE = re.compile("|".join(_DANGEROUS_PATTERNS), re.IGNORECASE)

# SQL injection pattern'leri
_SQL_PATTERNS = [
    r"\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|EXEC|EXECUTE)\b.*\b(FROM|INTO|TABLE|WHERE|SET)\b",
    r"('|\")\s*(OR|AND)\s+\d+\s*=\s*\d+",
    r";\s*(DROP|DELETE|UPDATE|INSERT)\s",
]
_SQL_RE = re.compile("|".join(_SQL_PATTERNS), re.IGNORECASE)


def sanitize_html(text: str) -> str:
    """HTML escape — XSS koruması."""
    if not text:
        return ""
    return html.escape(str(text), quote=True)


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Kullanıcı girdisini temizle."""
    if not text:
        return ""
    text = str(text).strip()
    text = text[:max_length]
    # Zararlı pattern'leri temizle
    text = _DANGEROUS_RE.sub("", text)
    return text


def sanitize_filename(filename: str) -> str:
    """Dosya adını güvenli hale getir."""
    if not filename:
        return "dosya"
    # Path traversal
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")
    # Sadece güvenli karakterler
    safe = re.sub(r"[^\w\s\-\.\(\)]", "_", filename)
    return safe[:100] or "dosya"


def check_sql_injection(text: str) -> bool:
    """SQL injection kontrolü. True = tehlikeli."""
    if not text:
        return False
    return bool(_SQL_RE.search(text))


def validate_file_magic(file_bytes: bytes, expected_mime: str = "application/pdf") -> bool:
    """Magic bytes ile dosya tipini doğrula."""
    if not file_bytes or len(file_bytes) < 4:
        return False

    magic_list = ALLOWED_MIME_TYPES.get(expected_mime, [])
    for magic in magic_list:
        if file_bytes[:len(magic)] == magic:
            return True
    return False


def validate_file_size(file_bytes: bytes, max_mb: float = 50.0) -> bool:
    """Dosya boyutunu kontrol et."""
    max_bytes = int(max_mb * 1024 * 1024)
    return len(file_bytes) <= max_bytes


def hash_file(file_bytes: bytes) -> str:
    """Dosyanın SHA-256 hash'ini döndür."""
    return hashlib.sha256(file_bytes).hexdigest()


def validate_upload(file_bytes: bytes, filename: str, max_mb: float = 50.0) -> tuple[bool, str]:
    """
    Dosya yükleme doğrulama — magic bytes, boyut, uzantı.

    Returns:
        (geçerli_mi, hata_mesajı)
    """
    if not file_bytes:
        return False, "Dosya boş"

    if not validate_file_size(file_bytes, max_mb):
        return False, f"Dosya boyutu {max_mb}MB'ı aşıyor"

    if not filename.lower().endswith(".pdf"):
        return False, "Sadece PDF dosyaları kabul edilir"

    if not validate_file_magic(file_bytes, "application/pdf"):
        return False, "Dosya geçerli bir PDF değil (magic bytes)"

    return True, ""
