from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Set
from uuid import uuid4
import json

app = FastAPI()
       
# Allow CORS for development purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dictionaries to manage connections and subscriptions
connections: Dict[str, WebSocket] = {}
subscriptions: Dict[str, Set[str]] = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(uuid4())
    connections[client_id] = websocket
    print(f"Client {client_id} connected.")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await handle_message(client_id, message)
    except WebSocketDisconnect:
        await unregister_client(client_id)
    except Exception as e:
        print(f"Error: {e}")
        await unregister_client(client_id)

@app.websocket("/realtime-updates")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Message received: {data}")
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()
        
async def unregister_client(client_id: str):
    """Remove a client from the registry and all topic subscriptions."""
    if client_id in connections:
        del connections[client_id]
    for topic, subscribers in subscriptions.items():
        subscribers.discard(client_id)
    print(f"Client {client_id} disconnected.")

async def handle_message(client_id: str, message: Dict):
    """Handle incoming messages from clients."""
    action = message.get("action")
    topics: List[str] = message.get("topics", [])
    content = message.get("message")

    if action == "subscribe":
        for topic in topics:
            if topic not in subscriptions:
                subscriptions[topic] = set()
            subscriptions[topic].add(client_id)
            print(f"Client {client_id} subscribed to topic {topic}")

    elif action == "send":
        for topic in topics:
            await broadcast_update(topic, content)

async def broadcast_update(topic: str, content: str):
    """Broadcast updates to all clients subscribed to a topic."""
    if topic in subscriptions:
        message = json.dumps({"topic": topic, "content": content})
        for client_id in list(subscriptions[topic]):
            if client_id in connections:
                websocket = connections[client_id]
                try:
                    await websocket.send_text(message)
                    print(f"Sent update to client {client_id} for topic {topic}")
                except Exception as e:
                    print(f"Error sending to client {client_id}: {e}")
                    await unregister_client(client_id)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
