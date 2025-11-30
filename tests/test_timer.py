"""Unit tests for timer functionality."""

import pytest

from main import format_time


class TestFormatTime:
    """Tests for the format_time function."""

    def test_zero_seconds(self):
        """Zero seconds should format as 00:00.0."""
        assert format_time(0.0) == "00:00.0"

    def test_tenths_only(self):
        """Sub-second times should show tenths correctly."""
        assert format_time(0.1) == "00:00.1"
        assert format_time(0.5) == "00:00.5"
        assert format_time(0.9) == "00:00.9"

    def test_seconds_only(self):
        """Times under a minute should format correctly."""
        assert format_time(1.0) == "00:01.0"
        assert format_time(5.0) == "00:05.0"
        assert format_time(10.0) == "00:10.0"
        assert format_time(59.0) == "00:59.0"

    def test_seconds_with_tenths(self):
        """Seconds with tenths should format correctly."""
        assert format_time(1.5) == "00:01.5"
        assert format_time(12.3) == "00:12.3"
        assert format_time(45.7) == "00:45.7"

    def test_minutes(self):
        """Times over a minute should show minutes."""
        assert format_time(60.0) == "01:00.0"
        assert format_time(90.0) == "01:30.0"
        assert format_time(120.0) == "02:00.0"

    def test_minutes_with_seconds_and_tenths(self):
        """Full format with minutes, seconds, and tenths."""
        assert format_time(61.5) == "01:01.5"
        assert format_time(123.4) == "02:03.4"
        assert format_time(599.9) == "09:59.9"

    def test_double_digit_minutes(self):
        """Times over 10 minutes should show double-digit minutes."""
        assert format_time(600.0) == "10:00.0"
        assert format_time(3599.9) == "59:59.9"

    def test_truncates_to_tenths(self):
        """Times should truncate (not round) to tenths."""
        # 0.99 should show as 0.9, not 1.0
        assert format_time(0.99) == "00:00.9"
        # 1.99 should show as 1.9, not 2.0
        assert format_time(1.99) == "00:01.9"

    def test_very_long_times(self):
        """Very long times should still format correctly."""
        # 1 hour = 3600 seconds = 60:00.0
        assert format_time(3600.0) == "60:00.0"
        # 99 minutes 59 seconds
        assert format_time(5999.9) == "99:59.9"

    def test_negative_time_edge_case(self):
        """Negative time (edge case) should handle gracefully."""
        # This shouldn't happen in practice, but the function should not crash
        result = format_time(-1.0)
        # Python's int() truncates toward zero, so -1.0 // 60 = -1, % 60 = 59
        # This is a known behavior; we just verify it doesn't crash
        assert isinstance(result, str)
