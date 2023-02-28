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
    return


def start_game():
    winner = 0
    turn = 0
    while winner == 0:
        # decide whose turn it is
        if (turn % 2 == 0):
            print("player 1 turn")
            player_input(1)
        else:
            player_input(2)


def start_server():
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


print("Starting the server.")
start_server()
