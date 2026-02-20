"""
TenderAI Modül 9 Helper Testleri / Module 9 Helper Tests.

format_risk_score, risk_color, format_date_turkish,
format_file_size_mb ve time_ago fonksiyonları için testler.
"""

import pytest
from datetime import datetime, timedelta

from src.utils.helpers import (
    format_risk_score,
    risk_color,
    format_date_turkish,
    format_file_size_mb,
    time_ago,
)


# ============================================================
# format_risk_score
# ============================================================


class TestFormatRiskScore:
    def test_low(self) -> None:
        assert "🟢" in format_risk_score(20)
        assert "20" in format_risk_score(20)

    def test_medium(self) -> None:
        assert "🟡" in format_risk_score(55)

    def test_high(self) -> None:
        assert "🔴" in format_risk_score(85)

    def test_boundary_40(self) -> None:
        assert "🟢" in format_risk_score(40)

    def test_boundary_70(self) -> None:
        assert "🟡" in format_risk_score(70)

    def test_boundary_71(self) -> None:
        assert "🔴" in format_risk_score(71)

    def test_none(self) -> None:
        result = format_risk_score(None)
        assert "⚪" in result

    def test_zero(self) -> None:
        assert "🟢" in format_risk_score(0)

    def test_hundred(self) -> None:
        assert "🔴" in format_risk_score(100)


# ============================================================
# risk_color
# ============================================================


class TestRiskColor:
    def test_low_green(self) -> None:
        assert risk_color(20) == "#27ae60"

    def test_medium_orange(self) -> None:
        assert risk_color(55) == "#f39c12"

    def test_high_red(self) -> None:
        assert risk_color(85) == "#e74c3c"

    def test_none_gray(self) -> None:
        assert risk_color(None) == "#95a5a6"

    def test_boundary_40(self) -> None:
        assert risk_color(40) == "#27ae60"

    def test_boundary_41(self) -> None:
        assert risk_color(41) == "#f39c12"


# ============================================================
# format_date_turkish
# ============================================================


class TestFormatDateTurkish:
    def test_known_date(self) -> None:
        dt = datetime(2025, 6, 12)  # Perşembe
        result = format_date_turkish(dt)
        assert "12" in result
        assert "Haziran" in result
        assert "2025" in result
        assert "Perşembe" in result

    def test_january(self) -> None:
        dt = datetime(2025, 1, 1)
        assert "Ocak" in format_date_turkish(dt)

    def test_none(self) -> None:
        assert format_date_turkish(None) == "—"


# ============================================================
# format_file_size_mb
# ============================================================


class TestFormatFileSizeMb:
    def test_large_mb(self) -> None:
        assert "1.6 MB" in format_file_size_mb(1.567)

    def test_small_kb(self) -> None:
        result = format_file_size_mb(0.5)
        assert "KB" in result

    def test_none(self) -> None:
        assert format_file_size_mb(None) == "—"

    def test_exact_1mb(self) -> None:
        assert "1.0 MB" in format_file_size_mb(1.0)


# ============================================================
# time_ago
# ============================================================


class TestTimeAgo:
    def test_just_now(self) -> None:
        result = time_ago(datetime.now() - timedelta(seconds=5))
        assert "az önce" in result

    def test_minutes(self) -> None:
        result = time_ago(datetime.now() - timedelta(minutes=30))
        assert "dakika önce" in result

    def test_hours(self) -> None:
        result = time_ago(datetime.now() - timedelta(hours=3))
        assert "saat önce" in result

    def test_days(self) -> None:
        result = time_ago(datetime.now() - timedelta(days=5))
        assert "gün önce" in result

    def test_months(self) -> None:
        result = time_ago(datetime.now() - timedelta(days=60))
        assert "ay önce" in result

    def test_years(self) -> None:
        result = time_ago(datetime.now() - timedelta(days=400))
        assert "yıl önce" in result

    def test_none(self) -> None:
        assert time_ago(None) == "—"
