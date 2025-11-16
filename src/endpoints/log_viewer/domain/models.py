"""
Domain models for log viewer.

Reuses models from log_collector endpoint.
"""

from src.endpoints.log_collector.domain.models import LogEntry, UptimeRecord

__all__ = ["LogEntry", "UptimeRecord"]

