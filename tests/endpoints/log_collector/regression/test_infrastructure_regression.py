"""
Regression tests for log collector infrastructure layer.

Ensures that infrastructure components continue to work correctly after changes.
"""

import tempfile
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.endpoints.log_collector.domain.models import LogEntry, UptimeRecord
from src.endpoints.log_collector.infrastructure.log_reader import LogReader
from src.endpoints.log_collector.infrastructure.repositories import (
    SQLAlchemyLogRepository,
    SQLAlchemyUptimeRepository,
)


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
