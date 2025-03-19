from fastapi import FastAPI, HTTPException
from aiokafka import AIOKafkaConsumer
import asyncio
import httpx
import os
import uvicorn # For running the FastAPI server
from dotenv import load_dotenv
import logging
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"

app = FastAPI()

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
            return result
        else:
            logger.warning(f"No data available for {ticker} on {date}")
            return {"message": "No data available for this date."}

    logger.error(f"Failed to fetch stock data for {ticker}: {response.text}")
    return {"error": "Failed to fetch stock data", "status_code": response.status_code}

async def consume():
    """ Kafka Consumer """
    consumer = AIOKafkaConsumer("stock-data", bootstrap_servers="kafka:9092", group_id="stock-group")
    await consumer.start()
    try:
        async for msg in consumer:
            logger.info(f"Received Kafka message: {msg.value}")
    finally:
        await consumer.stop()

async def main():
    """ Start both FastAPI and Kafka Consumer concurrently """
    kafka_task = asyncio.create_task(consume())  # ✅ Fix: Function now exists before calling
    config = uvicorn.Config("polygon_stocks_api:app", host="0.0.0.0", port=8080, reload=True)
    server = uvicorn.Server(config)
    
    api_task = asyncio.create_task(server.serve())  # ✅ Fix: Running FastAPI server

    await asyncio.gather(kafka_task, api_task)  # ✅ Fix: Both tasks now run concurrently

if __name__ == "__main__":
    logger.info("🚀 Polygon API microservice Started...")
    asyncio.run(main())  # ✅ Fix: Ensures both FastAPI & Kafka run together
   
