import socket
import threading
import pickle

HEADER = 4096
PORT = 5050
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(conn, addr):
    print(f"{addr} connected.")

    connected = True
    while connected:
        msg = conn.recv(HEADER)
        message = pickle.loads(msg)
        print(type(message))
        print(f"User board was {message}")
        conn.send(f"Server received board.".encode(FORMAT))

    conn.close()

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        if(threading.active_count() - 1 <= 2):
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("Starting the serevr.")
start()
