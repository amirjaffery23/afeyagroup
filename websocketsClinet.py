import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8080"  # Replace with your server's URI
    try:
        async with websockets.connect(uri, open_timeout=10) as websocket:
            print("Connected to WebSocket server")
            # Add your communication logic here
    except Exception as e:
        print(f"Connection failed: {e}")

asyncio.run(test_websocket())

