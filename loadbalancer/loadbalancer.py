import socket
import redis

HEADER = 4096
PORT = 16432
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


load_balancer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
load_balancer.bind(ADDR)
load_balancer.listen(1)

print("Load balancer active.")
print(f"Load balancer is listening on {SERVER}")

game_server_addresses = []

chat_online = False

while True:
    client_socket, client_address = load_balancer.accept()
    data = client_socket.recv(1024)
    if "reconnect" in data.decode():
        # if the last 4 string letters are the gamecode
        # there needs to be a number in Redis() if each gameserver has a different db 
        redis = redis.Redis()
        redis.mget(data.decode()[-4:])
        pass
    else:
        if "Game server" in data.decode():
            print(f'Received from {client_address}: {data.decode()}')
            game_server_addresses.append(data.decode()[-4:])
        if "Chat server" in data.decode():
            print(f"Chat server is online.")
            chat_online = True
        else:
            print("Client connected!")
            response = f"There are currently {len(game_server_addresses)} game servers active in addresses: \n {''.join(str(game_server_addresses))}"
            if chat_online:
                response = response + ". and the Chat Server is online."
            client_socket.send(response.encode())
    client_socket.close()
