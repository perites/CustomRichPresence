import sys

import socket
import struct
import time

import logging

PORT = 13370
SERVER = "127.0.0.1"
SERVER_ADDR = (SERVER, PORT)

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] : %(message)s \/ [LOGGER:%(name)s] [FUNC:%(funcName)s] [FILE:%(filename)s]',
    datefmt='%H:%M:%S',
    filename="native_messages_proxy.log",
    filemode='w', level=logging.DEBUG, encoding='utf-8')


def wait_until_connect():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(SERVER_ADDR)
            logging.info("Connected to server")
            return client
        
        except Exception as exception:
            logging.error("Error while connecting to server, trying again in 5 seconds")
            client.close()

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            time.sleep(10)


def send_message_to_server(message, client):
    client.send(str(len(message)).encode("utf-8").ljust(64))
    client.send(message.encode("utf-8"))


def get_native_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        sys.exit(0)
    message_length = struct.unpack("@I", raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return message


def main():
    client = wait_until_connect()
    while True:
        try:
            message = get_native_message()
            logging.debug(f"Message received: {message}")
            try:
                send_message_to_server(message, client)
            except ConnectionResetError:
                client = wait_until_connect()
                logging.warning("Connection was reestablished")

                send_message_to_server(message, client)

            logging.debug(f"Message sent to server")

        except Exception as exception:
            logging.exception("Error while sending message to server, message not sent")


if __name__ == "__main__":
    logging.debug("Starting main")
    main()
