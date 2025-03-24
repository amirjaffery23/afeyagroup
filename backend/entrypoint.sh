#!/bin/sh

if [ "$RUN_WEBSOCKETS" = "true" ]; then
    echo "🔌 Starting WebSocket Server..."
    exec uvicorn websockets_server:app --host 0.0.0.0 --port 8001 --reload

elif [ "$RUN_POLYGON_API" = "true" ]; then
    echo "📊 Starting Polygon Stocks API..."
    exec python /app/polygon_stocks_api.py

elif [ "$RUN_FINNHUB_PRODUCER" = "true" ]; then
    echo "📡 Starting Finnhub Producer..."
    exec python /app/finnhub_producer.py

else
    echo "🚀 Starting Default FastAPI App..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi



