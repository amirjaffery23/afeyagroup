import finnhub
from aiokafka import AIOKafkaProducer
import asyncio
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Finnhub client
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
if not FINNHUB_API_KEY:
    logger.error("❌ FINNHUB_API_KEY is missing! Set it in the environment.")
    exit(1)

finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC_NAME = "market-updates"


async def fetch_and_send_data():
    """Fetch stock data from Finnhub and send it to Kafka."""
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Ensure proper encoding
    )
    
    await producer.start()
    try:
        while True:
            indices = {
                "Apple": "AAPL",
                "Microsoft": "MSFT",
                "Google": "GOOGL",
                "Amazon": "AMZN",
                "Facebook": "FB",
                "Tesla": "TSLA",
                "NVIDIA": "NVDA",
                "AMD": "AMD",
            }
            
            for name, symbol in indices.items():
                try:
                    logger.debug(f"🔄 Fetching live data for {name} ({symbol})...")
                    
                    # Use `/quote` instead of `/stock/candle` to avoid 403 error
                    data = finnhub_client.quote(symbol)

                    if data and "c" in data:  # Ensure we received valid stock data
                        message = {
                            "index": name,
                            "symbol": symbol,
                            "price": data["c"],  # Current price
                            "change": data["d"],  # Price change
                            "percent_change": data["dp"],  # Percentage change
                            "high": data["h"],  # High price of the day
                            "low": data["l"],  # Low price of the day
                            "open": data["o"],  # Open price
                            "previous_close": data["pc"],  # Previous closing price
                            "timestamp": data["t"],  # Timestamp
                        }
                        
                        # Send data to Kafka
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
