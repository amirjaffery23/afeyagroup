FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies including librdkafka
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libssl-dev \
    libz-dev \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt requirements.txt

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables
ENV KAFKA_BROKER=kafka:9092

# Ensure finnhub_producer.py is executable
RUN chmod +x app/finnhub_producer.py

# Ensure finnhub_producer.py is executable
RUN chmod +x app/polygon_stocks_api.py

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]

# Command to run the application
#CMD ["sh", "-c", "if [ \"$RUN_WEBSOCKETS\" = 'true' ]; then uvicorn websockets_server:app --host 0.0.0.0 --port 8001 --reload; else uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; fi"]

