import socket
import redis
import subprocess
import time
import os

HEADER = 4096
PORT = 16432
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

SERVER_PORTS = [5050, 5051, 5052]


load_balancer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
load_balancer.bind(ADDR)
load_balancer.listen(1)

print("Load balancer active.")
print(f"Load balancer is listening on {SERVER}")

game_server_addresses = []

chat_online = False

# if no game servers, start 3 game servers
subprocess.call('start /wait python game_server.py', shell=True)
input()
print("ASD")

if not game_server_addresses:
    print("starting 3 game server instances")
    for port in SERVER_PORTS:
        try:
            subprocess.call('start /wait python ./gameserver/game_server.py', shell=True)
        except Exception as e:
            print("Error: ", e)
        else:
            print("started on: ", port)
            game_server_addresses.append(str(port))
    time.sleep(10)

input()
while True:
    client_socket, client_address = load_balancer.accept()
    data = client_socket.recv(1024)
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
                check_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                for game_server in game_server_addresses:
                    try:
                        print("Checking ports...", game_server)
                        check_socket.bind((SERVER, int(game_server)))
                    except Exception as e:
                        print("Error: ", e)

                    else:
                        print("error")
                        game_server_addresses.pop(game_server)

                # if no game servers, start 3 game servers
                if not game_server_addresses:
                    print("starting 3 game server instances")
                    for port in SERVER_PORTS:
                        try:
                            subprocess.call('start /wait python gameserver.py', shell=True)
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

    except Exception as e:
        print("Exception: ", e)



    client_socket.close()
