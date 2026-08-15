# =========================
# Stage 1: Build
# =========================
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


# =========================
# Stage 2: Production
# =========================
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Put virtual environment first in PATH
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd \
    --create-home \
    --shell /bin/bash \
    appuser

# Copy application
COPY app ./app

# Change ownership
RUN chown -R appuser:appuser /app

# Run as non-root user
USER appuser

# Application port
EXPOSE 8000

# Container health check
HEALTHCHECK --interval=30s \
            --timeout=5s \
            --start-period=10s \
            --retries=3 \
            CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
