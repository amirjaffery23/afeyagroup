FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
ENV PYTHONPATH=/app/src

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    libc-dev \
    libssl-dev \
    libz-dev \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src

# Optional:
# HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
