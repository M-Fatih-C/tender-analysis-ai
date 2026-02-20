"""
TenderAI Yardımcı Fonksiyonlar / Helper Functions.
"""

import json
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def format_risk_score(score: int) -> str:
    """78 → '78 🔴'"""
    if score <= 40:
        return f"{score} 🟢"
    elif score <= 70:
        return f"{score} 🟡"
    else:
        return f"{score} 🔴"


def risk_color_hex(score: int) -> str:
    """Score'a göre hex renk."""
    if score <= 30:
        return "#27ae60"
    elif score <= 50:
        return "#2ecc71"
    elif score <= 70:
        return "#f39c12"
    elif score <= 85:
        return "#e74c3c"
    else:
        return "#c0392b"


def risk_level_text(score: int) -> str:
    """Score'a göre Türkçe seviye metni."""
    if score <= 30:
        return "DÜŞÜK"
    elif score <= 50:
        return "ORTA"
    elif score <= 70:
        return "YÜKSEK"
    else:
        return "ÇOK YÜKSEK"


def risk_emoji(score: int) -> str:
    """Score'a göre emoji."""
    if score <= 40:
        return "🟢"
    elif score <= 70:
        return "🟡"
    else:
        return "🔴"


_MONTHS_TR = [
    "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
]
_DAYS_TR = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]


def format_date_turkish(dt: datetime | None) -> str:
    """12 Haziran 2025, Perşembe."""
    if not dt:
        return "—"
    try:
        return f"{dt.day} {_MONTHS_TR[dt.month]} {dt.year}, {_DAYS_TR[dt.weekday()]}"
    except Exception:
        return str(dt)


def time_ago_turkish(dt: datetime | None) -> str:
    """2 saat önce, 3 gün önce."""
    if not dt:
        return "—"
    try:
        now = datetime.now()
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "Az önce"
        elif seconds < 3600:
            return f"{seconds // 60} dakika önce"
        elif seconds < 86400:
            return f"{seconds // 3600} saat önce"
        elif seconds < 604800:
            return f"{seconds // 86400} gün önce"
        else:
            return format_date_turkish(dt)
    except Exception:
        return "—"


def format_currency_try(amount) -> str:
    """85000000 → '85.000.000 TL'."""
    try:
        if amount is None:
            return "—"
        n = float(amount)
        if n >= 1_000_000:
            formatted = f"{n:,.0f}".replace(",", ".")
        else:
            formatted = f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted} TL"
    except Exception:
        return f"{amount} TL"


def format_file_size(size_mb: float) -> str:
    """1.5 → '1.5 MB'."""
    try:
        if size_mb < 1:
            return f"{int(size_mb * 1024)} KB"
        return f"{size_mb:.1f} MB"
    except Exception:
        return f"{size_mb} MB"


def truncate_text(text: str, max_len: int = 100) -> str:
    """Uzun metni kısalt."""
    if not text:
        return ""
    return text[:max_len] + "..." if len(text) > max_len else text


def safe_json_parse(text) -> dict:
    """String veya dict'i güvenli şekilde dict'e çevir."""
    if isinstance(text, dict):
        return text
    if isinstance(text, str):
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


def get_turkish_cities() -> list[str]:
    """81 il listesi (A-Z sıralı)."""
    return [
        "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya",
        "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir",
        "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis",
        "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum",
        "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan",
        "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari",
        "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", "Kahramanmaraş",
        "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale",
        "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya",
        "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş",
        "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya",
        "Samsun", "Şanlıurfa", "Siirt", "Sinop", "Sivas", "Şırnak",
        "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van",
        "Yalova", "Yozgat", "Zonguldak",
    ]


def generate_avatar_initials(name: str) -> str:
    """'Mehmet Yılmaz' → 'MY'."""
    if not name:
        return "?"
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return parts[0][0].upper()


def calculate_password_strength(password: str) -> dict:
    """Şifre güçlülük analizi."""
    if not password:
        return {"score": 0, "label": "—", "color": "#555"}

    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[0-9]", password):
        score += 1
    if re.search(r"[^A-Za-z0-9]", password):
        score += 1

    if score <= 1:
        return {"score": score, "label": "Zayıf", "color": "#e74c3c"}
    elif score <= 3:
        return {"score": score, "label": "Orta", "color": "#f39c12"}
    else:
        return {"score": score, "label": "Güçlü", "color": "#27ae60"}
