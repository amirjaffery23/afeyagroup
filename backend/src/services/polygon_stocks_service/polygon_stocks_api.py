import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

import asyncpg
import httpx
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import FastAPI, HTTPException

from core.config import PolygonStocksSettings

print(">>> DEBUG ENV", dict(os.environ), flush=True)

# ----- Load Settings -----
settings = PolygonStocksSettings()

# ----- Logging -----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----- Settings -----
API_KEY = settings.POLYGON_API_KEY
FINNHUB_API_KEY = settings.FINNHUB_API_KEY
DB_URL = settings.DATABASE_URL
KAFKA_BROKER = settings.KAFKA_BOOTSTRAP_SERVERS
TOPIC = "new-stock-data"
GROUP_ID = "stock-group"
MAX_RETRIES = 5
RETRY_DELAY = 5

db_pool = None
producer = None

# ----- FastAPI App -----
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, producer
    tasks = []
    try:
        logger.info("🚀 Connecting to PostgreSQL...")
        db_pool = await asyncpg.create_pool(DB_URL)
        logger.info("✅ PostgreSQL pool created")

        producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKER)
        await safe_start_producer(producer)
        logger.info("✅ Kafka producer started")

        tasks.extend([
            asyncio.create_task(fetch_and_store_historical_data()),
            asyncio.create_task(schedule_daily_updates()),
            asyncio.create_task(fetch_missing_data()),
            asyncio.create_task(consume())
        ])

        yield

    finally:
        logger.info("🟣 Shutting down gracefully...")
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"Cancelled task: {task}")

        if db_pool:
            await db_pool.close()
            logger.info("🔌 PostgreSQL pool closed")
        if producer:
            await producer.stop()
            logger.info("✅ Kafka producer stopped")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def home():
    return {"message": "Polygon Stocks API is running"}

@app.get("/test-db")
async def test_db():
    if not db_pool:
        return {"error": "Database pool is not initialized"}
    try:
        async with db_pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
        return {"status": "DB Connected", "result": result}
    except Exception as e:
        return {"error": str(e)}

# ----- Utility Functions -----

async def save_to_db(stock_data: dict):
    if not db_pool:
        logger.error("DB Pool not initialized")
        return
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO historicalstockdata (ticker, date, open, close, high, low, volume, trades)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (ticker, date) DO NOTHING
                """,
                stock_data["ticker"],
                datetime.strptime(stock_data["date"], "%Y-%m-%d").date(),
                stock_data["open"],
                stock_data["close"],
                stock_data["high"],
                stock_data["low"],
                stock_data["volume"],
                stock_data["trades"],
            )
            logger.info(f"Inserted data for {stock_data['ticker']} on {stock_data['date']}")
    except Exception as e:
        logger.error(f"Error saving to DB: {e}")

async def publish_to_kafka(topic: str, message: dict):
    if not producer:
        logger.error("Producer is not initialized")
        return
    try:
        await producer.send_and_wait(topic, value=json.dumps(message).encode("utf-8"))
        logger.info(f"Published message to Kafka [{topic}]: {message}")
    except Exception as e:
        logger.error(f"Kafka publish error: {e}")

async def fetch_stock_symbols():
    if not db_pool:
        logger.error("DB Pool not initialized")
        return []
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT stock_symbol FROM allstock")
        return [row["stock_symbol"] for row in rows]
    except Exception as e:
        logger.error(f"Error fetching symbols: {e}")
        return []

# ----- Scheduled Tasks -----

async def schedule_daily_updates():
    while True:
        next_run = datetime.utcnow() + timedelta(minutes=5)
        logger.info(f"Next update scheduled at: {next_run}")
        await asyncio.sleep((next_run - datetime.utcnow()).total_seconds())
        await update_daily_data()

async def update_daily_data():
    logger.info("Fetching today's data...")
    stock_symbols = await fetch_stock_symbols()
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    for symbol in stock_symbols:
        logger.info(f"Updating daily data for {symbol}")
        await fetch_historical_data_for_symbol(symbol, yesterday.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))

async def fetch_and_store_historical_data():
    logger.info("Fetching 2-year historical data...")
    stock_symbols = await fetch_stock_symbols()
    today = datetime.utcnow().date()
    two_years_ago = today - timedelta(days=730)

    batch_size = 5
    for i in range(0, len(stock_symbols), batch_size):
        for symbol in stock_symbols[i:i + batch_size]:
            await fetch_historical_data_for_symbol(symbol, two_years_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        await asyncio.sleep(60)

async def fetch_missing_data():
    logger.info("Checking for missing data...")
    stock_symbols = await fetch_stock_symbols()
    yesterday = datetime.utcnow().date() - timedelta(days=1)

    for symbol in stock_symbols:
        try:
            async with db_pool.acquire() as conn:
                count = await conn.fetchval("SELECT COUNT(*) FROM historicalstockdata WHERE ticker = $1 AND date = $2", symbol, yesterday)
                if count == 0:
                    logger.warning(f"Missing data for {symbol} on {yesterday}, fetching now...")
                    await fetch_historical_data_for_symbol(symbol, yesterday.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d"))
        except Exception as e:
            logger.error(f"Error checking missing data: {e}")

# ----- Polygon + Finnhub Logic -----

def date_to_unix_timestamp(date_str: str) -> int:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(time.mktime(dt.timetuple()))

async def fetch_finnhub_data_for_symbol(symbol: str, start_date: str, end_date: str):
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution=D&from={date_to_unix_timestamp(start_date)}&to={date_to_unix_timestamp(end_date)}&token={FINNHUB_API_KEY}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            data = response.json()
            if response.status_code == 200 and data.get("s") == "ok":
                for i in range(len(data["t"])):
                    result = {
                        "ticker": symbol,
                        "date": datetime.utcfromtimestamp(data["t"][i]).strftime("%Y-%m-%d"),
                        "open": data["o"][i],
                        "close": data["c"][i],
                        "high": data["h"][i],
                        "low": data["l"][i],
                        "volume": data["v"][i],
                        "trades": 0,
                    }
                    await save_to_db(result)
                    await publish_to_kafka(TOPIC, result)
            else:
                logger.warning(f"Invalid Finnhub data for {symbol} {start_date} - {end_date}")
        except Exception as e:
            logger.error(f"Finnhub error: {e}")

async def fetch_historical_data_for_symbol(symbol: str, start_date: str, end_date: str):
    url = f"{BASE_URL}/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}?apiKey={API_KEY}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
    except Exception as e:
        logger.error(f"Polygon request failed: {e}")
        return await fetch_finnhub_data_for_symbol(symbol, start_date, end_date)

    if response.status_code == 200 and data.get("resultsCount", 0) > 0:
        for stock_data in data["results"]:
            result = {
                "ticker": symbol,
                "date": datetime.utcfromtimestamp(stock_data["t"] / 1000).strftime("%Y-%m-%d"),
                "open": stock_data["o"],
                "close": stock_data["c"],
                "high": stock_data["h"],
                "low": stock_data["l"],
                "volume": stock_data["v"],
                "trades": stock_data["n"],
            }
            await save_to_db(result)
            await publish_to_kafka(TOPIC, result)
    else:
        logger.warning(f"Polygon returned no data for {symbol}, falling back to Finnhub")
        await fetch_finnhub_data_for_symbol(symbol, start_date, end_date)

# ----- Kafka Consumer -----

async def consume():
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id=GROUP_ID
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Attempt {attempt}: Starting Kafka Consumer...")
            await consumer.start()
            logger.info("✅ Kafka Consumer running")
            break
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            if attempt == MAX_RETRIES:
                return
            await asyncio.sleep(RETRY_DELAY)

    try:
        async for msg in consumer:
            logger.info(f"Received Kafka message: {msg.value.decode('utf-8')}")
    except Exception as e:
        logger.error(f"Kafka consumer runtime error: {e}")
    finally:
        await consumer.stop()
        logger.info("Kafka Consumer stopped")

async def safe_start_producer(producer, retries=10, delay=5):
    for attempt in range(1, retries + 1):
        try:
            await producer.start()
            logger.info("✅ Kafka producer connected.")
            return
        except Exception as e:
            logger.warning(f"❌ Kafka connection failed (attempt {attempt}/{retries}): {e}")
            if attempt == retries:
                logger.error("Producer failed after maximum retries.")
                raise
            await asyncio.sleep(delay)