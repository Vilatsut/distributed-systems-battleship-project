import socket
import sys


HEADER = 1024
FORMAT = 'utf-8'
PORT = 6969
# load balancer port
PORT1 = 16432

SERVER = '127.0.0.1'

chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected_players = []

try:
    chat_server.bind((SERVER, PORT))
except OSError:
    print("No available ports for chat server.")
    sys.exit()


def send_to_load_balancer():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((SERVER, PORT1))
    message = f"Chat server started at {PORT}"
    server.send(message.encode())
    server.close()


print(f"Chat server is listening on {SERVER}")
send_to_load_balancer()
chat_server.listen()

while True:
    conn, addr = chat_server.accept()