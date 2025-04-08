from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter.depends import RateLimiter
from fastapi_limiter import FastAPILimiter
from redis import asyncio as aioredis
from sqlalchemy.orm import Session
import requests
import json
from aiokafka import AIOKafkaProducer
import asyncio

from core.config import PolygonStocksSettings

settings = PolygonStocksSettings()

from routes import stock_router, user_router
from core.db import get_db
from util.logging_config import configure_logging
from services.polygon_flatfiles_service.polygon_flatfiles import app as polygon_flatfiles_app

# -------------------------------
# Configure logging before anything else
# -------------------------------
configure_logging()

# -------------------------------
# FastAPI App
# -------------------------------
app = FastAPI(
    title="Stock Portfolio API",
    description="A REST API for fetching, storing, and managing stock data.",
    version="1.0.0"
)

# -------------------------------
# CORS Config
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.59:3000",  # Your VM's IP
        "http://stock.local:3000",   # If you mapped a custom name],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Endpoints
# -------------------------------
@app.get("/health")
async def healthcheck():
    return {"status": "ok"}

@app.get("/api/stock-search")
def search_stock(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        response = requests.get(f"https://finnhub.io/api/v1/search?q={query}&token={settings.FINNHUB_API_KEY}")
        response.raise_for_status()
        data = response.json()
        if data['count'] == 0:
            return {"message": "No results found", "results": []}
        return {"message": "Success", "results": data['result']}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock suggestions: {str(e)}")

# -------------------------------
# Redis Configuration
# -------------------------------
@app.on_event("startup")
async def startup_event():
    """Initialize Redis for Rate Limiting."""
    app.state.redis = aioredis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    await FastAPILimiter.init(app.state.redis)

@app.on_event("shutdown")
async def shutdown_event():
    """Properly close Redis connection."""
    if hasattr(app.state, "redis"):
        await app.state.redis.close()

@app.get("/", tags=["General"])
def root():
    return {"message": "Welcome to the Stock Portfolio API"}

# -------------------------------
# Middleware Example
# -------------------------------
def validate_api_key(token: str = Header(None, alias="X-Finnhub-Token")):
    api_key = settings.FINNHUB_API_KEY
    if not token:
        raise HTTPException(status_code=401, detail="Missing X-Finnhub-Token header")
    if token != api_key:
        raise HTTPException(status_code=403, detail="Invalid API token")
    return token

# -------------------------------
# Protected & Public Endpoints
# -------------------------------
@app.get("/api/v1/protected", dependencies=[Depends(RateLimiter(times=30, seconds=1))], tags=["General"])
def protected_endpoint():
    return {"message": "This endpoint is rate-limited and requires authentication"}

@app.get("/api/allstock-search")
def search_stock(query: str, db: Session = Depends(get_db)):
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    response = requests.get(f"https://finnhub.io/api/v1/search?q={query}&token={settings.FINNHUB_API_KEY}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching stock symbols")
    return response.json()

@app.get("/api/stock-quote")
def get_stock_quote(symbol: str):
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol cannot be empty")
    try:
        response = requests.get(f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={settings.FINNHUB_API_KEY}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")

@app.get("/api/quote")
def get_stock_quote(symbol: str, db: Session = Depends(get_db)):
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol cannot be empty")
    response = requests.get(f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={settings.FINNHUB_API_KEY}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching stock data")
    return response.json()

# -------------------------------
# Kafka Integration
# -------------------------------
async def publish_to_kafka(topic: str, message: dict):
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    await producer.start()
    try:
        await producer.send_and_wait(topic, message)
        app.logger.debug(f"Published message to Kafka topic {topic}: {message}")
    finally:
        await producer.stop()

@app.post("/api/publish-stock-data")
async def publish_stock_data(symbol: str, db: Session = Depends(get_db)):
    response = requests.get(f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={settings.FINNHUB_API_KEY}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching stock data")
    stock_data = response.json()
    message = {
        "symbol": symbol,
        "current_price": stock_data["c"],
        "open_price": stock_data["o"],
        "high_price": stock_data["h"],
        "low_price": stock_data["l"],
        "previous_close_price": stock_data["pc"],
        "price_change_percentage": ((stock_data["c"] - stock_data["pc"]) / stock_data["pc"] * 100)
    }
    await publish_to_kafka("stock-data", message)
    return {"message": "Stock data published to Kafka"}

# -------------------------------
# Routers & Mounted Apps
# -------------------------------
app.include_router(stock_router, prefix="/api", tags=["stocks"])
app.include_router(user_router, prefix="/api", tags=["users"])

app.mount("/polygon-files", polygon_flatfiles_app)
