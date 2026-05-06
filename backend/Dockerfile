# --- Build the FastAPI app image ---
FROM python:3.11-slim

WORKDIR /app

# System dependencies for pymysql + bcrypt
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY app/ /app/app/

# Storage directory (will be mounted as a volume)
RUN mkdir -p /app/storage

EXPOSE 8000

# Run with 1 worker to keep memory low (single-vCPU VPS)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
