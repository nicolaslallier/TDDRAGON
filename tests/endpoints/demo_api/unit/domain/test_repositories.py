"""
Unit tests for repository interfaces.

Tests for the DemoItemRepository interface and its contract.
"""

from typing import Protocol

from src.endpoints.demo_api.domain.repositories import DemoItemRepository


class TestDemoItemRepository:
    """Test suite for DemoItemRepository interface."""

    def test_repository_is_protocol(self):
        """Test that DemoItemRepository is a Protocol."""
        # Assert
        assert isinstance(DemoItemRepository, type(Protocol))

    def test_repository_has_create_method(self):
        """Test that DemoItemRepository has a create method."""
        # Assert
        assert hasattr(DemoItemRepository, "create")

    def test_repository_has_find_all_method(self):
        """Test that DemoItemRepository has a find_all method."""
        # Assert
        assert hasattr(DemoItemRepository, "find_all")
