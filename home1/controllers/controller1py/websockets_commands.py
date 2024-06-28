# import asyncio
# import websockets
#
#
# async def echo(websocket, path):
#     try:
#         print("WebSocket server started. Waiting for messages...")
#         async for message in websocket:
#             print(f"Received message: {message}")
#             # send message to robot
#
#     except websockets.ConnectionClosed:
#         print("Connection closed, client disconnected.")
#
#
# async def start_command_server():
#     async with websockets.serve(echo, "localhost", 8080):
#         print("Server is running on ws://localhost:8080")
#         await asyncio.Future()  # This keeps the server running indefinitely
#
#
# if __name__ == "__main__":
#     asyncio.run(start_command_server())
