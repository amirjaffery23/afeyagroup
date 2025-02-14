import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from aiokafka import AIOKafkaConsumer
from contextlib import asynccontextmanager
import asyncio
import json
import uuid

connections = {}

async def safe_json_deserializer(m):
    """Safely deserialize JSON messages, handling errors gracefully."""
    try:
        return json.loads(m.decode("utf-8"))
    except json.JSONDecodeError:
        print(f"⚠️ Warning: Received non-JSON message: {m}")
        return None  # Return None or a default dict instead of crashing

async def kafka_listener():
    # Ensure topic exists before starting consumer
    admin = KafkaAdminClient(bootstrap_servers="kafka:9092")
    try:
        if "market-updates" not in admin.list_topics():
            admin.create_topics([NewTopic("market-updates", 1, 1)])
    finally:
        admin.close()
    """Kafka consumer using aiokafka to allow async processing."""
    consumer = AIOKafkaConsumer(
        "market-updates",
        bootstrap_servers="kafka:9092",
        allow_auto_create_topics=True,  # 👈 Add this
        value_deserializer=safe_json_deserializer
    )
    await consumer.start()
    
    try:
        async for message in consumer:
            if message.value is not None:
                await broadcast_update(message.value)
    except asyncio.CancelledError:
        print("Kafka listener task cancelled.")
    finally:
        await consumer.stop()
        print("Kafka listener stopped.")

async def broadcast_update(update):
    """Send updates to all connected WebSocket clients."""
    message = json.dumps(update)
    disconnected_clients = []

    for client_id, websocket in connections.items():
        try:
            await websocket.send_text(message)
        except Exception:
            disconnected_clients.append(client_id)

    # Remove disconnected clients after sending messages
    for client_id in disconnected_clients:
        del connections[client_id]
        print(f"Removed disconnected client: {client_id}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure WebSocket starts immediately, and Kafka retries connection separately."""
    print("🚀 WebSocket Server Starting...")
    kafka_task = asyncio.create_task(kafka_listener())  # Start Kafka in the background
    yield
    print("🛑 Stopping Kafka listener...")
    kafka_task.cancel()
    try:
        await kafka_task
    except asyncio.CancelledError:
        print("Kafka listener task cancelled.")

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection handler."""
    await websocket.accept()
    client_id = str(uuid.uuid4())  # Unique ID for each connection
    connections[client_id] = websocket
    print(f"Client {client_id} connected.")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from client {client_id}: {data}")
    except WebSocketDisconnect:
        del connections[client_id]
        print(f"Client {client_id} disconnected.")

if __name__ == "__main__":
    print("🔥 Starting WebSocket Server on 0.0.0.0:8001...")
    uvicorn.run("websockets_server:app", host="0.0.0.0", port=8001)
