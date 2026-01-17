# Development container for POC DTA MCP
FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Install additional system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    postgresql-client \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml /tmp/
RUN pip install --no-cache-dir psycopg2-binary python-dotenv fastmcp pandas sqlalchemy \
    && pip install --no-cache-dir pytest pytest-asyncio black ruff

# Set working directory
WORKDIR /workspace
