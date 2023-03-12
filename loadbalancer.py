import socket
import redis
import subprocess
import time
import os
import sys
from psutil import process_iter
from signal import SIGTERM  # or SIGKILL

HEADER = 4096
PORT = 16432
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

SERVER_PORTS = [5050, 5051]


for proc in process_iter():
    for conns in proc.connections(kind='inet'):
        if conns.laddr.port == 16432:
            proc.send_signal(SIGTERM)
        if conns.laddr.port == 5050:
            proc.send_signal(SIGTERM)
        if conns.laddr.port == 5051:
            proc.send_signal(SIGTERM)
        if conns.laddr.port == 5052:
            proc.send_signal(SIGTERM)


load_balancer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
load_balancer.bind(ADDR)
load_balancer.listen(1)

print("Load balancer active.")
print(f"Load balancer is listening on {SERVER}")

game_server_addresses = []

chat_online = False

# if no game servers, start 3 game servers
if not game_server_addresses:
    print("starting 3 game server instances")
    for port in SERVER_PORTS:
        try:
            subprocess.Popen('start /wait python game_server.py', shell=True)
            time.sleep(2)
        except Exception as e:
            print("Error: ", e)
        else:
            print("started on: ", port)



while True:
    try:
        client_socket, client_address = load_balancer.accept()
        data = client_socket.recv(1024)

    except:
        sys.exit()
    try:
        if "reconnect" in data.decode():
            # if the last 4 string letters are the gamecode
            # there needs to be a number in Redis() if each gameserver has a different db
            # -8:-4 should propably contain the port of the gameserver that crashed so loadbalancer can restart it
            # subprocess.call('start /wait python bb.py', shell=True) this is how you can start a new gameserver from loadbalancer
            # handle client and
            redis = redis.Redis()
            redis.mget(data.decode()[-4:])
            restart_port = data.decode()[-8:-4]
            pass
        else:
            if "Game server" in data.decode():
                print(f'Received from {client_address}: {data.decode()}')
                if data.decode()[-4:] not in game_server_addresses:
                    # print(data.decode()[-4:])
                    game_server_addresses.append(data.decode()[-4:])

            if "Chat server" in data.decode():
                print(f"Received from {client_address}: {data.decode()}")
                chat_online = True

            if "send servers pls!" in data.decode():
                print("Client connected!")

                # check which ports are actually game servers
                check_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                for game_server in game_server_addresses:
                    try:
                        print("Checking ports...", game_server)
                        check_socket.bind((SERVER, int(game_server)))
                    except Exception as e:
                        print(f"Game server {game_server} active.")

                    else:
                        print("error")
                        game_server_addresses.pop(game_server)

                # if no game servers, start 3 game servers
                if not game_server_addresses:
                    print("starting 3 game server instances")
                    for port in SERVER_PORTS:
                        try:
                            subprocess.Popen(
                                'start /wait python gameserver.py', shell=True)
                        except Exception as e:
                            print("Error: ", e)
                        else:
                            game_server_addresses.append(str(port))
                    time.sleep(5)

                # send the number of game servers online
                response = f"There are currently {len(game_server_addresses)} game servers active in addresses: \n "
                client_socket.send(response.encode())

                # send ports now
                ports = ""
                for i in game_server_addresses:
                    ports = ports + "," + i
                response = f"{ports}"
                print(response)
                client_socket.send(response.encode())
                if chat_online:
                    response = ""
                    response = "Chat Server is online."
                    client_socket.send(response.encode())

    except:
        print("Exceptionpy")

    client_socket.close()
