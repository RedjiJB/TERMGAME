# Multi-stage build for TermGame

# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml .
COPY README.md .
COPY src/ src/

# Install dependencies
RUN uv pip install --system .

# Runtime stage
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/termgame /usr/local/bin/termgame
COPY scenarios/ scenarios/

# Create non-root user
RUN useradd -m -u 1000 termgame && \
    chown -R termgame:termgame /app

USER termgame

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TERMGAME_DATA_DIR=/app/data

# Create data directory
RUN mkdir -p /app/data

ENTRYPOINT ["termgame"]
CMD ["--help"]
