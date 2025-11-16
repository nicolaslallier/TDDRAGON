"""
Integration tests for HealthcheckService.

Tests health checks with real HTTP requests and database connections.
"""

import os
from unittest.mock import Mock, patch

import pytest

from src.endpoints.log_collector.infrastructure.healthcheck import HealthcheckService
from src.shared.infrastructure.database import init_database, get_engine


@pytest.fixture
def test_database_url() -> str:
    """Provide test database URL."""
    return "sqlite:///:memory:"


@pytest.fixture
def test_session(test_database_url: str):
    """Initialize test database."""
    original_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = test_database_url
    try:
        init_database(test_database_url)
        yield
    finally:
        if original_db_url is not None:
            os.environ["DATABASE_URL"] = original_db_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]


@pytest.mark.integration
def test_check_nginx_health_returns_up_on_200_status(test_session):
    """Test that check_nginx_health returns UP on 200 status code."""
    # Test lines 69-71: Success case with debug logging
    service = HealthcheckService(nginx_url="http://httpbin.org/status/200")
    
    with patch("src.endpoints.log_collector.infrastructure.healthcheck.logger") as mock_logger:
        status, details = service.check_nginx_health()
        
        assert status == "UP"
        assert details is None
        # Verify debug log was called (lines 70-71)
        mock_logger.debug.assert_called()
        debug_call = mock_logger.debug.call_args_list[0]
        assert "Nginx healthcheck successful" in debug_call[0][0]


@pytest.mark.integration
def test_check_nginx_health_returns_down_on_non_200_status(test_session):
    """Test that check_nginx_health returns DOWN on non-200 status code."""
    # Test lines 69-76: Non-200 status code handling
    service = HealthcheckService(nginx_url="http://httpbin.org/status/500")
    
    status, details = service.check_nginx_health()
    
    assert status == "DOWN"
    assert details == "HTTP 500"


@pytest.mark.integration
def test_check_nginx_health_handles_unexpected_exception(test_session):
    """Test that check_nginx_health handles unexpected exceptions."""
    # Test lines 80-82: Unexpected exception handling
    service = HealthcheckService(nginx_url="http://invalid-url-that-will-fail.com/health")
    
    # Mock requests.get to raise unexpected exception
    with patch("src.endpoints.log_collector.infrastructure.healthcheck.requests.get") as mock_get:
        mock_get.side_effect = ValueError("Unexpected error")
        
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.logger") as mock_logger:
            status, details = service.check_nginx_health()
            
            assert status == "DOWN"
            assert "Unexpected error" in details
            mock_logger.error.assert_called_once()


@pytest.mark.integration
def test_check_log_collector_health_returns_up_on_200_status(test_session):
    """Test that check_log_collector_health returns UP on 200 status code."""
    # Test lines 101-103: Success case with debug logging
    service = HealthcheckService(log_collector_url="http://httpbin.org/status/200")
    
    with patch("src.endpoints.log_collector.infrastructure.healthcheck.logger") as mock_logger:
        status, details = service.check_log_collector_health()
        
        assert status == "UP"
        assert details is None
        # Verify debug log was called (lines 102-103)
        mock_logger.debug.assert_called()
        debug_call = mock_logger.debug.call_args_list[0]
        assert "Log-collector healthcheck successful" in debug_call[0][0]


@pytest.mark.integration
def test_check_log_collector_health_returns_down_on_non_200_status(test_session):
    """Test that check_log_collector_health returns DOWN on non-200 status code."""
    # Test lines 101-108: Non-200 status code handling
    service = HealthcheckService(log_collector_url="http://httpbin.org/status/404")
    
    status, details = service.check_log_collector_health()
    
    assert status == "DOWN"
    assert details == "HTTP 404"


@pytest.mark.integration
def test_check_log_collector_health_handles_request_exception(test_session):
    """Test that check_log_collector_health handles RequestException."""
    # Test lines 109-111: RequestException handling
    service = HealthcheckService(log_collector_url="http://invalid-url-that-will-fail.com/health")
    
    status, details = service.check_log_collector_health()
    
    assert status == "DOWN"
    assert details is not None
    assert isinstance(details, str)


@pytest.mark.integration
def test_check_log_collector_health_handles_unexpected_exception(test_session):
    """Test that check_log_collector_health handles unexpected exceptions."""
    # Test lines 112-114: Unexpected exception handling
    service = HealthcheckService(log_collector_url="http://httpbin.org/status/200")
    
    # Mock requests.get to raise unexpected exception
    with patch("src.endpoints.log_collector.infrastructure.healthcheck.requests.get") as mock_get:
        mock_get.side_effect = ValueError("Unexpected error")
        
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.logger") as mock_logger:
            status, details = service.check_log_collector_health()
            
            assert status == "DOWN"
            assert "Unexpected error" in details
            mock_logger.error.assert_called_once()


@pytest.mark.integration
def test_check_postgresql_health_returns_up_when_connected(test_session):
    """Test that check_postgresql_health returns UP when database is connected."""
    # Test lines 127-134: PostgreSQL health check success
    service = HealthcheckService()
    
    status, details = service.check_postgresql_health()
    
    assert status == "UP"
    assert details is None


@pytest.mark.integration
def test_check_postgresql_health_returns_down_on_connection_error(test_session):
    """Test that check_postgresql_health returns DOWN on connection error."""
    # Test lines 135-137: PostgreSQL health check failure
    service = HealthcheckService()
    
    # Mock get_engine to raise exception
    with patch("src.endpoints.log_collector.infrastructure.healthcheck.get_engine") as mock_get_engine:
        mock_get_engine.side_effect = Exception("Connection failed")
        
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.logger") as mock_logger:
            status, details = service.check_postgresql_health()
            
            assert status == "DOWN"
            assert "Connection failed" in details
            mock_logger.warning.assert_called_once()
