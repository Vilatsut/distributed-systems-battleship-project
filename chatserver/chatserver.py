import socket
import sys
import threading


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

print(f"Chat server is listening on {SERVER}:{PORT}")
send_to_load_balancer()
chat_server.listen()


def handle_client(conn, addr):
    print(f"Connection to chat server from: {conn}: {addr}.")
    
    while True:
        message = conn.recv(HEADER).decode(FORMAT)
        if message:
            print(f"Message received from {addr}: {message}")
            for player in connected_players:
                if player != conn:
                    print(player)
                    try:
                        player.send(message.encode(FORMAT))
                    except Exception as e:
                        print("Exception: ", e)
                #else:
                    #player.send("Successfully sent message".encode(FORMAT))

def start_server():
    chat_server.listen()
    print(f"Chat server is listening on {SERVER}:{PORT}")

    while True:
        conn, addr = chat_server.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        connected_players.append(conn)
        client_thread.start()

start_server()


