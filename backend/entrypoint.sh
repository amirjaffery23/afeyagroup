#!/bin/sh

set -e

echo "🔄 Entrypoint started..."

if [ "$RUN_WEBSOCKETS" = "true" ]; then
    echo "🔌 Starting WebSocket Server..."
    exec uvicorn websockets_server:app --host 0.0.0.0 --port 8001 --reload

elif [ "$RUN_POLYGON_API" = "true" ]; then
    echo "📊 Starting Polygon Stocks API..."
    exec python /app/microservices/polygon_stocks_service/polygon_stocks_api.py

elif [ "$RUN_FINNHUB_PRODUCER" = "true" ]; then
    echo "📡 Starting Finnhub Producer..."
    exec python /app/microservices/finnhub_service/finnhub_producer.py

elif [ "$RUN_POLYGON_FLATFILES" = "true" ]; then
    echo "🗂️ Starting Polygon Flatfiles Microservice (FastAPI)..."
    exec uvicorn app.microservices.polygon_flatfiles_service.app:app --host 0.0.0.0 --port 8002 --reload

else
    echo "🚀 Starting Default FastAPI Backend..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi