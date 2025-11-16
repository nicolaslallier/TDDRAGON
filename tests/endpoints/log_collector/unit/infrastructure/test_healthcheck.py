"""
Unit tests for healthcheck service.

Tests health check functionality for Nginx, log-collector, and PostgreSQL.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from requests.exceptions import RequestException

from src.endpoints.log_collector.infrastructure.healthcheck import HealthcheckService


class TestHealthcheckService:
    """Test suite for HealthcheckService."""

    @pytest.mark.unit
    def test_check_nginx_health_returns_up_when_status_200(self):
        """Test that check_nginx_health returns UP when HTTP status is 200."""
        # Arrange
        service = HealthcheckService(nginx_url="http://test-nginx/health")
        mock_response = Mock()
        mock_response.status_code = 200

        # Act
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.requests.get") as mock_get:
            mock_get.return_value = mock_response
            status, details = service.check_nginx_health()

        # Assert
        assert status == "UP"
        assert details is None
        mock_get.assert_called_once_with(
            "http://test-nginx/health",
            timeout=5,
            allow_redirects=True,
        )

    @pytest.mark.unit
    def test_check_nginx_health_returns_down_when_status_not_200(self):
        """Test that check_nginx_health returns DOWN when HTTP status is not 200."""
        # Arrange
        service = HealthcheckService(nginx_url="http://test-nginx/health")
        mock_response = Mock()
        mock_response.status_code = 500

        # Act
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.requests.get") as mock_get:
            mock_get.return_value = mock_response
            status, details = service.check_nginx_health()

        # Assert
        assert status == "DOWN"
        assert details == "HTTP 500"

    @pytest.mark.unit
    def test_check_nginx_health_returns_down_on_request_exception(self):
        """Test that check_nginx_health returns DOWN on RequestException."""
        # Arrange
        service = HealthcheckService(nginx_url="http://test-nginx/health")

        # Act
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.requests.get") as mock_get:
            mock_get.side_effect = RequestException("Connection failed")
            status, details = service.check_nginx_health()

        # Assert
        assert status == "DOWN"
        assert details == "Connection failed"

    @pytest.mark.unit
    def test_check_nginx_health_returns_down_on_unexpected_exception(self):
        """Test that check_nginx_health returns DOWN on unexpected exception."""
        # Arrange
        service = HealthcheckService(nginx_url="http://test-nginx/health")

        # Act
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.requests.get") as mock_get:
            mock_get.side_effect = ValueError("Unexpected error")
            status, details = service.check_nginx_health()

        # Assert
        assert status == "DOWN"
        assert "Unexpected error" in details

    @pytest.mark.unit
    def test_check_log_collector_health_returns_up_when_status_200(self):
        """Test that check_log_collector_health returns UP when HTTP status is 200."""
        # Arrange
        service = HealthcheckService(log_collector_url="http://test-collector/health")
        mock_response = Mock()
        mock_response.status_code = 200

        # Act
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.requests.get") as mock_get:
            mock_get.return_value = mock_response
            status, details = service.check_log_collector_health()

        # Assert
        assert status == "UP"
        assert details is None
        mock_get.assert_called_once_with(
            "http://test-collector/health",
            timeout=5,
            allow_redirects=True,
        )

    @pytest.mark.unit
    def test_check_log_collector_health_returns_down_when_status_not_200(self):
        """Test that check_log_collector_health returns DOWN when HTTP status is not 200."""
        # Arrange
        service = HealthcheckService(log_collector_url="http://test-collector/health")
        mock_response = Mock()
        mock_response.status_code = 503

        # Act
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.requests.get") as mock_get:
            mock_get.return_value = mock_response
            status, details = service.check_log_collector_health()

        # Assert
        assert status == "DOWN"
        assert details == "HTTP 503"

    @pytest.mark.unit
    def test_check_log_collector_health_returns_down_on_request_exception(self):
        """Test that check_log_collector_health returns DOWN on RequestException."""
        # Arrange
        service = HealthcheckService(log_collector_url="http://test-collector/health")

        # Act
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.requests.get") as mock_get:
            mock_get.side_effect = RequestException("Timeout")
            status, details = service.check_log_collector_health()

        # Assert
        assert status == "DOWN"
        assert details == "Timeout"

    @pytest.mark.unit
    def test_check_log_collector_health_returns_down_on_unexpected_exception(self):
        """Test that check_log_collector_health returns DOWN on unexpected exception."""
        # Arrange
        service = HealthcheckService(log_collector_url="http://test-collector/health")

        # Act
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.requests.get") as mock_get:
            mock_get.side_effect = RuntimeError("Unexpected error")
            status, details = service.check_log_collector_health()

        # Assert
        assert status == "DOWN"
        assert "Unexpected error" in details

    @pytest.mark.unit
    def test_check_postgresql_health_returns_up_when_connection_succeeds(self):
        """Test that check_postgresql_health returns UP when database connection succeeds."""
        # Arrange
        service = HealthcheckService()
        mock_engine = Mock()
        mock_connection = Mock()
        mock_result = Mock()
        mock_result.fetchone.return_value = (1,)
        mock_connection.execute.return_value = mock_result
        
        # Mock context manager properly using MagicMock
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_connection
        mock_context.__exit__.return_value = None
        mock_engine.connect.return_value = mock_context

        # Act
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.get_engine") as mock_get_engine:
            mock_get_engine.return_value = mock_engine
            status, details = service.check_postgresql_health()

        # Assert
        assert status == "UP"
        assert details is None
        mock_connection.execute.assert_called_once()

    @pytest.mark.unit
    def test_check_postgresql_health_returns_down_on_exception(self):
        """Test that check_postgresql_health returns DOWN on database exception."""
        # Arrange
        service = HealthcheckService()

        # Act
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.get_engine") as mock_get_engine:
            mock_get_engine.side_effect = Exception("Connection failed")
            status, details = service.check_postgresql_health()

        # Assert
        assert status == "DOWN"
        assert details == "Connection failed"

    @pytest.mark.unit
    def test_init_uses_default_urls_when_not_provided(self):
        """Test that __init__ uses default URLs when not provided."""
        # Arrange & Act
        with patch.dict("os.environ", {}, clear=True):
            service = HealthcheckService()

        # Assert
        assert service._nginx_url == "http://nginx/health"
        assert service._log_collector_url == "http://log-collector:8001/health"
        assert service._timeout == 5

    @pytest.mark.unit
    def test_init_uses_env_vars_when_not_provided(self):
        """Test that __init__ uses environment variables when not provided."""
        # Arrange & Act
        with patch.dict(
            "os.environ",
            {
                "NGINX_HEALTHCHECK_URL": "http://custom-nginx/health",
                "LOG_COLLECTOR_HEALTHCHECK_URL": "http://custom-collector/health",
            },
            clear=False,
        ):
            service = HealthcheckService()

        # Assert
        assert service._nginx_url == "http://custom-nginx/health"
        assert service._log_collector_url == "http://custom-collector/health"

    @pytest.mark.unit
    def test_init_uses_provided_urls_over_env_vars(self):
        """Test that __init__ uses provided URLs over environment variables."""
        # Arrange & Act
        with patch.dict(
            "os.environ",
            {
                "NGINX_HEALTHCHECK_URL": "http://env-nginx/health",
                "LOG_COLLECTOR_HEALTHCHECK_URL": "http://env-collector/health",
            },
            clear=False,
        ):
            service = HealthcheckService(
                nginx_url="http://provided-nginx/health",
                log_collector_url="http://provided-collector/health",
            )

        # Assert
        assert service._nginx_url == "http://provided-nginx/health"
        assert service._log_collector_url == "http://provided-collector/health"

