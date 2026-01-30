# Use a slim Python image
FROM python:3.10-slim

# Install system dependencies (Required for Postgres)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (The standalone installer is best for Docker)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# 1. Copy dependency definitions first (to leverage Docker caching)
COPY pyproject.toml uv.lock ./

# 2. Install dependencies using uv
# --system: Installs into the system Python (no venv needed inside Docker)
# --deploy: Fails if uv.lock is out of sync with pyproject.toml
RUN uv sync --frozen --no-dev

# 3. Copy the rest of the application code
COPY . .

# Expose port
EXPOSE 8080

# Run the application
# We use 'python -m streamlit' to ensure path resolution works correctly
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]