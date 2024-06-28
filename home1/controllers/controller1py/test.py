import threading
from communication.communication_interface import send_data, start_server
from configs_init import configs

if __name__ == '__main__':
    configs()

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    send_data("START")

    # wait for thread to finish
    server_thread.join()
