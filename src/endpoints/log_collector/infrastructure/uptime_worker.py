"""
Background worker for recording uptime measurements.

Periodically checks Nginx health and records uptime measurements to the database.
"""

import asyncio
import os
from typing import Optional

from src.endpoints.log_collector.infrastructure.healthcheck import HealthcheckService
from src.endpoints.log_collector.presentation.dependencies import (
    get_calculate_uptime_use_case,
)
from src.shared.infrastructure.database import get_session
from src.shared.infrastructure.logger import get_logger

logger = get_logger(__name__)


class UptimeWorker:
    """
    Background worker that periodically records uptime measurements.

    This worker runs in the background and periodically checks Nginx health,
    then records the status to the database.
    """

    def __init__(
        self,
        interval_seconds: int = 60,
        nginx_url: Optional[str] = None,
        log_collector_url: Optional[str] = None,
    ) -> None:
        """
        Initialize UptimeWorker.

        Args:
            interval_seconds: Interval between health checks in seconds (default: 60).
            nginx_url: URL to check Nginx health (optional, uses env var or default).
            log_collector_url: URL to check log-collector health (optional, uses env var or default).
        """
        self._interval = interval_seconds
        self._healthcheck_service = HealthcheckService(
            nginx_url=nginx_url,
            log_collector_url=log_collector_url,
        )
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """
        Start the uptime worker.

        Begins periodic health checks and uptime recording.
        """
        if self._running:
            logger.warning("UptimeWorker is already running")
            return

        self._running = True
        logger.info(
            f"Starting UptimeWorker with {self._interval}s interval for health checks"
        )
        # Start periodic loop (will wait 5 seconds before first check)
        self._task = asyncio.create_task(self._run_loop())
        # Also run an immediate check (don't await, let it run in background)
        immediate_task = asyncio.create_task(self._check_and_record())
        # Log if immediate check fails
        immediate_task.add_done_callback(
            lambda t: logger.error(f"Immediate health check failed: {t.exception()}")
            if t.exception()
            else None
        )

    async def stop(self) -> None:
        """
        Stop the uptime worker.

        Stops periodic health checks gracefully.
        """
        if not self._running:
            return

        logger.info("Stopping UptimeWorker...")
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("UptimeWorker stopped")

    async def _run_loop(self) -> None:
        """
        Main worker loop.

        Periodically checks health and records uptime measurements.
        """
        while self._running:
            try:
                await self._check_and_record()
            except Exception as e:
                logger.error(f"Error in UptimeWorker loop: {e}", exc_info=True)

            # Wait for next interval
            try:
                await asyncio.sleep(self._interval)
            except asyncio.CancelledError:
                break

    async def _check_and_record(self) -> None:
        """
        Check health and record uptime measurements for all services.

        Performs health checks for Nginx, log-collector, and PostgreSQL,
        then records the results to the database.
        """
        try:
            loop = asyncio.get_event_loop()

            logger.debug("Starting health checks for all services...")
            # Check all services in parallel (run in executor to avoid blocking)
            nginx_status, nginx_details = await loop.run_in_executor(
                None, self._healthcheck_service.check_nginx_health
            )
            log_collector_status, log_collector_details = await loop.run_in_executor(
                None, self._healthcheck_service.check_log_collector_health
            )
            postgresql_status, postgresql_details = await loop.run_in_executor(
                None, self._healthcheck_service.check_postgresql_health
            )
            logger.debug(
                f"Health check results - Nginx: {nginx_status}, "
                f"Log Collector: {log_collector_status}, "
                f"PostgreSQL: {postgresql_status}"
            )

            # Record uptime measurements for all services
            session_gen = get_session()
            session = next(session_gen)
            try:
                # Create use case with session directly (not using Depends)
                from src.endpoints.log_collector.application.calculate_uptime import (
                    CalculateUptime,
                )
                from src.endpoints.log_collector.infrastructure.repositories import (
                    SQLAlchemyUptimeRepository,
                )

                repository = SQLAlchemyUptimeRepository(session)
                use_case = CalculateUptime(repository=repository)

                # Record Nginx uptime
                nginx_record = use_case.record_uptime(
                    status=nginx_status,
                    source="healthcheck_nginx",
                    details=nginx_details,
                )
                logger.info(
                    f"Recorded Nginx uptime: {nginx_record.status} at {nginx_record.timestamp_utc}"
                )

                # Record log-collector uptime
                log_collector_record = use_case.record_uptime(
                    status=log_collector_status,
                    source="healthcheck_log_collector",
                    details=log_collector_details,
                )
                logger.info(
                    f"Recorded log-collector uptime: {log_collector_record.status} at {log_collector_record.timestamp_utc}"
                )

                # Record PostgreSQL uptime
                postgresql_record = use_case.record_uptime(
                    status=postgresql_status,
                    source="healthcheck_postgresql",
                    details=postgresql_details,
                )
                logger.info(
                    f"Recorded PostgreSQL uptime: {postgresql_record.status} at {postgresql_record.timestamp_utc}"
                )
                # Repository.create() already commits, but ensure session is flushed
                session.flush()
                logger.debug("Successfully recorded all uptime measurements")
            except Exception as e:
                logger.error(f"Error recording uptime: {e}", exc_info=True)
                session.rollback()
                raise
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Error checking and recording uptime: {e}", exc_info=True)


# Global worker instance
_worker: Optional[UptimeWorker] = None


def get_uptime_worker() -> UptimeWorker:
    """
    Get or create the global UptimeWorker instance.

    Returns:
        UptimeWorker instance.
    """
    global _worker
    if _worker is None:
        interval = int(os.getenv("UPTIME_CHECK_INTERVAL", "60"))
        nginx_url = os.getenv("NGINX_HEALTHCHECK_URL", "http://nginx/health")
        log_collector_url = os.getenv(
            "LOG_COLLECTOR_HEALTHCHECK_URL", "http://log-collector:8001/health"
        )
        _worker = UptimeWorker(
            interval_seconds=interval,
            nginx_url=nginx_url,
            log_collector_url=log_collector_url,
        )
    return _worker

