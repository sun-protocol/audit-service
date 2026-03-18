FROM python:3.11-slim

# Install Node.js (required by Claude Code CLI/SDK)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .

COPY skills/ skills/

# Create non-root user (Claude Code CLI refuses bypassPermissions as root)
RUN useradd -m -s /bin/bash appuser && \
    mkdir -p reports && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.audit_service.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "16"]
