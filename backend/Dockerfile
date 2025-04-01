FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies including librdkafka
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libssl-dev \
    libz-dev \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the actual application code (from backend/)
COPY . .

# Optional environment defaults (override in docker-compose)
ENV KAFKA_BROKER=kafka:9092

# Make Python scripts executable if needed (only if you execute them directly via bash)
RUN chmod +x app/microservices/finnhub_service/finnhub_producer.py
RUN chmod +x app/microservices/polygon_stocks_service/polygon_stocks_api.py
RUN chmod +x app/microservices/polygon_flatfiles_service/polygon_flatfiles.py

# Copy and make entrypoint executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Default CMD delegates to entrypoint.sh
CMD ["/entrypoint.sh"]
