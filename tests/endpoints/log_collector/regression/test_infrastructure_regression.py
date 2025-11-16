"""
Regression tests for log collector infrastructure layer.

Ensures that infrastructure components continue to work correctly after changes.
"""

import asyncio
import os
import tempfile
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.endpoints.log_collector.domain.models import LogEntry, UptimeRecord
from src.endpoints.log_collector.infrastructure.healthcheck import HealthcheckService
from src.endpoints.log_collector.infrastructure.log_reader import LogReader
from src.endpoints.log_collector.infrastructure.repositories import (
    SQLAlchemyLogRepository,
    SQLAlchemyUptimeRepository,
)
from src.endpoints.log_collector.infrastructure.uptime_worker import (
    UptimeWorker,
    get_uptime_worker,
)
from src.shared.infrastructure.database import init_database


class TestLogReaderRegression:
    """Regression tests for LogReader."""

    @pytest.mark.regression
    def test_log_reader_initializes_file_positions_dict(self):
        """Test that LogReader.__init__ initializes file_positions dict."""
        # Arrange & Act
        reader = LogReader()

        # Assert
        assert hasattr(reader, "_file_positions")
        assert reader._file_positions == {}

    @pytest.mark.regression
    def test_read_from_file_reads_all_lines(self):
        """Test that read_from_file reads all lines from a file."""
        # Arrange
        reader = LogReader()
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            for line in log_lines:
                f.write(line + "\n")
            file_path = f.name

        try:
            # Act
            result = reader.read_from_file(file_path)

            # Assert
            assert len(result) == 2
            assert result[0] == log_lines[0]
            assert result[1] == log_lines[1]
        finally:
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.regression
    def test_read_from_file_with_nonexistent_file_returns_empty_list(self):
        """Test that read_from_file returns empty list for nonexistent file."""
        # Arrange
        reader = LogReader()
        nonexistent_path = "/tmp/nonexistent_file_12345.log"

        # Act
        result = reader.read_from_file(nonexistent_path)

        # Assert
        assert result == []

    @pytest.mark.regression
    def test_read_from_file_handles_io_error(self):
        """Test that read_from_file handles IOError gracefully."""
        # Arrange
        reader = LogReader()
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.write("test line\n")
            temp_path = f.name

        try:
            # Mock open to raise IOError
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                # Act
                result = reader.read_from_file(temp_path)

                # Assert
                assert result == []
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.regression
    def test_read_new_lines_tracks_position(self):
        """Test that read_new_lines tracks file position correctly."""
        # Arrange
        reader = LogReader()
        initial_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
        ]
        new_lines = [
            '192.168.1.3 - - [16/Nov/2024:10:00:02 +0000] "GET /demo-items HTTP/1.1" 200 789 "-" "Mozilla/5.0"',
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            for line in initial_lines:
                f.write(line + "\n")
            file_path = f.name

        try:
            # Act - Read initial lines
            result1 = reader.read_new_lines(file_path)
            assert len(result1) == 2

            # Append new lines
            with open(file_path, "a", encoding="utf-8") as f:
                for line in new_lines:
                    f.write(line + "\n")

            # Read new lines only
            result2 = reader.read_new_lines(file_path)

            # Assert
            assert len(result2) == 1
            assert result2[0] == new_lines[0]
        finally:
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.regression
    def test_read_new_lines_with_nonexistent_file_returns_empty_list(self):
        """Test that read_new_lines returns empty list for nonexistent file."""
        # Arrange
        reader = LogReader()
        nonexistent_path = "/tmp/nonexistent_file_12345.log"

        # Act
        result = reader.read_new_lines(nonexistent_path)

        # Assert
        assert result == []

    @pytest.mark.regression
    def test_read_new_lines_handles_io_error(self):
        """Test that read_new_lines handles IOError gracefully."""
        # Arrange
        reader = LogReader()
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.write("test line\n")
            temp_path = f.name

        try:
            # Mock open to raise IOError
            with patch("builtins.open", side_effect=OSError("Permission denied")):
                # Act
                result = reader.read_new_lines(temp_path)

                # Assert
                assert result == []
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @pytest.mark.regression
    def test_read_from_stream_reads_all_lines(self):
        """Test that read_from_stream reads all lines from a stream."""
        # Arrange
        reader = LogReader()
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
        ]
        stream = StringIO("\n".join(log_lines) + "\n")

        # Act
        result = reader.read_from_stream(stream)

        # Assert
        assert len(result) == 2
        assert result[0] == log_lines[0]
        assert result[1] == log_lines[1]

    @pytest.mark.regression
    def test_read_from_stream_with_empty_stream_returns_empty_list(self):
        """Test that read_from_stream returns empty list for empty stream."""
        # Arrange
        reader = LogReader()
        stream = StringIO("")

        # Act
        result = reader.read_from_stream(stream)

        # Assert
        assert result == []

    @pytest.mark.regression
    def test_read_from_stream_handles_io_error(self):
        """Test that read_from_stream handles IOError gracefully."""
        # Arrange
        reader = LogReader()
        stream = Mock()
        stream.readline.side_effect = OSError("Stream error")

        # Act
        result = reader.read_from_stream(stream)

        # Assert
        assert result == []

    @pytest.mark.regression
    def test_reset_position_resets_file_position(self):
        """Test that reset_position resets file position tracking."""
        # Arrange
        reader = LogReader()
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            for line in log_lines:
                f.write(line + "\n")
            file_path = f.name

        try:
            # Act - Read initial lines
            result1 = reader.read_new_lines(file_path)
            assert len(result1) == 1

            # Reset position
            reader.reset_position(file_path)

            # Read again - should read from beginning
            result2 = reader.read_new_lines(file_path)

            # Assert
            assert len(result2) == 1
            assert result2[0] == log_lines[0]
        finally:
            Path(file_path).unlink(missing_ok=True)

    @pytest.mark.regression
    def test_read_from_file_skips_empty_lines(self):
        """Test that read_from_file skips empty lines."""
        # Arrange
        reader = LogReader()
        log_lines = [
            '192.168.1.1 - - [16/Nov/2024:10:00:00 +0000] "GET /health HTTP/1.1" 200 123 "-" "Mozilla/5.0"',
            "",
            "   ",
            '192.168.1.2 - - [16/Nov/2024:10:00:01 +0000] "POST /demo-items HTTP/1.1" 201 456 "-" "curl/7.0"',
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            for line in log_lines:
                f.write(line + "\n")
            file_path = f.name

        try:
            # Act
            result = reader.read_from_file(file_path)

            # Assert - Should only return non-empty lines
            assert len(result) == 2
            assert result[0] == log_lines[0]
            assert result[1] == log_lines[3]
        finally:
            Path(file_path).unlink(missing_ok=True)


class TestSQLAlchemyLogRepositoryRegression:
    """Regression tests for SQLAlchemyLogRepository."""

    @pytest.mark.regression
    def test_sqlalchemy_log_repository_initializes_with_session(self):
        """Test that SQLAlchemyLogRepository.__init__ stores session correctly."""
        # Arrange
        mock_session = Mock()

        # Act
        repository = SQLAlchemyLogRepository(session=mock_session)

        # Assert
        assert repository._session is mock_session

    @pytest.mark.regression
    def test_create_log_entry_converts_to_domain_model(self):
        """Test that create converts database model to domain model."""
        # Arrange
        from src.endpoints.log_collector.infrastructure.models import (
            NginxAccessLogModel,
        )

        mock_session = Mock()
        mock_db_model = Mock(spec=NginxAccessLogModel)
        mock_db_model.id = 1
        mock_db_model.timestamp_utc = datetime.now()
        mock_db_model.client_ip = "192.168.1.1"
        mock_db_model.http_method = "GET"
        mock_db_model.request_uri = "/health"
        mock_db_model.status_code = 200
        mock_db_model.response_time = 0.05
        mock_db_model.user_agent = "Mozilla/5.0"
        mock_db_model.raw_line = "test line"
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.commit.return_value = None
        mock_session.expire_all.return_value = None
        mock_session.connection.return_value.dialect.name = "postgresql"

        repository = SQLAlchemyLogRepository(session=mock_session)
        entry = LogEntry(
            id=0,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
        )

        # Mock the _to_domain_model method to return the entry
        with patch.object(repository, "_to_domain_model", return_value=entry):
            # Act
            result = repository.create(entry)

            # Assert
            assert result is entry
            mock_session.add.assert_called_once()
            mock_session.flush.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.regression
    def test_create_log_entry_handles_sqlite_checkpoint_exception(self):
        """Test that create handles SQLite checkpoint exception gracefully."""
        # Arrange
        from src.endpoints.log_collector.infrastructure.models import (
            NginxAccessLogModel,
        )

        mock_session = Mock()
        mock_db_model = Mock(spec=NginxAccessLogModel)
        mock_db_model.id = 1
        mock_db_model.timestamp_utc = datetime.now()
        mock_db_model.client_ip = "192.168.1.1"
        mock_db_model.http_method = "GET"
        mock_db_model.request_uri = "/health"
        mock_db_model.status_code = 200
        mock_db_model.response_time = 0.05
        mock_db_model.user_agent = "Mozilla/5.0"
        mock_db_model.raw_line = "test line"
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.commit.return_value = None
        mock_session.expire_all.return_value = None
        mock_connection = Mock()
        mock_connection.dialect.name = "sqlite"
        mock_session.connection.return_value = mock_connection
        mock_connection.execute.side_effect = Exception("Checkpoint failed")

        repository = SQLAlchemyLogRepository(session=mock_session)
        entry = LogEntry(
            id=0,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
        )

        # Mock _to_domain_model to return the entry
        with patch.object(repository, "_to_domain_model", return_value=entry):
            # Act - Should not raise exception
            result = repository.create(entry)

            # Assert
            assert result is entry

    @pytest.mark.regression
    def test_to_domain_model_converts_log_entry(self):
        """Test that _to_domain_model converts NginxAccessLogModel to LogEntry."""
        # Arrange
        from src.endpoints.log_collector.infrastructure.models import (
            NginxAccessLogModel,
        )

        mock_session = Mock()
        repository = SQLAlchemyLogRepository(session=mock_session)
        db_model = Mock(spec=NginxAccessLogModel)
        db_model.id = 1
        db_model.timestamp_utc = datetime.now()
        db_model.client_ip = "192.168.1.1"
        db_model.http_method = "GET"
        db_model.request_uri = "/health"
        db_model.status_code = 200
        db_model.response_time = 0.05
        db_model.user_agent = "Mozilla/5.0"
        db_model.raw_line = "test line"

        # Act
        result = repository._to_domain_model(db_model)

        # Assert
        assert isinstance(result, LogEntry)
        assert result.id == 1
        assert result.client_ip == "192.168.1.1"
        assert result.http_method == "GET"
        assert result.status_code == 200

    @pytest.mark.regression
    def test_find_by_time_range_calls_session_query(self):
        """Test that find_by_time_range calls session query correctly."""
        # Arrange
        from src.endpoints.log_collector.infrastructure.models import (
            NginxAccessLogModel,
        )

        mock_session = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_db_model = Mock(spec=NginxAccessLogModel)
        mock_query.all.return_value = [mock_db_model]
        mock_session.query.return_value = mock_query

        repository = SQLAlchemyLogRepository(session=mock_session)
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()

        # Mock _to_domain_model to return a LogEntry
        mock_entry = LogEntry(
            id=1,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
        )
        with patch.object(repository, "_to_domain_model", return_value=mock_entry):
            # Act
            result = repository.find_by_time_range(start_time, end_time)

            # Assert
            assert len(result) == 1
            mock_session.query.assert_called_once()

    @pytest.mark.regression
    def test_find_by_status_code_calls_session_query(self):
        """Test that find_by_status_code calls session query correctly."""
        # Arrange
        from src.endpoints.log_collector.infrastructure.models import (
            NginxAccessLogModel,
        )

        mock_session = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_db_model = Mock(spec=NginxAccessLogModel)
        mock_query.all.return_value = [mock_db_model]
        mock_session.query.return_value = mock_query

        repository = SQLAlchemyLogRepository(session=mock_session)

        # Mock _to_domain_model to return a LogEntry
        mock_entry = LogEntry(
            id=1,
            timestamp_utc=datetime.now(),
            client_ip="192.168.1.1",
            http_method="GET",
            request_uri="/health",
            status_code=200,
            response_time=0.05,
        )
        with patch.object(repository, "_to_domain_model", return_value=mock_entry):
            # Act
            result = repository.find_by_status_code(200)

            # Assert
            assert len(result) == 1
            mock_session.query.assert_called_once()


class TestSQLAlchemyUptimeRepositoryRegression:
    """Regression tests for SQLAlchemyUptimeRepository."""

    @pytest.mark.regression
    def test_sqlalchemy_uptime_repository_initializes_with_session(self):
        """Test that SQLAlchemyUptimeRepository.__init__ stores session correctly."""
        # Arrange
        mock_session = Mock()

        # Act
        repository = SQLAlchemyUptimeRepository(session=mock_session)

        # Assert
        assert repository._session is mock_session

    @pytest.mark.regression
    def test_create_uptime_record_converts_to_domain_model(self):
        """Test that create converts database model to domain model."""
        # Arrange
        mock_session = Mock()
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.commit.return_value = None
        mock_session.expire_all.return_value = None
        mock_session.connection.return_value.dialect.name = "postgresql"

        repository = SQLAlchemyUptimeRepository(session=mock_session)
        record = UptimeRecord(
            id=0,
            timestamp_utc=datetime.now(),
            status="UP",
            source="healthcheck",
        )

        # Mock the _to_domain_model method to return the record
        with patch.object(repository, "_to_domain_model", return_value=record):
            # Act
            result = repository.create(record)

            # Assert
            assert result is record
            mock_session.add.assert_called_once()
            mock_session.flush.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.regression
    def test_create_uptime_record_handles_sqlite_checkpoint_exception(self):
        """Test that create handles SQLite checkpoint exception gracefully."""
        # Arrange
        mock_session = Mock()
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.commit.return_value = None
        mock_session.expire_all.return_value = None
        mock_connection = Mock()
        mock_connection.dialect.name = "sqlite"
        mock_session.connection.return_value = mock_connection
        mock_connection.execute.side_effect = Exception("Checkpoint failed")

        repository = SQLAlchemyUptimeRepository(session=mock_session)
        record = UptimeRecord(
            id=0,
            timestamp_utc=datetime.now(),
            status="UP",
            source="healthcheck",
        )

        # Mock _to_domain_model to return the record
        with patch.object(repository, "_to_domain_model", return_value=record):
            # Act - Should not raise exception
            result = repository.create(record)

            # Assert
            assert result is record

    @pytest.mark.regression
    def test_to_domain_model_converts_uptime_record(self):
        """Test that _to_domain_model converts NginxUptimeModel to UptimeRecord."""
        # Arrange
        from src.endpoints.log_collector.infrastructure.models import NginxUptimeModel

        mock_session = Mock()
        repository = SQLAlchemyUptimeRepository(session=mock_session)
        db_model = Mock(spec=NginxUptimeModel)
        db_model.id = 1
        db_model.timestamp_utc = datetime.now()
        db_model.status = "UP"
        db_model.source = "healthcheck"
        db_model.details = None

        # Act
        result = repository._to_domain_model(db_model)

        # Assert
        assert isinstance(result, UptimeRecord)
        assert result.id == 1
        assert result.status == "UP"
        assert result.source == "healthcheck"

    @pytest.mark.regression
    def test_find_by_time_range_calls_session_query(self):
        """Test that find_by_time_range calls session query correctly."""
        # Arrange
        from src.endpoints.log_collector.infrastructure.models import NginxUptimeModel

        mock_session = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_db_model = Mock(spec=NginxUptimeModel)
        mock_query.all.return_value = [mock_db_model]
        mock_session.query.return_value = mock_query

        repository = SQLAlchemyUptimeRepository(session=mock_session)
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()

        # Mock _to_domain_model to return a UptimeRecord
        mock_record = UptimeRecord(
            id=1,
            timestamp_utc=datetime.now(),
            status="UP",
            source="healthcheck",
        )
        with patch.object(repository, "_to_domain_model", return_value=mock_record):
            # Act
            result = repository.find_by_time_range(start_time, end_time)

            # Assert
            assert len(result) == 1
            mock_session.query.assert_called_once()

    @pytest.mark.regression
    def test_calculate_uptime_percentage_with_no_records_returns_100(self):
        """Test that calculate_uptime_percentage returns 100% when no records."""
        # Arrange
        mock_session = Mock()
        repository = SQLAlchemyUptimeRepository(session=mock_session)
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()

        # Mock find_by_time_range to return empty list
        with patch.object(repository, "find_by_time_range", return_value=[]):
            # Act
            result = repository.calculate_uptime_percentage(start_time, end_time)

            # Assert
            assert result == 100.0

    @pytest.mark.regression
    def test_calculate_uptime_percentage_calculates_correctly(self):
        """Test that calculate_uptime_percentage calculates percentage correctly."""
        # Arrange
        mock_session = Mock()
        repository = SQLAlchemyUptimeRepository(session=mock_session)
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()

        # Create mock records: 8 UP, 2 DOWN
        mock_records = []
        for i in range(8):
            mock_record = UptimeRecord(
                id=i + 1,
                timestamp_utc=datetime.now(),
                status="UP",
                source="healthcheck",
            )
            mock_records.append(mock_record)
        for i in range(2):
            mock_record = UptimeRecord(
                id=i + 9,
                timestamp_utc=datetime.now(),
                status="DOWN",
                source="healthcheck",
            )
            mock_records.append(mock_record)

        # Mock find_by_time_range to return the records
        with patch.object(repository, "find_by_time_range", return_value=mock_records):
            # Act
            result = repository.calculate_uptime_percentage(start_time, end_time)

            # Assert
            assert result == 80.0  # 8 out of 10 = 80%


class TestUptimeWorkerRegression:
    """Regression tests for UptimeWorker."""

    @pytest.mark.regression
    def test_uptime_worker_start_when_already_running_logs_warning(self):
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

    @pytest.mark.regression
    def test_uptime_worker_stop_when_not_running_returns_early(self):
        """Test that stopping UptimeWorker when not running returns early."""
        # Test line 83: Early return when not running
        async def _test():
            worker = UptimeWorker(interval_seconds=60)
            
            # Stop without starting (should return early)
            await worker.stop()  # Should not raise exception
            
            # Verify _running is False
            assert worker._running is False
        
        asyncio.run(_test())

    @pytest.mark.regression
    def test_uptime_worker_run_loop_handles_exceptions(self):
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

    @pytest.mark.regression
    def test_uptime_worker_check_and_record_performs_health_checks(self):
        """Test that _check_and_record performs health checks for all services."""
        # Test lines 128-192: Health checks and database recording
        async def _test():
            original_db_url = os.environ.get("DATABASE_URL")
            os.environ["DATABASE_URL"] = "sqlite:///:memory:"
            
            try:
                init_database("sqlite:///:memory:")
                
                from src.endpoints.log_collector.infrastructure.models import (
                    NginxAccessLogModel,
                    NginxUptimeModel,
                )
                from src.shared.models.base import Base as SharedBase
                from src.shared.infrastructure.database import get_engine, get_session
                
                engine = get_engine()
                SharedBase.metadata.create_all(engine)
                
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
                await asyncio.sleep(0.2)
                
                session_gen = get_session()
                session = next(session_gen)
                try:
                    from sqlalchemy import text
                    connection = session.connection()
                    if connection.dialect.name == "sqlite":
                        connection.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
                    
                    records = session.query(NginxUptimeModel).order_by(NginxUptimeModel.timestamp_utc.desc()).limit(3).all()
                    
                    # Should have at least 3 records (one for each service)
                    assert len(records) >= 3
                    
                    # Verify sources
                    sources = {r.source for r in records}
                    assert "healthcheck_nginx" in sources
                    assert "healthcheck_log_collector" in sources
                    assert "healthcheck_postgresql" in sources
                finally:
                    session.close()
                    SharedBase.metadata.drop_all(engine)
            finally:
                if original_db_url is not None:
                    os.environ["DATABASE_URL"] = original_db_url
                elif "DATABASE_URL" in os.environ:
                    del os.environ["DATABASE_URL"]
        
        asyncio.run(_test())

    @pytest.mark.regression
    def test_uptime_worker_check_and_record_handles_exceptions(self):
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

    @pytest.mark.regression
    def test_uptime_worker_check_and_record_rolls_back_on_database_error(self):
        """Test that _check_and_record rolls back on database error during recording."""
        # Test lines 187-190: Database error handling during recording
        async def _test():
            original_db_url = os.environ.get("DATABASE_URL")
            os.environ["DATABASE_URL"] = "sqlite:///:memory:"
            
            try:
                init_database("sqlite:///:memory:")
                
                from src.endpoints.log_collector.infrastructure.models import (
                    NginxAccessLogModel,
                    NginxUptimeModel,
                )
                from src.shared.models.base import Base as SharedBase
                from src.shared.infrastructure.database import get_engine, get_session
                
                engine = get_engine()
                SharedBase.metadata.create_all(engine)
                
                worker = UptimeWorker(interval_seconds=60)
                
                # Mock healthcheck service to return UP (so we get past health checks)
                mock_healthcheck = Mock()
                mock_healthcheck.check_nginx_health.return_value = ("UP", None)
                mock_healthcheck.check_log_collector_health.return_value = ("UP", None)
                mock_healthcheck.check_postgresql_health.return_value = ("UP", None)
                worker._healthcheck_service = mock_healthcheck
                
                # Mock repository.create() to raise exception on third call (PostgreSQL recording)
                # This will trigger the exception handler on lines 187-190
                call_count = 0
                
                # Create a mock session with rollback method
                mock_session = Mock()
                mock_session.rollback = Mock()
                mock_session.flush = Mock()
                mock_session.close = Mock()
                
                # Create a wrapper that will raise exception on third call
                original_create_method = None
                def create_wrapper(record):
                    nonlocal call_count, original_create_method
                    call_count += 1
                    if call_count == 3:  # Raise on PostgreSQL recording
                        raise Exception("Database error during recording")
                    # For first two calls, create records normally
                    if original_create_method is None:
                        from src.endpoints.log_collector.infrastructure.repositories import SQLAlchemyUptimeRepository
                        original_repo = SQLAlchemyUptimeRepository(mock_session)
                        original_create_method = original_repo.create
                    return original_create_method(record)
                
                # Patch SQLAlchemyUptimeRepository.create to use our wrapper
                with patch("src.endpoints.log_collector.infrastructure.repositories.SQLAlchemyUptimeRepository.create", side_effect=create_wrapper):
                    # Patch get_session to return our mock session
                    with patch("src.endpoints.log_collector.infrastructure.uptime_worker.get_session") as mock_get_session:
                        def session_generator():
                            yield mock_session
                        mock_get_session.return_value = session_generator()
                        
                        # Execute check and record (should handle exception and rollback)
                        with patch("src.endpoints.log_collector.infrastructure.uptime_worker.logger") as mock_logger:
                            # Should not raise exception (caught by outer try-except on line 193-194)
                            await worker._check_and_record()
                            
                            # Verify error was logged (lines 187-190)
                            mock_logger.error.assert_called()
                            # Find the error call about recording uptime (line 188)
                            error_calls = [call for call in mock_logger.error.call_args_list if "Error recording uptime" in call[0][0]]
                            assert len(error_calls) > 0, "Expected error log about recording uptime"
                            
                            # Verify rollback was called (line 189)
                            mock_session.rollback.assert_called_once()
                
                SharedBase.metadata.drop_all(engine)
            finally:
                if original_db_url is not None:
                    os.environ["DATABASE_URL"] = original_db_url
                elif "DATABASE_URL" in os.environ:
                    del os.environ["DATABASE_URL"]
        
        asyncio.run(_test())

    @pytest.mark.regression
    def test_get_uptime_worker_creates_singleton(self):
        """Test that get_uptime_worker creates a singleton instance."""
        # Test lines 209-220: get_uptime_worker function
        import src.endpoints.log_collector.infrastructure.uptime_worker as uptime_worker_module
        
        # Reset the global worker
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


class TestHealthcheckServiceRegression:
    """Regression tests for HealthcheckService."""

    @pytest.mark.regression
    def test_check_nginx_health_returns_up_on_200_status(self):
        """Test that check_nginx_health returns UP on 200 status code."""
        # Test lines 69-76: Success case with debug logging
        service = HealthcheckService(nginx_url="http://httpbin.org/status/200")
        
        with patch("src.endpoints.log_collector.infrastructure.healthcheck.logger") as mock_logger:
            status, details = service.check_nginx_health()
            
            assert status == "UP"
            assert details is None
            # Verify debug log was called (lines 70-71)
            mock_logger.debug.assert_called()
            debug_call = mock_logger.debug.call_args_list[0]
            assert "Nginx healthcheck successful" in debug_call[0][0]

    @pytest.mark.regression
    def test_check_nginx_health_returns_down_on_non_200_status(self):
        """Test that check_nginx_health returns DOWN on non-200 status code."""
        # Test lines 69-76: Non-200 status code handling
        service = HealthcheckService(nginx_url="http://httpbin.org/status/500")
        
        status, details = service.check_nginx_health()
        
        assert status == "DOWN"
        assert details == "HTTP 500"

    @pytest.mark.regression
    def test_check_nginx_health_handles_unexpected_exception(self):
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

    @pytest.mark.regression
    def test_check_log_collector_health_returns_up_on_200_status(self):
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

    @pytest.mark.regression
    def test_check_log_collector_health_returns_down_on_non_200_status(self):
        """Test that check_log_collector_health returns DOWN on non-200 status code."""
        # Test lines 101-108: Non-200 status code handling
        service = HealthcheckService(log_collector_url="http://httpbin.org/status/404")
        
        status, details = service.check_log_collector_health()
        
        assert status == "DOWN"
        assert details == "HTTP 404"

    @pytest.mark.regression
    def test_check_log_collector_health_handles_request_exception(self):
        """Test that check_log_collector_health handles RequestException."""
        # Test lines 109-111: RequestException handling
        service = HealthcheckService(log_collector_url="http://invalid-url-that-will-fail.com/health")
        
        status, details = service.check_log_collector_health()
        
        assert status == "DOWN"
        assert details is not None
        assert isinstance(details, str)

    @pytest.mark.regression
    def test_check_log_collector_health_handles_unexpected_exception(self):
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

    @pytest.mark.regression
    def test_check_postgresql_health_returns_up_when_connected(self):
        """Test that check_postgresql_health returns UP when database is connected."""
        # Test lines 127-134: PostgreSQL health check success
        original_db_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        
        try:
            init_database("sqlite:///:memory:")
            service = HealthcheckService()
            
            status, details = service.check_postgresql_health()
            
            assert status == "UP"
            assert details is None
        finally:
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]

    @pytest.mark.regression
    def test_check_postgresql_health_returns_down_on_connection_error(self):
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
