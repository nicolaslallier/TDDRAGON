"""
Main entry point for log_viewer endpoint.

Initializes and runs the FastAPI application for log viewer UI.
"""

import os
import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src.endpoints.log_viewer.presentation.routes import router as log_viewer_router
from src.shared.infrastructure.database import init_database
from src.shared.infrastructure.logger import get_logger

logger = get_logger(__name__)


def run_migrations() -> None:
    """
    Run Alembic migrations.

    Executes database migrations using Alembic from the log_collector directory
    (where migrations are defined).
    """
    try:
        # Get project root (where src/ directory is located)
        # In Docker container, working directory is /app, which is the project root
        # Calculate project root from current file location
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        endpoints_dir = os.path.dirname(current_file_dir)
        src_dir = os.path.dirname(endpoints_dir)
        project_root = os.path.dirname(src_dir)
        
        # Use current working directory if it's a valid project root (has src/ subdirectory)
        # Otherwise use calculated path
        cwd = os.getcwd()
        if os.path.exists(os.path.join(cwd, "src")):
            project_root = cwd
        
        log_collector_dir = os.path.join(project_root, "src", "endpoints", "log_collector")
        
        if not os.path.exists(log_collector_dir):
            logger.warning(f"Log collector directory not found: {log_collector_dir}")
            return
        
        original_dir = os.getcwd()
        original_pythonpath = os.environ.get("PYTHONPATH", "")
        
        # Set PYTHONPATH to include project root so imports work
        pythonpath = project_root
        if original_pythonpath:
            pythonpath = f"{project_root}:{original_pythonpath}"
        
        # Create environment dict with updated PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = pythonpath
        
        os.chdir(log_collector_dir)

        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=False,
            env=env,
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
    finally:
        # Restore original directory and PYTHONPATH
        try:
            os.chdir(original_dir)
        except NameError:
            pass
        try:
            if original_pythonpath:
                os.environ["PYTHONPATH"] = original_pythonpath
            elif "PYTHONPATH" in os.environ:
                del os.environ["PYTHONPATH"]
        except NameError:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown logic for the application.

    Args:
        app: FastAPI application instance.
    """
    # Startup
    logger.info("Starting log_viewer endpoint...")

    # Initialize database
    init_database()

    # Run migrations in development mode
    if os.getenv("ENV", "development") == "development":
        logger.info("Running database migrations...")
        run_migrations()

    logger.info("log_viewer endpoint started successfully")

    yield

    # Shutdown
    logger.info("Shutting down log_viewer endpoint...")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Sets up routes, middleware, static files, and application configuration.

    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title="Log Viewer API",
        description="Log Viewer endpoint for v0.3.0 - Web UI for querying and visualizing Nginx logs",
        version="0.3.0",
        lifespan=lifespan,
    )

    # Configure session middleware for authentication
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv("SESSION_SECRET_KEY", "dev-secret-key-change-in-production"),
        max_age=3600,  # 1 hour
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static files
    _static_dir = os.path.join(os.path.dirname(__file__), "presentation", "static")
    app.mount(
        "/static",
        StaticFiles(directory=_static_dir),
        name="static",
    )

    # Register routers
    app.include_router(log_viewer_router)

    return app


app = create_app()


def main() -> None:
    """
    Main entry point for running the application.

    Starts the Uvicorn server with the FastAPI application.
    """
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8002"))  # Different port from other endpoints
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "src.endpoints.log_viewer.main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=os.getenv("ENV", "development") == "development",
    )


if __name__ == "__main__":
    main()

