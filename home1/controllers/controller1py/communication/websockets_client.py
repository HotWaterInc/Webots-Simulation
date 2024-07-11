import asyncio
import json
import websockets
from .communication_interface import receive_data
import threading
from typing import Dict

PORT = 8080
websocket_global = None


async def listen(websocket):
    async for message in websocket:
        receive_data(json.loads(message))


async def send_data_websockets(websocket, message):
    await websocket.send(message)


def send_data_async(json_data: Dict):
    asyncio.create_task(send_data(json_data))


def send_data_sync(json_data: Dict):
    asyncio.run(send_data(json_data))


def send_data(json_data: Dict):
    global websocket_global
    websocket = websocket_global
    message = json.dumps(json_data)

    try:
        asyncio.create_task(send_data_websockets(websocket, message))
    except RuntimeError:
        asyncio.run(send_data_websockets(websocket, message))

    # if asyncio.get_running_loop() is None:
    #     asyncio.run(send_data_websockets(websocket, message))
    # else:
    #     asyncio.create_task(send_data_websockets(websocket, message))


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
