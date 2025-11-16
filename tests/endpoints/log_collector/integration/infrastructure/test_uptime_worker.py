"""
Integration tests for UptimeWorker.

Tests the UptimeWorker with real database connections and health check services.
"""

import asyncio
import os
from unittest.mock import Mock, patch

import pytest

from src.endpoints.log_collector.infrastructure.uptime_worker import UptimeWorker
from src.endpoints.log_collector.infrastructure.models import NginxUptimeModel
from src.shared.infrastructure.database import init_database, get_session


@pytest.fixture
def test_database_url() -> str:
    """Provide test database URL."""
    return "sqlite:///:memory:"


@pytest.fixture
def test_session(test_database_url: str):
    """Provide test database session."""
    original_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = test_database_url
    try:
        init_database(test_database_url)
        
        # Create tables using the shared database engine
        from src.endpoints.log_collector.infrastructure.models import (
            NginxAccessLogModel,
            NginxUptimeModel,
        )
        from src.shared.models.base import Base as SharedBase
        from src.shared.infrastructure.database import get_engine
        
        engine = get_engine()
        SharedBase.metadata.create_all(engine)
        
        # Use get_session() to ensure we use the same connection pool
        from src.shared.infrastructure.database import get_session
        session_gen = get_session()
        session = next(session_gen)
        
        yield session
        
        # Cleanup
        SharedBase.metadata.drop_all(engine)
        session.close()
    finally:
        if original_db_url is not None:
            os.environ["DATABASE_URL"] = original_db_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]


@pytest.mark.integration
def test_uptime_worker_start_when_already_running_logs_warning(test_session):
    """Test that starting UptimeWorker when already running logs a warning."""
    # Test lines 58-59: Already running check
    async def _test():
        worker = UptimeWorker(interval_seconds=60)
        
        # Start worker
        await worker.start()
        
        # Try to start again (should log warning and return early)
        with patch("src.endpoints.log_collector.infrastructure.uptime_worker.logger") as mock_logger:
            await worker.start()
            mock_logger.warning.assert_called_once_with("UptimeWorker is already running")
        
        # Cleanup
        await worker.stop()
    
    asyncio.run(_test())


@pytest.mark.integration
def test_uptime_worker_stop_when_not_running_returns_early(test_session):
    """Test that stopping UptimeWorker when not running returns early."""
    # Test line 83: Early return when not running
    async def _test():
        worker = UptimeWorker(interval_seconds=60)
        
        # Stop without starting (should return early)
        await worker.stop()  # Should not raise exception
        
        # Verify _running is False
        assert worker._running is False
    
    asyncio.run(_test())


@pytest.mark.integration
def test_uptime_worker_run_loop_handles_exceptions(test_session):
    """Test that _run_loop handles exceptions gracefully."""
    # Test lines 101-111: Exception handling in run loop
    async def _test():
        worker = UptimeWorker(interval_seconds=1)  # Short interval for testing
        
        # Mock _check_and_record to raise an exception
        call_count = 0
        async def mock_check_and_record():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Test exception")
            # Second call succeeds
        
        worker._check_and_record = mock_check_and_record
        worker._running = True
        
        # Start the loop
        loop_task = asyncio.create_task(worker._run_loop())
        
        # Wait a bit for the loop to run
        await asyncio.sleep(0.1)
        
        # Stop the worker
        worker._running = False
        loop_task.cancel()
        
        try:
            await loop_task
        except asyncio.CancelledError:
            pass
        
        # Verify exception was handled (loop continued)
        assert call_count >= 1
    
    asyncio.run(_test())


@pytest.mark.integration
def test_uptime_worker_run_loop_handles_cancelled_error(test_session):
    """Test that _run_loop handles CancelledError during sleep."""
    # Test lines 108-111: CancelledError handling
    async def _test():
        worker = UptimeWorker(interval_seconds=60)
        
        call_count = 0
        async def mock_check_and_record():
            nonlocal call_count
            call_count += 1
        
        worker._check_and_record = mock_check_and_record
        worker._running = True
        
        # Start the loop
        loop_task = asyncio.create_task(worker._run_loop())
        
        # Wait a bit
        await asyncio.sleep(0.01)
        
        # Cancel the task (simulates CancelledError during sleep)
        loop_task.cancel()
        
        try:
            await loop_task
        except asyncio.CancelledError:
            pass
        
        # Verify CancelledError was handled (break from loop)
        assert call_count >= 1
    
    asyncio.run(_test())


@pytest.mark.integration
def test_uptime_worker_check_and_record_performs_health_checks(test_session):
    """Test that _check_and_record performs health checks for all services."""
    # Test lines 128-192: Health checks and database recording
    async def _test():
        worker = UptimeWorker(interval_seconds=60)
        
        # Mock healthcheck service to return known values
        mock_healthcheck = Mock()
        mock_healthcheck.check_nginx_health.return_value = ("UP", None)
        mock_healthcheck.check_log_collector_health.return_value = ("UP", None)
        mock_healthcheck.check_postgresql_health.return_value = ("UP", None)
        worker._healthcheck_service = mock_healthcheck
        
        # Execute check and record
        await worker._check_and_record()
        
        # Verify all health checks were called
        mock_healthcheck.check_nginx_health.assert_called_once()
        mock_healthcheck.check_log_collector_health.assert_called_once()
        mock_healthcheck.check_postgresql_health.assert_called_once()
        
        # Verify records were created in database
        # The worker uses get_session() which creates its own session and commits via repository.create().
        # Since we're using StaticPool with size=1 for SQLite, all sessions share the same connection.
        # Wait a bit to ensure async operations complete and commits are visible
        await asyncio.sleep(0.2)
        
        # Query using a fresh session from get_session() to see committed data
        # This ensures we're using the same connection pool as the worker
        # The repository.create() method commits each record individually, so they should be visible
        session_gen = get_session()
        session = next(session_gen)
        try:
            # Execute WAL checkpoint to ensure data is visible (SQLite requirement)
            from sqlalchemy import text
            connection = session.connection()
            if connection.dialect.name == "sqlite":
                connection.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
            
            records = session.query(NginxUptimeModel).order_by(NginxUptimeModel.timestamp_utc.desc()).limit(3).all()
            
            # Should have at least 3 records (one for each service)
            assert len(records) >= 3, f"Expected at least 3 records, got {len(records)}"
            
            # Verify sources
            sources = {r.source for r in records}
            assert "healthcheck_nginx" in sources
            assert "healthcheck_log_collector" in sources
            assert "healthcheck_postgresql" in sources
        finally:
            session.close()
    
    asyncio.run(_test())


@pytest.mark.integration
def test_uptime_worker_check_and_record_handles_exceptions(test_session):
    """Test that _check_and_record handles exceptions gracefully."""
    # Test line 194: Exception handler in _check_and_record
    async def _test():
        worker = UptimeWorker(interval_seconds=60)
        
        # Mock healthcheck service to raise exception
        mock_healthcheck = Mock()
        mock_healthcheck.check_nginx_health.side_effect = Exception("Health check failed")
        worker._healthcheck_service = mock_healthcheck
        
        # Execute check and record (should handle exception)
        with patch("src.endpoints.log_collector.infrastructure.uptime_worker.logger") as mock_logger:
            await worker._check_and_record()
            
            # Verify error was logged
            mock_logger.error.assert_called()
            error_call = mock_logger.error.call_args_list[-1]
            assert "Error checking and recording uptime" in error_call[0][0]
    
    asyncio.run(_test())


@pytest.mark.integration
def test_uptime_worker_check_and_record_rolls_back_on_database_error(test_session):
    """Test that _check_and_record rolls back on database error."""
    # Test lines 187-190: Database error handling
    async def _test():
        worker = UptimeWorker(interval_seconds=60)
        
        # Mock healthcheck service
        mock_healthcheck = Mock()
        mock_healthcheck.check_nginx_health.return_value = ("UP", None)
        mock_healthcheck.check_log_collector_health.return_value = ("UP", None)
        mock_healthcheck.check_postgresql_health.return_value = ("UP", None)
        worker._healthcheck_service = mock_healthcheck
        
        # Mock SQLAlchemyUptimeRepository.create to raise exception
        # Patch at the source module where it's imported inside _check_and_record
        with patch("src.endpoints.log_collector.infrastructure.repositories.SQLAlchemyUptimeRepository") as mock_repo_class:
            mock_repo_instance = Mock()
            mock_repo_instance.create.side_effect = Exception("Database error")
            mock_repo_class.return_value = mock_repo_instance
            
            # Execute check and record
            with patch("src.endpoints.log_collector.infrastructure.uptime_worker.logger") as mock_logger:
                await worker._check_and_record()
                
                # Verify error was logged (lines 187-190)
                mock_logger.error.assert_called()
                # Find the error call about recording uptime
                error_calls = [call for call in mock_logger.error.call_args_list if "Error recording uptime" in call[0][0]]
                assert len(error_calls) > 0, "Expected error log about recording uptime"
    
    asyncio.run(_test())


@pytest.mark.integration
def test_get_uptime_worker_creates_singleton(test_session):
    """Test that get_uptime_worker creates a singleton instance."""
    # Test lines 209-220: get_uptime_worker function
    import os
    from src.endpoints.log_collector.infrastructure.uptime_worker import get_uptime_worker
    
    # Reset the global worker
    import src.endpoints.log_collector.infrastructure.uptime_worker as uptime_worker_module
    original_worker = uptime_worker_module._worker
    uptime_worker_module._worker = None
    
    try:
        # Set environment variables to test the function
        original_interval = os.environ.get("UPTIME_CHECK_INTERVAL")
        original_nginx_url = os.environ.get("NGINX_HEALTHCHECK_URL")
        original_log_collector_url = os.environ.get("LOG_COLLECTOR_HEALTHCHECK_URL")
        
        os.environ["UPTIME_CHECK_INTERVAL"] = "120"
        os.environ["NGINX_HEALTHCHECK_URL"] = "http://test-nginx/health"
        os.environ["LOG_COLLECTOR_HEALTHCHECK_URL"] = "http://test-collector:9000/health"
        
        # Get worker instance (should create new one)
        worker1 = get_uptime_worker()
        
        # Get worker instance again (should return same instance)
        worker2 = get_uptime_worker()
        
        # Should be the same instance (singleton)
        assert worker1 is worker2
        assert isinstance(worker1, UptimeWorker)
        assert worker1._interval == 120
        assert worker1._healthcheck_service._nginx_url == "http://test-nginx/health"
        assert worker1._healthcheck_service._log_collector_url == "http://test-collector:9000/health"
        
        # Restore environment variables
        if original_interval is not None:
            os.environ["UPTIME_CHECK_INTERVAL"] = original_interval
        elif "UPTIME_CHECK_INTERVAL" in os.environ:
            del os.environ["UPTIME_CHECK_INTERVAL"]
        
        if original_nginx_url is not None:
            os.environ["NGINX_HEALTHCHECK_URL"] = original_nginx_url
        elif "NGINX_HEALTHCHECK_URL" in os.environ:
            del os.environ["NGINX_HEALTHCHECK_URL"]
        
        if original_log_collector_url is not None:
            os.environ["LOG_COLLECTOR_HEALTHCHECK_URL"] = original_log_collector_url
        elif "LOG_COLLECTOR_HEALTHCHECK_URL" in os.environ:
            del os.environ["LOG_COLLECTOR_HEALTHCHECK_URL"]
    finally:
        # Restore original worker
        uptime_worker_module._worker = original_worker
