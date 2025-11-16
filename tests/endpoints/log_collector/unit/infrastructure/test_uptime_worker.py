"""
Unit tests for uptime worker.

Tests background worker functionality for recording uptime measurements.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.endpoints.log_collector.infrastructure.uptime_worker import (
    UptimeWorker,
    get_uptime_worker,
)


class TestUptimeWorker:
    """Test suite for UptimeWorker."""

    @pytest.mark.unit
    def test_init_sets_attributes_correctly(self):
        """Test that __init__ sets all attributes correctly."""
        # Arrange & Act
        worker = UptimeWorker(
            interval_seconds=30,
            nginx_url="http://test-nginx/health",
            log_collector_url="http://test-collector/health",
        )

        # Assert
        assert worker._interval == 30
        assert worker._running is False
        assert worker._task is None
        assert worker._healthcheck_service is not None

    @pytest.mark.unit
    def test_start_sets_running_flag(self):
        """Test that start() sets _running flag to True."""
        # Arrange
        worker = UptimeWorker(interval_seconds=60)

        # Act
        asyncio.run(worker.start())

        # Assert
        assert worker._running is True
        assert worker._task is not None

        # Cleanup
        asyncio.run(worker.stop())

    @pytest.mark.unit
    def test_start_warns_if_already_running(self):
        """Test that start() warns if worker is already running."""
        # Arrange
        worker = UptimeWorker(interval_seconds=60)
        asyncio.run(worker.start())

        # Act
        with patch("src.endpoints.log_collector.infrastructure.uptime_worker.logger") as mock_logger:
            asyncio.run(worker.start())

        # Assert
        mock_logger.warning.assert_called_once_with("UptimeWorker is already running")

        # Cleanup
        asyncio.run(worker.stop())

    @pytest.mark.unit
    def test_stop_sets_running_flag_to_false(self):
        """Test that stop() sets _running flag to False."""
        # Arrange
        worker = UptimeWorker(interval_seconds=60)
        asyncio.run(worker.start())

        # Act
        asyncio.run(worker.stop())

        # Assert
        assert worker._running is False

    @pytest.mark.unit
    def test_stop_does_nothing_if_not_running(self):
        """Test that stop() does nothing if worker is not running."""
        # Arrange
        worker = UptimeWorker(interval_seconds=60)

        # Act
        asyncio.run(worker.stop())

        # Assert
        assert worker._running is False

    @pytest.mark.unit
    def test_check_and_record_records_uptime_for_all_services(self):
        """Test that _check_and_record() records uptime for all services."""
        # Arrange
        worker = UptimeWorker(interval_seconds=60)
        mock_session = Mock()
        mock_repository = Mock()
        mock_use_case = Mock()
        mock_record = Mock()
        mock_record.status = "UP"
        mock_record.timestamp_utc = None
        mock_use_case.record_uptime.return_value = mock_record

        # Mock healthcheck service
        worker._healthcheck_service.check_nginx_health = Mock(return_value=("UP", None))
        worker._healthcheck_service.check_log_collector_health = Mock(return_value=("UP", None))
        worker._healthcheck_service.check_postgresql_health = Mock(return_value=("UP", None))

        # Mock get_session
        mock_session_gen = iter([mock_session])
        with patch("src.endpoints.log_collector.infrastructure.uptime_worker.get_session") as mock_get_session:
            mock_get_session.return_value = mock_session_gen

            # Mock imports - patch at the source module since imports are done inside the function
            with patch(
                "src.endpoints.log_collector.infrastructure.repositories.SQLAlchemyUptimeRepository"
            ) as mock_repo_class:
                mock_repo_class.return_value = mock_repository

                with patch(
                    "src.endpoints.log_collector.application.calculate_uptime.CalculateUptime"
                ) as mock_use_case_class:
                    mock_use_case_class.return_value = mock_use_case

                    # Act
                    asyncio.run(worker._check_and_record())

        # Assert
        assert mock_use_case.record_uptime.call_count == 3
        mock_session.flush.assert_called_once()

    @pytest.mark.unit
    def test_check_and_record_rolls_back_on_error(self):
        """Test that _check_and_record() handles errors and rolls back session."""
        # Arrange
        worker = UptimeWorker(interval_seconds=60)
        mock_session = Mock()
        mock_session_gen = iter([mock_session])

        # Mock healthcheck service
        worker._healthcheck_service.check_nginx_health = Mock(return_value=("UP", None))
        worker._healthcheck_service.check_log_collector_health = Mock(return_value=("UP", None))
        worker._healthcheck_service.check_postgresql_health = Mock(return_value=("UP", None))

        # Mock get_session
        with patch("src.endpoints.log_collector.infrastructure.uptime_worker.get_session") as mock_get_session:
            mock_get_session.return_value = mock_session_gen

            # Mock imports to raise exception when instantiating repository
            with patch(
                "src.endpoints.log_collector.infrastructure.repositories.SQLAlchemyUptimeRepository"
            ) as mock_repo_class:
                # Make the class instantiation raise an exception
                def raise_on_init(*args, **kwargs):
                    raise Exception("Database error")
                mock_repo_class.side_effect = raise_on_init

                # Act
                # The exception will be raised when SQLAlchemyUptimeRepository is instantiated
                # It will be caught by the inner try-except (line 187), which calls rollback (line 189)
                # Then it's re-raised (line 190) and caught by the outer try-except (line 193)
                # The outer try-except logs the error but doesn't re-raise it
                asyncio.run(worker._check_and_record())
                
                # Assert
                # Verify session was accessed (get_session was called)
                assert mock_get_session.called
                # Verify rollback was called in the inner except block
                mock_session.rollback.assert_called_once()
                # Verify session.close() was called in finally block (line 192)
                mock_session.close.assert_called_once()

    @pytest.mark.unit
    def test_run_loop_executes_periodically(self):
        """Test that _run_loop() executes checks periodically."""
        # Arrange
        worker = UptimeWorker(interval_seconds=0.1)  # Very short interval for test
        worker._running = True
        call_count = 0

        async def mock_check():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                worker._running = False  # Stop after 2 calls

        worker._check_and_record = mock_check

        # Act
        asyncio.run(worker._run_loop())

        # Assert
        assert call_count == 2

    @pytest.mark.unit
    def test_run_loop_handles_exceptions(self):
        """Test that _run_loop() handles exceptions gracefully."""
        # Arrange
        worker = UptimeWorker(interval_seconds=0.1)
        worker._running = True
        call_count = 0

        async def mock_check():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Test error")
            worker._running = False  # Stop after handling error

        worker._check_and_record = mock_check

        # Act
        with patch("src.endpoints.log_collector.infrastructure.uptime_worker.logger") as mock_logger:
            asyncio.run(worker._run_loop())

        # Assert
        assert call_count == 2  # Should continue after error
        mock_logger.error.assert_called_once()

    @pytest.mark.unit
    def test_run_loop_handles_cancelled_error(self):
        """Test that _run_loop() handles CancelledError during sleep."""
        # Arrange
        worker = UptimeWorker(interval_seconds=60)
        worker._running = True
        call_count = 0

        async def mock_check():
            nonlocal call_count
            call_count += 1

        worker._check_and_record = mock_check

        # Create a task that will cancel the sleep
        async def cancel_sleep():
            await asyncio.sleep(0.01)  # Small delay
            # Get the sleep task and cancel it
            for task in asyncio.all_tasks():
                if task != asyncio.current_task():
                    task.cancel()

        # Act
        async def run_with_cancellation():
            # Start the worker loop
            loop_task = asyncio.create_task(worker._run_loop())
            # Start cancellation task
            cancel_task = asyncio.create_task(cancel_sleep())
            # Wait for cancellation
            try:
                await loop_task
            except asyncio.CancelledError:
                pass

        try:
            asyncio.run(run_with_cancellation())
        except asyncio.CancelledError:
            pass  # Expected

        # Assert
        assert call_count >= 1  # Should have called check at least once before cancellation

    @pytest.mark.unit
    def test_get_uptime_worker_returns_singleton(self):
        """Test that get_uptime_worker() returns the same instance."""
        # Arrange & Act
        with patch.dict("os.environ", {"UPTIME_CHECK_INTERVAL": "30"}, clear=False):
            worker1 = get_uptime_worker()
            worker2 = get_uptime_worker()

        # Assert
        assert worker1 is worker2

    @pytest.mark.unit
    def test_get_uptime_worker_uses_env_vars(self):
        """Test that get_uptime_worker() uses environment variables."""
        # Arrange - Reset the global worker singleton
        from src.endpoints.log_collector.infrastructure.uptime_worker import _worker
        import src.endpoints.log_collector.infrastructure.uptime_worker as uptime_worker_module
        original_worker = uptime_worker_module._worker
        uptime_worker_module._worker = None
        
        try:
            # Act
            with patch.dict(
                "os.environ",
                {
                    "UPTIME_CHECK_INTERVAL": "120",
                    "NGINX_HEALTHCHECK_URL": "http://env-nginx/health",
                    "LOG_COLLECTOR_HEALTHCHECK_URL": "http://env-collector/health",
                },
                clear=False,
            ):
                worker = get_uptime_worker()

            # Assert
            assert worker._interval == 120
        finally:
            # Restore original worker
            uptime_worker_module._worker = original_worker

