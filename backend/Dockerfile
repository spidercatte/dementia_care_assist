FROM python:3.12-slim

WORKDIR /app

# Install system dependencies needed for compiling some Python libraries (e.g., ChromaDB dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY . .

# Set default env variables pointing data stores to the persistent volume mount path
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DB_PATH=/app/data/dementia_care.db
ENV CHROMA_DB_PATH=/app/data/chroma_db

# Create directories for persistent storage and ensure permissions are correct
RUN mkdir -p /app/data

EXPOSE 8000

# Start FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
