"""
Unit tests for log_viewer presentation schemas.

Tests Pydantic schemas for API requests.
"""

import pytest
from pydantic import ValidationError

from src.endpoints.log_viewer.presentation.schemas import (
    FilterLogsRequest,
    LoginRequest,
    QueryUptimeRequest,
)


class TestFilterLogsRequest:
    """Test suite for FilterLogsRequest schema."""

    @pytest.mark.unit
    def test_valid_request_creates_instance(self):
        """Test that valid request data creates an instance."""
        # Arrange & Act
        request = FilterLogsRequest(
            start_time="2024-01-01T00:00:00",
            end_time="2024-01-01T23:59:59",
            status_code=200,
            uri="/health",
            client_ip="192.168.1.1",
            page=1,
            page_size=50,
        )

        # Assert
        assert request.start_time == "2024-01-01T00:00:00"
        assert request.end_time == "2024-01-01T23:59:59"
        assert request.status_code == 200
        assert request.uri == "/health"
        assert request.client_ip == "192.168.1.1"
        assert request.page == 1
        assert request.page_size == 50

    @pytest.mark.unit
    def test_minimal_request_creates_instance_with_defaults(self):
        """Test that minimal request data creates an instance with defaults."""
        # Arrange & Act
        request = FilterLogsRequest(
            start_time="2024-01-01T00:00:00",
            end_time="2024-01-01T23:59:59",
        )

        # Assert
        assert request.start_time == "2024-01-01T00:00:00"
        assert request.end_time == "2024-01-01T23:59:59"
        assert request.status_code is None
        assert request.uri is None
        assert request.client_ip is None
        assert request.page == 1
        assert request.page_size == 50

    @pytest.mark.unit
    def test_missing_required_fields_raises_validation_error(self):
        """Test that missing required fields raises ValidationError."""
        # Act & Assert
        with pytest.raises(ValidationError):
            FilterLogsRequest(start_time="2024-01-01T00:00:00")

    @pytest.mark.unit
    def test_invalid_page_raises_validation_error(self):
        """Test that invalid page number raises ValidationError."""
        # Act & Assert
        with pytest.raises(ValidationError):
            FilterLogsRequest(
                start_time="2024-01-01T00:00:00",
                end_time="2024-01-01T23:59:59",
                page=0,  # Must be >= 1
            )

    @pytest.mark.unit
    def test_invalid_page_size_raises_validation_error(self):
        """Test that invalid page size raises ValidationError."""
        # Act & Assert
        with pytest.raises(ValidationError):
            FilterLogsRequest(
                start_time="2024-01-01T00:00:00",
                end_time="2024-01-01T23:59:59",
                page_size=0,  # Must be >= 1
            )

    @pytest.mark.unit
    def test_page_size_exceeds_maximum_raises_validation_error(self):
        """Test that page size exceeding maximum raises ValidationError."""
        # Act & Assert
        with pytest.raises(ValidationError):
            FilterLogsRequest(
                start_time="2024-01-01T00:00:00",
                end_time="2024-01-01T23:59:59",
                page_size=101,  # Must be <= 100
            )


class TestQueryUptimeRequest:
    """Test suite for QueryUptimeRequest schema."""

    @pytest.mark.unit
    def test_valid_request_creates_instance(self):
        """Test that valid request data creates an instance."""
        # Arrange & Act
        request = QueryUptimeRequest(
            start_time="2024-01-01T00:00:00",
            end_time="2024-01-01T23:59:59",
        )

        # Assert
        assert request.start_time == "2024-01-01T00:00:00"
        assert request.end_time == "2024-01-01T23:59:59"

    @pytest.mark.unit
    def test_missing_start_time_raises_validation_error(self):
        """Test that missing start_time raises ValidationError."""
        # Act & Assert
        with pytest.raises(ValidationError):
            QueryUptimeRequest(end_time="2024-01-01T23:59:59")

    @pytest.mark.unit
    def test_missing_end_time_raises_validation_error(self):
        """Test that missing end_time raises ValidationError."""
        # Act & Assert
        with pytest.raises(ValidationError):
            QueryUptimeRequest(start_time="2024-01-01T00:00:00")


class TestLoginRequest:
    """Test suite for LoginRequest schema."""

    @pytest.mark.unit
    def test_valid_request_creates_instance(self):
        """Test that valid request data creates an instance."""
        # Arrange & Act
        request = LoginRequest(username="admin", password="admin123")

        # Assert
        assert request.username == "admin"
        assert request.password == "admin123"

    @pytest.mark.unit
    def test_missing_username_raises_validation_error(self):
        """Test that missing username raises ValidationError."""
        # Act & Assert
        with pytest.raises(ValidationError):
            LoginRequest(password="admin123")

    @pytest.mark.unit
    def test_missing_password_raises_validation_error(self):
        """Test that missing password raises ValidationError."""
        # Act & Assert
        with pytest.raises(ValidationError):
            LoginRequest(username="admin")

