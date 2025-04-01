from fastapi import FastAPI, HTTPException
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio
import asyncpg  # For PostgreSQL connection
import httpx
import os
import uvicorn
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import time  # for Unix timestamp conversions

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

API_KEY = os.getenv("POLYGON_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")  # <-- Make sure this is set
BASE_URL = "https://api.polygon.io"

DB_URL = os.getenv("DATABASE_URL")  # PostgreSQL connection string
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")  # Kafka broker address
TOPIC = "new-stock-data"
GROUP_ID = "stock-group"
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds

db_pool = None  # Define db_pool globally
producer = None  # Kafka producer

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, producer
    try:
        logger.info("🚀 Connecting to PostgreSQL database...")
        db_pool = await asyncpg.create_pool(DB_URL)
        logger.info("✅ Database connection pool created successfully!")
        
        producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKER)
        await producer.start()
        logger.info("Kafka producer started")
        
        asyncio.create_task(fetch_and_store_historical_data())
        asyncio.create_task(schedule_daily_updates())
        asyncio.create_task(fetch_missing_data())
        
        yield
    finally:
        if db_pool:
            await db_pool.close()
            logger.info("🔌 Database connection pool closed.")
        if producer:
            await producer.stop()
            logger.info("Kafka producer stopped")

app = FastAPI(lifespan=lifespan)

@app.get("/test-db")
async def test_db():
    """Test database connection."""
    global db_pool
    if not db_pool:
        return {"error": "Database pool is not initialized"}
    
    try:
        async with db_pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
        return {"status": "DB Connected", "result": result}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def home():
    return {"message": "Polygon Stocks API is running"}

async def save_to_db(stock_data: dict):
    """Save stock data to PostgreSQL."""
    global db_pool
    if not db_pool:
        logger.error("Database pool is not initialized")
        return
    try:
        async with db_pool.acquire() as conn:
            query = """
                INSERT INTO historicalstockdata (ticker, date, open, close, high, low, volume, trades)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (ticker, date) DO NOTHING
            """
            await conn.execute(
                query,
                stock_data["ticker"],
                datetime.strptime(stock_data["date"], "%Y-%m-%d").date(),
                stock_data["open"],
                stock_data["close"],
                stock_data["high"],
                stock_data["low"],
                stock_data["volume"],
                stock_data["trades"],
            )
            logger.info(f"Inserted stock data into DB for {stock_data['ticker']} on {stock_data['date']}")
    except Exception as e:
        logger.error(f"Error saving to DB: {e}")

async def publish_to_kafka(topic: str, message: dict):
    """Publish a message to a Kafka topic."""
    global producer
    if not producer:
        logger.error("Kafka producer is not initialized")
        return
    try:
        await producer.send_and_wait(topic, value=str(message).encode("utf-8"))
        logger.info(f"Published message to Kafka topic '{topic}': {message}")
    except Exception as e:
        logger.error(f"Error publishing to Kafka: {e}")

async def fetch_stock_symbols():
    """Fetch stock symbols from the allstock table in stock_db."""
    global db_pool
    if not db_pool:
        logger.error("Database pool is not initialized")
        return []
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT stock_symbol FROM allstock")
        return [row["stock_symbol"] for row in rows]
    except Exception as e:
        logger.error(f"Error fetching stock symbols: {e}")
        return []

async def schedule_daily_updates():
    """Schedule updates every 5 minutes for debugging purposes."""
    while True:
        now = datetime.utcnow()
        next_run = now + timedelta(minutes=5)  # Schedule the next run 5 minutes from now
        sleep_duration = (next_run - now).total_seconds()
        logger.info(f"Next data pull scheduled at: {next_run}")
        await asyncio.sleep(sleep_duration)
        await update_daily_data()

async def update_daily_data():
    """Fetch and store the latest daily data for all stock symbols."""
    logger.info("Fetching and storing today's stock data...")
    stock_symbols = await fetch_stock_symbols()
    if not stock_symbols:
        logger.warning("No stock symbols found in the allstock table.")
        return

    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    for symbol in stock_symbols:
        logger.info(f"Fetching daily data for {symbol}")
        await fetch_historical_data_for_symbol(symbol, yesterday.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))

async def fetch_and_store_historical_data():
    """Fetch and store 2-year historical data for all stock symbols."""
    logger.info("Fetching and storing historical stock data...")
    stock_symbols = await fetch_stock_symbols()
    if not stock_symbols:
        logger.warning("No stock symbols found in the allstock table.")
        return

    today = datetime.utcnow().date()
    two_years_ago = today - timedelta(days=730)

    batch_size = 5  # Fetch data for 5 symbols at a time
    for i in range(0, len(stock_symbols), batch_size):
        batch = stock_symbols[i:i + batch_size]
        for symbol in batch:
            logger.info(f"Fetching historical data for {symbol}")
            await fetch_historical_data_for_symbol(symbol, two_years_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        await asyncio.sleep(60)  # Wait 60 seconds between batches to avoid rate limits

async def fetch_missing_data():
    """Fetch and store missing data for the previous day if not already stored."""
    logger.info("Checking for missing data...")
    stock_symbols = await fetch_stock_symbols()
    if not stock_symbols:
        logger.warning("No stock symbols found in the allstock table.")
        return

    yesterday = datetime.utcnow().date() - timedelta(days=1)

    for symbol in stock_symbols:
        logger.info(f"Checking for missing data for {symbol} on {yesterday}")
        try:
            async with db_pool.acquire() as conn:
                query = "SELECT COUNT(*) FROM historicalstockdata WHERE ticker = $1 AND date = $2"
                result = await conn.fetchval(query, symbol, yesterday)

                if result == 0:  # No data found for the previous day
                    logger.warning(f"No data found for {symbol} on {yesterday}. Fetching now...")
                    await fetch_historical_data_for_symbol(symbol, yesterday.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d"))
        except Exception as e:
            logger.error(f"Error checking for missing data for {symbol}: {e}")

# -----------------------------------------------
#   FINNHUB FALLBACK LOGIC
# -----------------------------------------------

def date_to_unix_timestamp(date_str: str) -> int:
    """Convert YYYY-MM-DD to a Unix timestamp (seconds)."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(time.mktime(dt.timetuple()))

async def fetch_finnhub_data_for_symbol(symbol: str, start_date: str, end_date: str):
    """
    Fetch daily historical data from Finnhub and store/publish, similar to Polygon logic.
    Docs: https://finnhub.io/docs/api/stock-candles
    """
    if not FINNHUB_API_KEY:
        logger.error("FINNHUB_API_KEY not set. Cannot use Finnhub fallback.")
        return
    
    start_ts = date_to_unix_timestamp(start_date)
    end_ts = date_to_unix_timestamp(end_date)

    url = (
        f"https://finnhub.io/api/v1/stock/candle?"
        f"symbol={symbol}&resolution=D&from={start_ts}&to={end_ts}&token={FINNHUB_API_KEY}"
    )
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                # Finnhub returns e.g. {"c": [...], "h": [...], "l": [...], "o": [...], "v": [...], "t": [...], "s":"ok"}
                if data.get("s") == "ok" and data.get("t"):
                    closes = data["c"]
                    highs = data["h"]
                    lows = data["l"]
                    opens = data["o"]
                    volumes = data["v"]
                    timestamps = data["t"]

                    for i in range(len(timestamps)):
                        date_str = datetime.utcfromtimestamp(timestamps[i]).strftime("%Y-%m-%d")
                        result = {
                            "ticker": symbol,
                            "date": date_str,
                            "open": opens[i],
                            "close": closes[i],
                            "high": highs[i],
                            "low": lows[i],
                            "volume": volumes[i],
                            "trades": 0,  # Finnhub doesn't provide trade count, so set 0 or omit
                        }
                        await save_to_db(result)
                        await publish_to_kafka("new-stock-data", result)
                else:
                    logger.warning(f"No or invalid Finnhub data for {symbol} between {start_date} and {end_date}")
            else:
                logger.error(f"Finnhub fallback failed for {symbol}. HTTP {response.status_code}: {response.text}")
        except httpx.HTTPError as http_err:
            logger.error(f"Finnhub request failed for {symbol}: {http_err}")

# -----------------------------------------------
#   PRIMARY DATA FETCH WITH FALLBACK
# -----------------------------------------------

async def fetch_historical_data_for_symbol(symbol: str, start_date: str, end_date: str):
    """
    Fetch historical data for a stock symbol from Polygon API.
    If Polygon fails or returns NOT_AUTHORIZED, fallback to Finnhub.
    """
    polygon_url = (
        f"{BASE_URL}/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}?apiKey={API_KEY}"
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(polygon_url)
    except httpx.HTTPError as e:
        logger.error(f"Polygon request failed for {symbol}: {e}")
        logger.info(f"Falling back to Finnhub for {symbol}")
        await fetch_finnhub_data_for_symbol(symbol, start_date, end_date)
        return

    if response.status_code == 200:
        data = response.json()
        # Check if the API returned "NOT_AUTHORIZED" in the JSON status
        if data.get("status") == "NOT_AUTHORIZED":
            logger.warning(f"Polygon NOT_AUTHORIZED for {symbol}. Falling back to Finnhub.")
            await fetch_finnhub_data_for_symbol(symbol, start_date, end_date)
            return
        
        results_count = data.get("resultsCount", 0)
        if results_count > 0 and "results" in data:
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
                # Save to PostgreSQL
                await save_to_db(result)
                # Publish Kafka message
                await publish_to_kafka("new-stock-data", result)
        else:
            logger.warning(f"No data available from Polygon for {symbol} between {start_date} and {end_date}")
    else:
        # If we have a non-200 status code or an error in body
        logger.error(f"Polygon error for {symbol}: {response.text}")
        # If the error text hints "NOT_AUTHORIZED" or anything else, fallback:
        if "NOT_AUTHORIZED" in response.text:
            logger.warning(f"Falling back to Finnhub for {symbol} due to NOT_AUTHORIZED.")
        else:
            logger.info(f"Falling back to Finnhub for {symbol} due to Polygon error.")
        await fetch_finnhub_data_for_symbol(symbol, start_date, end_date)


# -----------------------------------------------
#   KAFKA CONSUMER LOGIC (with retries)
# -----------------------------------------------
async def consume():
    """Kafka Consumer with retry logic and detailed logging."""
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id=GROUP_ID
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"🌀 Attempt {attempt}: Starting Kafka Consumer...")
            await consumer.start()
            logger.info("✅ Kafka Consumer connected and running.")
            break
        except Exception as e:
            logger.error(f"⚠️ Attempt {attempt}: Failed to start Kafka Consumer - {e}")
            if attempt == MAX_RETRIES:
                logger.critical("❌ Reached maximum retry attempts. Giving up.")
                return
            await asyncio.sleep(RETRY_DELAY)

    try:
        async for msg in consumer:
            logger.info(f"📥 Received Kafka message: {msg.value.decode('utf-8')}")
    except Exception as e:
        logger.error(f"🔥 Kafka Consumer runtime error: {e}")
    finally:
        await consumer.stop()
        logger.info("🛑 Kafka Consumer stopped.")


async def main():
    """Start FastAPI server and Kafka Consumer concurrently."""
    kafka_task = asyncio.create_task(consume())  # Start Kafka consumer
    config = uvicorn.Config("polygon_stocks_api:app", host="0.0.0.0", port=8080, reload=True)
    server = uvicorn.Server(config)

    api_task = asyncio.create_task(server.serve())  # Start FastAPI server

    await asyncio.gather(kafka_task, api_task)  # Run both tasks concurrently


if __name__ == "__main__":
    logger.info("🚀 Polygon API microservice Started...")
    asyncio.run(main())
