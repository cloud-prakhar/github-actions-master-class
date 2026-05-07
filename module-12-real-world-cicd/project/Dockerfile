# =============================================================================
# Dockerfile — Production-ready multi-stage build for Python 3.14 Flask app
#
# Multi-stage build pattern:
#   Stage 1 (builder): Install dependencies in a full image
#   Stage 2 (production): Copy only what's needed into a slim image
#
# Why multi-stage?
#   - Smaller final image (no build tools, no pip cache)
#   - Better security (fewer packages = fewer vulnerabilities)
#   - Faster pulls in CI and Kubernetes
# =============================================================================

# ─── STAGE 1: Builder ─────────────────────────────────────────────────────────
# Install dependencies here. The build tools stay in this stage only.
FROM python:3.14-slim AS builder

WORKDIR /build

# Copy dependency files first (Docker layer caching: only re-run pip when
# requirements change, not when source code changes)
COPY requirements.txt .

# Install dependencies into /install prefix so we can copy them cleanly
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─── STAGE 2: Production Image ────────────────────────────────────────────────
# Start fresh from a slim base — no pip, no build tools
FROM python:3.14-slim AS production

# OCI-standard image labels (good practice for traceability)
LABEL org.opencontainers.image.title="GitHub Actions CI/CD Demo App"
LABEL org.opencontainers.image.description="Python 3.14 Flask app for the GitHub Actions Master Class"
LABEL org.opencontainers.image.source="https://github.com/your-org/github-actions-master-class"

# Copy installed packages from the builder stage
COPY --from=builder /install /usr/local

WORKDIR /app

# Create a non-root user for security (never run as root in production)
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

# Copy application source code
COPY src/ ./src/

# Change ownership to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 3000

# Health check: Docker will periodically check the /health endpoint.
# If it fails 3 times, the container is marked unhealthy.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/health')" \
    || exit 1

# Environment defaults (override at runtime)
ENV PORT=3000 \
    APP_ENV=production \
    PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Start the app with gunicorn (production WSGI server, not Flask's dev server)
# -w 4     : 4 worker processes
# -b       : bind to all interfaces on $PORT
# --access-logfile - : log access to stdout (for container log collection)
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:${PORT} --access-logfile - 'app:create_app()' --chdir /app/src"]
