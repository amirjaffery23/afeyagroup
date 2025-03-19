from fastapi import FastAPI, HTTPException
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import asyncio
import asyncpg  # For PostgreSQL connection
import httpx
import os
import uvicorn
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"
DB_URL = os.getenv("DATABASE_URL")  # PostgreSQL connection string
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")  # Kafka broker address

app = FastAPI()

# Initialize Kafka producer
producer = None

@app.on_event("startup")
async def startup_event():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKER)
    await producer.start()
    logger.info("Kafka producer started")

@app.on_event("shutdown")
async def shutdown_event():
    global producer
    if producer:
        await producer.stop()
        logger.info("Kafka producer stopped")

@app.get("/")
async def home():
    return {"message": "Polygon Stocks API is running"}

@app.get("/stock/{ticker}/historical")
async def get_stock_data(ticker: str, date: str):
    logger.info(f"Fetching historical data for {ticker} on {date}")
    
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{date}/{date}?apiKey={API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get("resultsCount", 0) > 0:
            stock_data = data["results"][0]
            result = {
                "ticker": ticker,
                "date": date,
                "open": stock_data["o"],
                "close": stock_data["c"],
                "high": stock_data["h"],
                "low": stock_data["l"],
                "volume": stock_data["v"],
                "trades": stock_data["n"],
            }
            logger.info(f"Stock Data: {result}")

            # Save to PostgreSQL
            await save_to_db(result)

            # Publish Kafka message
            await publish_to_kafka("new-stock-data", result)

            return result
        else:
            logger.warning(f"No data available for {ticker} on {date}")
            return {"message": "No data available for this date."}

    logger.error(f"Failed to fetch stock data for {ticker}: {response.text}")
    return {"error": "Failed to fetch stock data", "status_code": response.status_code}

async def save_to_db(stock_data: dict):
    """Save stock data to PostgreSQL."""
    try:
        conn = await asyncpg.connect(DB_URL)
        query = """
        INSERT INTO stock_data (ticker, date, open, close, high, low, volume, trades)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (ticker, date) DO NOTHING
        """
        await conn.execute(
            query,
            stock_data["ticker"],
            stock_data["date"],
            stock_data["open"],
            stock_data["close"],
            stock_data["high"],
            stock_data["low"],
            stock_data["volume"],
            stock_data["trades"],
        )
        logger.info(f"Inserted stock data into DB for {stock_data['ticker']} on {stock_data['date']}")
        await conn.close()
    except Exception as e:
        logger.error(f"Error saving to DB: {e}")

async def publish_to_kafka(topic: str, message: dict):
    """Publish a message to a Kafka topic."""
    try:
        global producer
        if producer:
            await producer.send_and_wait(topic, value=str(message).encode("utf-8"))
            logger.info(f"Published message to Kafka topic '{topic}': {message}")
    except Exception as e:
        logger.error(f"Error publishing to Kafka: {e}")

async def consume():
    """Kafka Consumer."""
    consumer = AIOKafkaConsumer("stock-data", bootstrap_servers=KAFKA_BROKER, group_id="stock-group")
    await consumer.start()
    try:
        async for msg in consumer:
            logger.info(f"Received Kafka message: {msg.value}")
    finally:
        await consumer.stop()

async def main():
    """Start both FastAPI and Kafka Consumer concurrently."""
    kafka_task = asyncio.create_task(consume())
    config = uvicorn.Config("polygon_stocks_api:app", host="0.0.0.0", port=8080, reload=True)
    server = uvicorn.Server(config)
    
    api_task = asyncio.create_task(server.serve())

    await asyncio.gather(kafka_task, api_task)

if __name__ == "__main__":
    logger.info("🚀 Polygon API microservice Started...")
    asyncio.run(main())

