# Bitcoin CLI Wrapper Dockerfile
# Multi-stage build for optimized production image

# =============================================================================
# BUILD STAGE
# =============================================================================
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0
ARG VCS_REF

# Add metadata
LABEL maintainer="Bitcoin CLI Wrapper Team" \
      version="${VERSION}" \
      description="Secure Bitcoin RPC CLI Wrapper" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}"

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# =============================================================================
# PRODUCTION STAGE
# =============================================================================
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create non-root user for security
RUN groupadd -r bitcoin && useradd -r -g bitcoin -s /bin/bash bitcoin

# Set up directories
RUN mkdir -p /app /app/lib /app/logs /app/certs /run/secrets \
    && chown -R bitcoin:bitcoin /app

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=bitcoin:bitcoin bitcoin_cli_wrapper.py /app/
COPY --chown=bitcoin:bitcoin lib/ /app/lib/
COPY --chown=bitcoin:bitcoin .env.example /app/.env

# Set up Python path
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 /app/bitcoin_cli_wrapper.py getblockchaininfo || exit 1

# Switch to non-root user
USER bitcoin

# Create volume mount points
VOLUME ["/app/logs", "/app/certs", "/app/config"]

# Expose port (if needed for future web interface)
EXPOSE 8080

# Use tini as init system for proper signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]

# Default command
CMD ["python3", "/app/bitcoin_cli_wrapper.py", "--help"]

# =============================================================================
# DEVELOPMENT STAGE (for development with hot reload)
# =============================================================================
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN /opt/venv/bin/pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-mock \
    black \
    flake8 \
    mypy

# Switch back to bitcoin user
USER bitcoin

# Override entrypoint for development
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/bin/bash"]