import socket
import threading
import pickle
import sys

HEADER = 4096
# load balancer port
PORT1 = 16432
# game server ports
PORT2 = 5050
PORT3 = 5051
PORT4 = 5052
SERVER = '127.0.0.1'
# ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

player_connections = []
player_addresses = []
player_boards = []


def handle_client(conn, addr, num):
    """
        waits for two players to connect
        and submit their boards
    """
    print(f"{addr} connected.")

    # add the player details to lists
    player_connections.append(conn)
    player_addresses.append(addr)

    # receive the player boards
    msg = conn.recv(HEADER)
    board = pickle.loads(msg)
    player_boards.append(board)

    print(f"User board was {board}")
    conn.send(f"Welcome you are player {num}.".encode(FORMAT))

    if (num == 2):
        start_game()
    conn.close()


def player_input(player):
    # to be implemented
    # this is supposed to take player inputs i.e. which tile they want to attack
    return "Move accepted"


def start_game():
    winner = 0
    turn = 0
    while winner == 0:
        # decide whose turn it is
        if (turn % 2 == 0):
            print("player 1 turn")
            p1 = player_input(1)
        else:
            p2 = player_input(2)
        if p1 or p2 == "Move accepted":
            turn = turn + 1


def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER, port))
    server.listen()
    print(f"Server is listening on {SERVER}")
    while True:
        if (threading.active_count() - 1 <= 2):
            for i in range(2):
                conn, addr = server.accept()
                thread = threading.Thread(
                    target=handle_client, args=(conn, addr, i+1))
                thread.start()
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


def send_to_load_balancer(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((SERVER, PORT1))
    message = f"Game server started at {port}"
    server.send(message.encode())
    server.close()


# this is for checking for available PORT to connect game server to
check_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
free_port = ""
try:
    check_socket.bind((SERVER, PORT2))
except OSError:
    try:
        check_socket.bind((SERVER, PORT3))
    except OSError:
        try:
            check_socket.bind((SERVER, PORT4))
        except OSError:
            print(
                "No available PORTs, maximum server number already exceeded. Press anything to exit.")
            input()
            sys.exit()
        else:
            print(f"Connected to {PORT4}")
            free_port = PORT4
    else:
        print(f"Connected to {PORT3}")
        free_port = PORT3
else:
    print(f"Connected to {PORT2}")
    free_port = PORT2

check_socket.close()

print("Sending information to load balancer.")
send_to_load_balancer(free_port)
print("Starting the server.")
start_server(free_port)




def asd():
    return 0
