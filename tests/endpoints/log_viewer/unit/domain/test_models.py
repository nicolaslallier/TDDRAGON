"""
Unit tests for log_viewer domain models.

Tests domain model imports and re-exports.
"""

import pytest

from src.endpoints.log_viewer.domain.models import LogEntry, UptimeRecord


class TestModels:
    """Test suite for log_viewer domain models."""

    @pytest.mark.unit
    def test_log_entry_is_imported(self):
        """Test that LogEntry is imported from log_collector."""
        # Assert
        assert LogEntry is not None
        # Verify it's the same class from log_collector
        from src.endpoints.log_collector.domain.models import LogEntry as CollectorLogEntry

        assert LogEntry is CollectorLogEntry

    @pytest.mark.unit
    def test_uptime_record_is_imported(self):
        """Test that UptimeRecord is imported from log_collector."""
        # Assert
        assert UptimeRecord is not None
        # Verify it's the same class from log_collector
        from src.endpoints.log_collector.domain.models import UptimeRecord as CollectorUptimeRecord

        assert UptimeRecord is CollectorUptimeRecord

    @pytest.mark.unit
    def test_all_exports_are_defined(self):
        """Test that __all__ exports are defined."""
        # Arrange
        from src.endpoints.log_viewer.domain.models import __all__

        # Assert
        assert "LogEntry" in __all__
        assert "UptimeRecord" in __all__

