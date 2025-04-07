import asyncio
import logging
from aiokafka.errors import KafkaConnectionError

logger = logging.getLogger(__name__)

async def safe_start_producer(producer, retries: int = 5, delay: int = 5):
    for attempt in range(1, retries + 1):
        try:
            await producer.start()
            logger.info("✅ Kafka Producer connected successfully.")
            return
        except KafkaConnectionError as e:
            logger.warning(f"❌ Kafka Producer connection failed (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                await asyncio.sleep(delay)
            else:
                logger.error("Producer failed to connect after maximum retries.")
                raise


async def safe_start_consumer(consumer, retries: int = 5, delay: int = 5):
    for attempt in range(1, retries + 1):
        try:
            await consumer.start()
            logger.info("✅ Kafka Consumer connected successfully.")
            return
        except KafkaConnectionError as e:
            logger.warning(f"❌ Kafka Consumer connection failed (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                await asyncio.sleep(delay)
            else:
                logger.error("Consumer failed to connect after maximum retries.")
                raise
