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
finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))

# Initialize Kafka producer
producer = AIOKafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

async def fetch_and_send_data():
    await producer.start()
    try:
        while True:
            # Fetch data from Finnhub for multiple indices
            indices = {
                "Dow Jones": "^DJI",
                "Nasdaq": "^IXIC",
                "S&P 500": "^GSPC",
                "Russell 2000": "^RUT"
            }
            for name, symbol in indices.items():
                try:
                    logger.debug(f"Fetching data for {name} ({symbol})")
                    data = finnhub_client.stock_candles(symbol, 'D', 1590988249, 1591852249)
                    if data:
                        logger.debug(f"Received data for {name} ({symbol}): {data}")
                        message = {
                            "index": name,
                            "symbol": symbol,
                            "data": data
                        }
                        # Send data to Kafka
                        await producer.send_and_wait("market-updates", message)
                        logger.debug(f"Sent data to Kafka for {name} ({symbol})")
                    else:
                        logger.warning(f"No data received for {name} ({symbol})")
                except Exception as e:
                    logger.error(f"Error fetching data for {name} ({symbol}): {e}")
            await asyncio.sleep(60)  # Fetch data every 60 seconds
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(fetch_and_send_data())