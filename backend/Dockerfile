# Dockerfile for Hugging Face Spaces
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for ChromaDB and HuggingFace cache with proper permissions
RUN mkdir -p /app/chroma_db && chmod 777 /app/chroma_db && \
    mkdir -p /app/.cache/huggingface && chmod -R 777 /app/.cache

# Expose port (HF Spaces uses 7860 by default)
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CHROMA_PERSIST_DIR=/app/chroma_db
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
ENV HUGGINGFACE_HUB_CACHE=/app/.cache/huggingface
# ChromaDB/SQLite specific settings to prevent readonly errors
ENV SQLITE_TMPDIR=/app/chroma_db
ENV TMPDIR=/tmp

# Set umask to ensure all files created by the app are writable
# This fixes ChromaDB's SQLite "readonly database" error
RUN echo "umask 000" >> /etc/profile

# Run the FastAPI server with proper umask
CMD ["sh", "-c", "umask 000 && uvicorn api.server:app --host 0.0.0.0 --port 7860"]
