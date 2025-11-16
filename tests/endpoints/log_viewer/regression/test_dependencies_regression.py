"""
Regression tests for log_viewer presentation dependencies.

Ensures that dependency injection functions continue to work correctly.
"""

from unittest.mock import Mock

import pytest

from src.endpoints.log_viewer.presentation.dependencies import (
    get_query_uptime_use_case,
)


class TestDependenciesRegression:
    """Regression tests for FastAPI dependencies."""

    @pytest.mark.regression
    def test_get_query_uptime_use_case_returns_query_uptime_instance(self):
        """Test that get_query_uptime_use_case returns QueryUptime instance."""
        # Test line 74: get_query_uptime_use_case return statement
        # Arrange
        mock_repository = Mock()

        # Act
        use_case = get_query_uptime_use_case(repository=mock_repository)

        # Assert
        assert use_case is not None
        assert hasattr(use_case, "execute")
        assert use_case._repository == mock_repository

