FROM python:3.12-slim

LABEL maintainer="INFRAGUARD Engineering Platform"
LABEL description="INFRAGUARD — Autonomous Infrastructure Health Monitoring & Structural Integrity Twin"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Install system dependencies required by OpenCV & Scikit-Image
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY sample_data/ ./sample_data/
COPY smoke_test.py ./

# Ensure benchmark sample data exists
RUN python -m sample_data.generate_demo_data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

CMD ["sh", "-c", "python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
