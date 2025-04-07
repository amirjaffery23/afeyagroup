import asyncio
import json
import logging

import finnhub
from aiokafka import AIOKafkaProducer
import os
from core.config import FinnhubSettings

# Load settings
settings = FinnhubSettings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print(">>> DEBUG ENV", dict(os.environ), flush=True)

# Validate FINNHUB_API_KEY via settings
if not settings.FINNHUB_API_KEY:
    logger.critical("❌ FINNHUB_API_KEY is not set! Exiting...")
    exit(1)

# Initialize Finnhub client
finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)

# Kafka Configuration
TOPIC_NAME = "market-updates"

async def fetch_and_send_data():
    """Fetch stock data from Finnhub and send it to Kafka."""
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    await producer.start()
    logger.info("✅ Kafka Producer started")

    try:
        while True:
            indices = {
                "Apple": "AAPL",
                "Microsoft": "MSFT",
                "Google": "GOOGL",
                "Amazon": "AMZN",
                "Facebook": "META",
                "Tesla": "TSLA",
                "NVIDIA": "NVDA",
                "AMD": "AMD",
            }

            for name, symbol in indices.items():
                try:
                    logger.debug(f"🔄 Fetching live data for {name} ({symbol})...")
                    data = finnhub_client.quote(symbol)

                    if data and "c" in data:
                        message = {
                            "index": name,
                            "symbol": symbol,
                            "price": data["c"],
                            "change": data["d"],
                            "percent_change": data["dp"],
                            "high": data["h"],
                            "low": data["l"],
                            "open": data["o"],
                            "previous_close": data["pc"],
                            "timestamp": data["t"],
                        }
                        await producer.send_and_wait(TOPIC_NAME, message)
                        logger.info(f"✅ Sent data to Kafka for {name} ({symbol}): {message}")
                    else:
                        logger.warning(f"⚠️ No valid data received for {name} ({symbol})")

                except Exception as e:
                    logger.error(f"❌ Error fetching data for {name} ({symbol}): {e}")

            await asyncio.sleep(120)  # Fetch data every 2 minutes

    except asyncio.CancelledError:
        logger.info("🛑 Task cancelled. Shutting down Kafka producer...")

    finally:
        await producer.stop()
        logger.info("✅ Kafka producer stopped.")

if __name__ == "__main__":
    logger.info("🚀 Finnhub Producer Started...")
    asyncio.run(fetch_and_send_data())
