"""
Database connection management.

Provides database session management and connection pooling for SQLAlchemy.
This module handles database connections in a thread-safe manner suitable
for use in web applications.
"""

import os
from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.shared.infrastructure.logger import get_logger

logger = get_logger(__name__)

# Global engine and session factory
_engine = None
_session_factory = None
_initialized_url = None


def get_database_url() -> str:
    """
    Get database URL from environment variable.

    Reads the DATABASE_URL environment variable. If not set, constructs
    a default PostgreSQL connection string from individual components.

    Returns:
        Database connection URL string.

    Raises:
        ValueError: If database configuration is incomplete.

    Example:
        >>> os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"
        >>> get_database_url()
        'postgresql://user:pass@localhost/db'
    """
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return database_url

    # Fallback to individual components
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "tddragon")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def init_database(database_url: str | None = None) -> None:
    """
    Initialize database engine and session factory.

    Creates a SQLAlchemy engine with connection pooling and a session
    factory. This should be called once at application startup.
    If already initialized with the same URL, this is a no-op.

    Args:
        database_url: Optional database URL. If not provided, uses
                     get_database_url() to determine the URL.

    Example:
        >>> init_database("postgresql://user:pass@localhost/db")
    """
    global _engine, _session_factory, _initialized_url

    if database_url is None:
        database_url = get_database_url()

    # If already initialized with the same URL, skip reinitialization
    if _engine is not None and _initialized_url == database_url:
        return

    logger.info(
        f"Initializing database connection: {database_url.split('@')[1] if '@' in database_url else '***'}"
    )

    # SQLite doesn't support pool_size and max_overflow
    # Only use these parameters for PostgreSQL
    engine_kwargs: dict[str, Any] = {
        "pool_pre_ping": True,  # Verify connections before using
        "echo": False,  # Set to True for SQL query logging
    }

    # PostgreSQL-specific pool parameters
    if database_url.startswith("postgresql"):
        engine_kwargs.update(
            {
                "pool_size": 5,  # Number of connections to maintain
                "max_overflow": 10,  # Additional connections beyond pool_size
            }
        )
    elif database_url.startswith("sqlite"):
        # SQLite-specific: Use WAL mode for better concurrency and connection isolation
        # This allows multiple connections to see committed data immediately
        # Use StaticPool with size=1 for SQLite to ensure all sessions share the same connection
        # This is necessary for E2E tests where we need cross-session visibility
        from sqlalchemy.pool import StaticPool

        engine_kwargs["poolclass"] = StaticPool
        engine_kwargs["connect_args"] = {"check_same_thread": False}
        # StaticPool with size=1 ensures all sessions share the same connection
        # This makes committed data immediately visible to all sessions

    _engine = create_engine(database_url, **engine_kwargs)

    # Enable WAL mode for SQLite file-based databases for better concurrency
    # WAL mode allows multiple connections to see committed data immediately
    if database_url.startswith("sqlite:///") and not database_url.startswith(
        "sqlite:///:memory:"
    ):

        def enable_wal(dbapi_conn, connection_record):  # noqa: ARG001
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")  # Faster than FULL, still safe
            # Set busy_timeout to avoid locking issues
            cursor.execute("PRAGMA busy_timeout=30000")  # 30 seconds
            cursor.close()

        from sqlalchemy import event

        event.listen(_engine, "connect", enable_wal)

    _session_factory = sessionmaker(
        bind=_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    _initialized_url = database_url
    logger.info("Database connection initialized successfully")


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session.

    Provides a database session using dependency injection pattern.
    The session is automatically closed after use. This function is
    designed to be used as a FastAPI dependency.

    Yields:
        SQLAlchemy Session instance.

    Raises:
        RuntimeError: If database has not been initialized.

    Example:
        >>> init_database()
        >>> with next(get_session()) as session:
        ...     # Use session
        ...     pass
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    session = _session_factory()
    try:
        yield session
    finally:
        session.close()


def get_engine():
    """
    Get the database engine.

    Returns the SQLAlchemy engine instance. Used primarily for
    Alembic migrations.

    Returns:
        SQLAlchemy Engine instance.

    Raises:
        RuntimeError: If database has not been initialized.
    """
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    return _engine
