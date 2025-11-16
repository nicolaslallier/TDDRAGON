"""
Healthcheck service for monitoring service availability.

Checks health of Nginx, log-collector, and PostgreSQL.
"""

import os
from typing import Optional

import requests
from requests.exceptions import RequestException
from sqlalchemy import text

from src.shared.infrastructure.database import get_engine
from src.shared.infrastructure.logger import get_logger

logger = get_logger(__name__)


class HealthcheckService:
    """
    Service for checking health status of multiple services.

    This service performs health checks against Nginx, log-collector,
    and PostgreSQL to determine if services are UP or DOWN.
    """

    def __init__(
        self,
        nginx_url: Optional[str] = None,
        log_collector_url: Optional[str] = None,
        timeout: int = 5,
    ) -> None:
        """
        Initialize HealthcheckService.

        Args:
            nginx_url: URL to check Nginx health (defaults to NGINX_HEALTHCHECK_URL env var or http://nginx/health).
            log_collector_url: URL to check log-collector health (defaults to LOG_COLLECTOR_HEALTHCHECK_URL env var or http://log-collector:8001/health).
            timeout: Request timeout in seconds.
        """
        self._nginx_url = (
            nginx_url
            or os.getenv("NGINX_HEALTHCHECK_URL", "http://nginx/health")
        )
        self._log_collector_url = (
            log_collector_url
            or os.getenv("LOG_COLLECTOR_HEALTHCHECK_URL", "http://log-collector:8001/health")
        )
        self._timeout = timeout

    def check_nginx_health(self) -> tuple[str, Optional[str]]:
        """
        Check Nginx health status.

        Makes an HTTP GET request to the Nginx healthcheck URL.

        Returns:
            Tuple of (status, details) where:
            - status: "UP" or "DOWN"
            - details: Optional error message if DOWN, None if UP
        """
        try:
            response = requests.get(
                self._nginx_url,
                timeout=self._timeout,
                allow_redirects=True,
            )
            if response.status_code == 200:
                logger.debug(f"Nginx healthcheck successful: {self._nginx_url}")
                return ("UP", None)
            else:
                logger.warning(
                    f"Nginx healthcheck returned status {response.status_code}: {self._nginx_url}"
                )
                return ("DOWN", f"HTTP {response.status_code}")
        except RequestException as e:
            logger.warning(f"Nginx healthcheck failed: {e}")
            return ("DOWN", str(e))
        except Exception as e:
            logger.error(f"Unexpected error during Nginx healthcheck: {e}", exc_info=True)
            return ("DOWN", f"Unexpected error: {str(e)}")

    def check_log_collector_health(self) -> tuple[str, Optional[str]]:
        """
        Check log-collector health status.

        Makes an HTTP GET request to the log-collector healthcheck URL.

        Returns:
            Tuple of (status, details) where:
            - status: "UP" or "DOWN"
            - details: Optional error message if DOWN, None if UP
        """
        try:
            response = requests.get(
                self._log_collector_url,
                timeout=self._timeout,
                allow_redirects=True,
            )
            if response.status_code == 200:
                logger.debug(f"Log-collector healthcheck successful: {self._log_collector_url}")
                return ("UP", None)
            else:
                logger.warning(
                    f"Log-collector healthcheck returned status {response.status_code}: {self._log_collector_url}"
                )
                return ("DOWN", f"HTTP {response.status_code}")
        except RequestException as e:
            logger.warning(f"Log-collector healthcheck failed: {e}")
            return ("DOWN", str(e))
        except Exception as e:
            logger.error(f"Unexpected error during log-collector healthcheck: {e}", exc_info=True)
            return ("DOWN", f"Unexpected error: {str(e)}")

    def check_postgresql_health(self) -> tuple[str, Optional[str]]:
        """
        Check PostgreSQL database health status.

        Executes a simple SQL query to verify database connectivity.

        Returns:
            Tuple of (status, details) where:
            - status: "UP" or "DOWN"
            - details: Optional error message if DOWN, None if UP
        """
        try:
            engine = get_engine()
            with engine.connect() as connection:
                # Execute a simple query to check database connectivity
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
                logger.debug("PostgreSQL healthcheck successful")
                return ("UP", None)
        except Exception as e:
            logger.warning(f"PostgreSQL healthcheck failed: {e}")
            return ("DOWN", str(e))

