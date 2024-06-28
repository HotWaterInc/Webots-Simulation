import asyncio
import websockets
from .communication_interface import receive_data

PORT = 8080
websocket_global = None


async def listen(websocket):
    async for message in websocket:
        receive_data(message)


async def send_data_websockets(websocket, message):
    await websocket.send(message)


def send_data(message):
    global websocket_global
    websocket = websocket_global
    asyncio.run(send_data_websockets(websocket, message))


async def start_websockets_client(set_server_started=(lambda: None)):
    uri = f"ws://localhost:{PORT}"
    global websocket_global
    async with websockets.connect(uri) as websocket:
        websocket_global = websocket
        set_server_started()
        await listen(websocket)


def start_websockets(set_server_started=(lambda: None)):
    asyncio.run(start_websockets_client(set_server_started))


if __name__ == "__main__":
    start_websockets()