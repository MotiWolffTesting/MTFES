FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc curl ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download NLTK resources to avoid runtime downloads
ENV NLTK_DATA=/usr/local/share/nltk_data
RUN mkdir -p "$NLTK_DATA" && \
    python - <<'PY'
import nltk
nltk.download('vader_lexicon', download_dir='/usr/local/share/nltk_data')
nltk.download('punkt', download_dir='/usr/local/share/nltk_data')
PY

# Copy application code
COPY app/ ./app/
COPY data/ ./data/

# Create necessary directories
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
