# Log Collector Dockerfile
# Multi-stage build for log_collector endpoint

FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy shared code and endpoint-specific code
COPY src/shared/ ./src/shared/
COPY src/endpoints/log_collector/ ./src/endpoints/log_collector/

# Set PATH to include user's local bin
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/logs/uptime?start_time=2024-01-01T00:00:00&end_time=2024-01-01T23:59:59')" || exit 1

# Expose port
EXPOSE 8001

# Run the endpoint's main entry point
CMD ["python", "-m", "src.endpoints.log_collector.main"]

