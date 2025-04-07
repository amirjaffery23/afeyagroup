import asyncio
import websockets

async def echo(websocket, path):
    while True:
        await websocket.send('{"symbol": "AAPL", "points": 100, "growthRate": 5}')
        await asyncio.sleep(1)

start_server = websockets.serve(echo, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

