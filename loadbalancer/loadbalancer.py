import random
import signal
import socket
import sys
from ast import literal_eval


HEADER = 4096
SERVER = '127.0.0.1'
PORT = 6969
ADDR = (SERVER, PORT)


class Loadbalancer:
    def __init__(self, address) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(address)
        self.sock.listen()
        print(f"Loadbalancer socket active. Listening on {address}")

        self.client_sock = None
        self.client_addr = None

        self.free_game_server_addresses = []
        self.waiting_game_server_addresses = []
        self.full_game_server_addresses = []

        self.reconnect_addresses = {}

        # Trap keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)
        
    def sighandler(self, signum, frame):
        print("\nShutting down the server")
        if self.client_sock:
            self.client_sock.close()
        self.sock.close()
        sys.exit(1)

    def register_game_server(self, msg):
        gs_addr = literal_eval(msg.split(":")[1])
        if gs_addr not in self.free_game_server_addresses:
            self.free_game_server_addresses.append(gs_addr)

    def register_chat_server(self, msg):
        print("Trying to register chat_server")
    
    def get_server(self, msg):

        if self.waiting_game_server_addresses:
            address = random.choice(self.waiting_game_server_addresses)
            self.waiting_game_server_addresses.remove(address)
            self.full_game_server_addresses.append(address)

            response = str(address)
            self.client_sock.send(response.encode())

        elif self.free_game_server_addresses:
            address = random.choice(self.free_game_server_addresses)
            self.free_game_server_addresses.remove(address)
            self.waiting_game_server_addresses.append(address)

            response = str(address)
            self.client_sock.send(response.encode())

        else:
            response = "N/A"
            self.client_sock.send(response.encode())

    def reconnect(self, msg):
        gameid = msg.split(":")[1]
        print("Reconnecting to game id:", gameid)

        # Connect to an already used address
        if gameid in self.reconnect_addresses:
            response = str(self.reconnect_addresses[gameid])
            self.client_sock.send(response.encode())
            print(f'Sent an already used reconnect address: {response}')

        # Connect to a free server
        else:
            address = random.choice(self.free_game_server_addresses)
            self.free_game_server_addresses.remove(address)
            self.reconnect_addresses[gameid] = address

            response = str(self.reconnect_addresses[gameid])
            self.client_sock.send(response.encode())
            print(f'Sent a fresh new reconnect address: {response}')

    def handle_client_data(self, msg):
        
        print(f'Message from {self.client_addr}: {msg}')

        if "Game server" in msg:
            self.register_game_server(msg)

        elif "Chat server" in msg:
            self.register_chat_server(msg)

        elif "send servers pls!" in msg:
            self.get_server(msg)

        elif "reconnect" in msg:
            self.reconnect(msg)

        else:
            print(f'Unknown message from client {self.client_addr} \nWith message {msg}')

    def serve(self):
        while True:
            self.client_sock = None
            try:
                self.client_sock, self.client_addr = self.sock.accept()
                msg = self.client_sock.recv(HEADER).decode()
                self.handle_client_data(msg)
            except Exception as e:
                print(f"Error handling client connection with error: {e}")
                if self.client_sock:
                    self.client_sock.close()
                self.sock.close()
                return
        

if __name__ == "__main__":
    lb = Loadbalancer(ADDR)
    lb.serve()