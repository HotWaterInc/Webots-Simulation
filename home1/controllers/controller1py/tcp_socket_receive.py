import asyncio
import threading
import json

host = 'localhost'
port = 8080


def decode_data(data: bytes):
    return data.decode()


async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connected by {addr}")
    while True:
        length_prefix = await reader.readexactly(4)
        if not length_prefix:
            break
        data_length = int.from_bytes(length_prefix, byteorder='big')
        data = await reader.readexactly(data_length)
        decoded_data = decode_data(data)
        print(f"Data received: {decoded_data}")
        if decoded_data == "END":
            print("Received 'END' signal. Closing connection.")
            writer.close()
            await writer.wait_closed()
            break
        else:
            print("Data received: ", decoded_data)
            json_data = json.loads(decoded_data)
            print(json_data["x"], json_data["y"])
            x, y = json_data["x"], json_data["y"]
            set_coords(x, y)


async def start_command_server():
    server = await asyncio.start_server(handle_client, host, port)
    print(f"Server listening on {host}:{port}")
    async with server:
        await server.serve_forever()


def run_server_in_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_command_server())
    loop.run_forever()


set_coords = None


def set_callback(coords):
    global set_coords
    set_coords = coords


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server_in_thread, daemon=True)
    server_thread.start()
    # Your main thread can perform other tasks concurrently here
    server_thread.join()  # Optional: wait for the server thread to finish if ever
