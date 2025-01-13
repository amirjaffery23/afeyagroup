import asyncio
import websockets
from collections import defaultdict

# Global dictionaries to manage connections and subscriptions
clients = {}  # Maps client IDs to WebSocket connections
subscriptions = defaultdict(set)  # Maps topics to sets of client IDs

async def register_client(websocket):
    """Register a new client and assign a unique ID."""
    # First message from the client should contain its unique ID
    client_id = await websocket.recv()
    clients[client_id] = websocket
    print(f"Client {client_id} connected.")
    return client_id

async def unregister_client(client_id):
    """Remove a client from the registry and all topic subscriptions."""
    if client_id in clients:
        del clients[client_id]
    for topic in subscriptions:
        subscriptions[topic].discard(client_id)
    print(f"Client {client_id} disconnected.")

async def handle_message(client_id, message):
    """Handle incoming messages from clients."""
    # Message structure: {"action": "subscribe|send|broadcast", "topic": "topic_name", "message": "content"}
    try:
        data = eval(message)  # Use JSON for real applications
        action = data.get("action")
        topic = data.get("topic")
        content = data.get("message")

        if action == "subscribe" and topic:
            subscriptions[topic].add(client_id)
            print(f"Client {client_id} subscribed to topic {topic}")

        elif action == "send" and topic and content:
            # Send a message to all clients subscribed to a topic
            for subscriber_id in subscriptions.get(topic, []):
                if subscriber_id in clients:
                    await clients[subscriber_id].send(f"[{topic}] {content}")

        elif action == "broadcast" and content:
            # Broadcast to all connected clients
            for target_id, target_ws in clients.items():
                if target_id != client_id:  # Optionally exclude sender
                    await target_ws.send(f"[Broadcast] {content}")

        else:
            print(f"Invalid action or missing fields from client {client_id}: {data}")

    except Exception as e:
        print(f"Error handling message from {client_id}: {e}")

async def handler(websocket, path):
    """Handle client connections and messages."""
    client_id = await register_client(websocket)
    try:
        async for message in websocket:
            await handle_message(client_id, message)
    except websockets.exceptions.ConnectionClosed:
        print(f"Connection closed for client {client_id}")
    finally:
        await unregister_client(client_id)

# Start the WebSocket server
start_server = websockets.serve(handler, "localhost", 8000)
print("WebSocket server running on ws://localhost:8000")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
