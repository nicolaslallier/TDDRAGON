"""
Unit tests for presentation dependencies.

Tests for dependency injection functions.
"""

from unittest.mock import Mock

import pytest

from src.endpoints.log_collector.application.collect_logs import CollectLogs
from src.endpoints.log_collector.presentation.dependencies import (
    get_collect_logs_use_case,
)


class TestDependencies:
    """Test suite for dependency functions."""

    @pytest.mark.unit
    def test_get_collect_logs_use_case_returns_collect_logs_instance(self):
        """Test that get_collect_logs_use_case returns CollectLogs instance."""
        # Arrange
        mock_repository = Mock()

        # Act
        use_case = get_collect_logs_use_case(repository=mock_repository)

        # Assert
        assert isinstance(use_case, CollectLogs)
        assert use_case._repository is mock_repository
