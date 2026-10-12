FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/
COPY bot.py .

RUN mkdir -p /app/index /app/logs

ENV HF_HOME=/app/.cache/huggingface \
    ANONYMIZED_TELEMETRY=False \
    PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]