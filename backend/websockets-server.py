from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from kafka import KafkaConsumer
import asyncio
import json

app = FastAPI()

connections = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = websocket.client.host
    connections[client_id] = websocket
    print(f"Client {client_id} connected.")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from client {client_id}: {data}")
    except WebSocketDisconnect:
        del connections[client_id]
        print(f"Client {client_id} disconnected.")

async def kafka_listener():
    consumer = KafkaConsumer(
        "market-updates",
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    for message in consumer:
        update = message.value
        await broadcast_update(update)

async def broadcast_update(update):
    message = json.dumps(update)
    for client_id, websocket in list(connections.items()):
        try:
            await websocket.send_text(message)
        except Exception:
            del connections[client_id]

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(kafka_listener())
