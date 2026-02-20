"""
TenderAI Helper Testleri / Helper Tests.
"""

import pytest
from datetime import datetime, timedelta

from src.utils.helpers import (
    format_risk_score,
    risk_color_hex,
    format_date_turkish,
    format_file_size,
    time_ago_turkish,
    format_currency_try,
    safe_json_parse,
    generate_avatar_initials,
    calculate_password_strength,
    get_turkish_cities,
    truncate_text,
)


class TestFormatRiskScore:
    def test_low(self) -> None:
        assert "🟢" in format_risk_score(20)

    def test_medium(self) -> None:
        assert "🟡" in format_risk_score(55)

    def test_high(self) -> None:
        assert "🔴" in format_risk_score(85)

    def test_boundary_40(self) -> None:
        assert "🟢" in format_risk_score(40)

    def test_boundary_71(self) -> None:
        assert "🔴" in format_risk_score(71)

    def test_zero(self) -> None:
        assert "🟢" in format_risk_score(0)


class TestRiskColorHex:
    def test_low_green(self) -> None:
        assert risk_color_hex(20) == "#27ae60"

    def test_medium_orange(self) -> None:
        assert risk_color_hex(55) == "#f39c12"

    def test_high_red(self) -> None:
        assert risk_color_hex(85) == "#e74c3c"


class TestFormatDateTurkish:
    def test_known_date(self) -> None:
        dt = datetime(2025, 6, 12)
        result = format_date_turkish(dt)
        assert "12" in result
        assert "Haziran" in result
        assert "2025" in result

    def test_none(self) -> None:
        assert format_date_turkish(None) == "—"


class TestFormatFileSize:
    def test_large_mb(self) -> None:
        assert "MB" in format_file_size(1.5)

    def test_small_kb(self) -> None:
        assert "KB" in format_file_size(0.5)


class TestTimeAgoTurkish:
    def test_just_now(self) -> None:
        assert "Az önce" in time_ago_turkish(datetime.now() - timedelta(seconds=5))

    def test_minutes(self) -> None:
        assert "dakika önce" in time_ago_turkish(datetime.now() - timedelta(minutes=30))

    def test_hours(self) -> None:
        assert "saat önce" in time_ago_turkish(datetime.now() - timedelta(hours=3))

    def test_days(self) -> None:
        assert "gün önce" in time_ago_turkish(datetime.now() - timedelta(days=5))

    def test_none(self) -> None:
        assert time_ago_turkish(None) == "—"


class TestFormatCurrencyTry:
    def test_large(self) -> None:
        assert "TL" in format_currency_try(85_000_000)

    def test_none(self) -> None:
        assert format_currency_try(None) == "—"


class TestSafeJsonParse:
    def test_dict(self) -> None:
        assert safe_json_parse({"a": 1}) == {"a": 1}

    def test_string(self) -> None:
        assert safe_json_parse('{"a": 1}') == {"a": 1}

    def test_invalid(self) -> None:
        assert safe_json_parse("not json") == {}


class TestGenerateAvatarInitials:
    def test_full_name(self) -> None:
        assert generate_avatar_initials("Mehmet Yılmaz") == "MY"

    def test_single_name(self) -> None:
        assert generate_avatar_initials("Ali") == "A"

    def test_empty(self) -> None:
        assert generate_avatar_initials("") == "?"


class TestPasswordStrength:
    def test_weak(self) -> None:
        assert calculate_password_strength("abc")["label"] == "Zayıf"

    def test_strong(self) -> None:
        result = calculate_password_strength("MyP@ssw0rd1234!")
        assert result["label"] == "Güçlü"


class TestTurkishCities:
    def test_count(self) -> None:
        assert len(get_turkish_cities()) == 81

    def test_istanbul(self) -> None:
        assert "İstanbul" in get_turkish_cities()


class TestTruncateText:
    def test_short(self) -> None:
        assert truncate_text("abc", 10) == "abc"

    def test_long(self) -> None:
        assert truncate_text("a" * 200, 10) == "a" * 10 + "..."
