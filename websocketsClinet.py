import asyncio
import websockets

async def client():
    uri = "ws://localhost:8000"
    async with websockets.connect(uri) as websocket:
        # Send client ID
        await websocket.send("microservice_1")

        # Subscribe to a topic
        await websocket.send('{"action": "subscribe", "topic": "news"}')

        # Send a message to the topic
        await websocket.send('{"action": "send", "topic": "news", "message": "Hello, subscribers!"}')

        # Receive messages
        while True:
            response = await websocket.recv()
            print(f"Received: {response}")

asyncio.run(client())
