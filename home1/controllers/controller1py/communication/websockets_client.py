import asyncio
import json
import websockets
from .communication_interface import receive_data
import threading
from typing import Dict

PORT = 8080
websocket_global = None


async def listen(websocket):
    try:
        async for message in websocket:
            receive_data(json.loads(message))
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed, attempting to reconnect...")
    finally:
        global websocket_global
        websocket_global = None


async def send_data_string_websockets(websocket, message):
    if websocket and websocket.open:
        await websocket.send(message)
    else:
        print("WebSocket is not open. Unable to send message.")


def send_data(json_data: Dict):
    global websocket_global
    websocket = websocket_global
    message = json.dumps(json_data)
    if websocket is None:
        print("WebSocket not connected. Unable to send data.")
        return
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(send_data_string_websockets(websocket, message))
    except RuntimeError:  # No running event loop
        asyncio.run(send_data_string_websockets(websocket, message))


async def start_websockets_client(set_server_started=(lambda: None)):
    uri = f"ws://localhost:{PORT}"
    global websocket_global
    try:
        async with websockets.connect(
                uri,
                ping_interval=None,  # Disable ping/pong mechanism
                ping_timeout=None
        ) as websocket:
            websocket_global = websocket
            set_server_started()
            print(f"Connected to WebSocket server at {uri}")
            await listen(websocket)
    except (websockets.exceptions.ConnectionClosed, OSError) as e:
        print(f"Connection failed: {e}.")


def start_websockets(set_server_started=(lambda: None)):
    asyncio.run(start_websockets_client(set_server_started))


if __name__ == "__main__":
    start_websockets()
