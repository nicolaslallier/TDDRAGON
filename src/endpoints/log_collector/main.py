"""
Main entry point for log_collector endpoint.

Initializes and runs the FastAPI application for log collection service.
"""

import os
import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.endpoints.log_collector.infrastructure.uptime_worker import get_uptime_worker
from src.endpoints.log_collector.presentation.routes import (
    health_router,
    router as logs_router,
)
from src.shared.infrastructure.database import init_database
from src.shared.infrastructure.logger import get_logger

logger = get_logger(__name__)


def run_migrations() -> None:
    """
    Run Alembic migrations.

    Executes database migrations using Alembic.
    """
    try:
        # Change to the log_collector directory where alembic.ini is located
        log_collector_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(log_collector_dir)

        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            logger.info("Database migrations completed successfully")
        else:
            logger.warning(f"Migration command output: {result.stdout}")
            logger.warning(f"Migration command errors: {result.stderr}")
    except FileNotFoundError:
        logger.warning("Alembic not found, skipping migrations")
    except Exception as e:
        logger.error(f"Error running migrations: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown logic for the application.

    Args:
        app: FastAPI application instance.
    """
    # Startup
    logger.info("Starting log_collector endpoint...")

    # Initialize database
    init_database()

    # Run migrations in development mode
    if os.getenv("ENV", "development") == "development":
        logger.info("Running database migrations...")
        run_migrations()

    # Start uptime worker
    uptime_worker = get_uptime_worker()
    await uptime_worker.start()
    logger.info("Uptime worker started")

    logger.info("log_collector endpoint started successfully")

    yield

    # Shutdown
    logger.info("Shutting down log_collector endpoint...")
    await uptime_worker.stop()
    logger.info("Uptime worker stopped")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Sets up routes, middleware, and application configuration.

    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title="Log Collector API",
        description="Log Collector endpoint for v0.2.0 - Nginx log collection and uptime tracking",
        version="0.2.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(logs_router)
    app.include_router(health_router)

    return app


app = create_app()


def main() -> None:
    """
    Main entry point for running the application.

    Starts the Uvicorn server with the FastAPI application.
    """
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8001"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "src.endpoints.log_collector.main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=os.getenv("ENV", "development") == "development",
    )


if __name__ == "__main__":
    main()
