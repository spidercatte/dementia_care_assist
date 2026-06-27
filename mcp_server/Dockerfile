FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install common library first (better layer caching)
COPY common/ ./common/
RUN pip install --no-cache-dir ./common

COPY mcp_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy mcp_server contents directly so app/ lives at /app/app/
COPY mcp_server/ .

ENV HOST=0.0.0.0
ENV PORT=8002
ENV DB_PATH=/app/data/dementia_care.db
ENV CHROMA_DB_PATH=/app/data/chroma_db

RUN mkdir -p /app/data

EXPOSE 8002

CMD ["uvicorn", "app.mcp_server:app", "--host", "0.0.0.0", "--port", "8002"]
