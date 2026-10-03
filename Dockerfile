# ==========================================
# STAGE 1: Builder
# ==========================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies for compiling wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition
COPY requirements.txt .

# Compile dependencies into wheels
RUN pip install --no-cache-dir --upgrade pip wheel && \
    pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# ==========================================
# STAGE 2: Runtime
# ==========================================
FROM python:3.12-slim AS runtime

# Set environment variables for Python runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install runtime library dependencies (e.g., libpq for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-compiled wheels from builder stage
COPY --from=builder /build/wheels /app/wheels

# Install pre-compiled wheels
RUN pip install --no-cache-dir --no-index --find-links=/app/wheels /app/wheels/* && \
    rm -rf /app/wheels

# Copy application source code
COPY src /app/src

# Create non-root user for principle of least privilege (Security hardening)
RUN useradd -u 8888 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Healthcheck probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to execute ASGI server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
