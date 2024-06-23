import socket
import threading
import json

from .logger import logger


class Server:
    def __init__(self, port, server_ip, data_queue):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((server_ip, port))
        self.data_queue = data_queue

    @staticmethod
    def handle_client(conn, addr, data_queue):
        while True:
            try:
                message_length = conn.recv(64).decode('utf-8')
                if not message_length:
                    continue
                message_length = int(message_length)
                message = conn.recv(message_length).decode('utf-8')

                json_data = json.loads(message)
                data_queue.put(json_data)
                logger.debug(f"Got new data: {json_data} from {addr}")

            except Exception as exception:
                logger.exception(f"Error while receiving data from '{addr}'")

    def _start_handling_clients(self):
        self.server.listen()
        while True:
            try:
                conn, addr = self.server.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr, self.data_queue), daemon=True).start()
                logger.info(f"New connection established '{addr}'. New thread started to handle")

            except Exception as exception:
                logger.exception(f"Error while accepting connection")

    def start_handling_clients(self, daemon):
        threading.Thread(target=self._start_handling_clients, daemon=daemon).start()
        logger.info(f"Server started")
