import socket
import threading
import pickle
import sys
import redis

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
RESTART_GAMEID = None

player_connections = []
player_addresses = []
player_boards = []

redis = redis.Redis()


def player_shoot(player):

    msg = f'SHOOT player {player}'.encode(FORMAT)
    print("sending player_shoot:", msg)
    player_connections[player-1].send(msg)

    response = player_connections[player-1].recv(HEADER)
    shot = pickle.loads(response)
    # TODO Make sure shot is valid tuple (int, int) inside boundaries 0-BOARD_SIZE and not hit yet
    return shot


def player_shoot_again(player):

    msg = f'HIT player {player}'.encode(FORMAT)
    print("sending player_shoot:", msg)
    player_connections[player-1].send(msg)

    response = player_connections[player-1].recv(HEADER)
    shot = pickle.loads(response)
    # TODO Make sure shot is valid tuple (int, int) inside boundaries 0-BOARD_SIZE and not hit yet
    return shot


def act_shot(player, shot):
    hit = False
    opposite_board = player_boards[player % 2]
    if opposite_board[shot[0]][shot[1]] == "X":
        print("Player hit something")
        hit = True
    player_boards[player % 2][shot[0]][shot[1]] = "O"
    return hit


def is_finished(player):
    opposite_board = player_boards[player % 2]
    return not any('X' in sublist for sublist in opposite_board)


def player_win(player):

    msg = f'WIN player {player}?'.encode(FORMAT)
    print("sending player_win:", msg)
    player_connections[player-1].send(msg)

    msg = f'LOSE player {player%2+1}?'.encode(FORMAT)
    print("sending player_lose:", msg)
    player_connections[player % 2].send(msg)


def player_miss(player):
    msg = f'MISS player {player - 1}?'.encode(FORMAT)
    print("sending player_miss:", msg)
    player_connections[player - 1].send(msg)


def print_boards(gameid=None):
    if gameid:
        redis.mset({gameid: "$" + str(player_boards)})
        print("this is what boards look like: ", player_boards)
        print("this is what is being sent: ", str(player_boards))
    msg = f'PRINT {player_boards}?'.encode(FORMAT)
    for conn in player_connections:
        print("sending print_boards:", msg)
        conn.send(msg)

def generate_gameId():
    """
        Generates gameid and makes sure there isn't one in the database currently
    """
    try:
        gameids = redis.keys('*')
        gameid = 0
        # this could be implemented better later for more unique game ids
        for i in range(10, 99):
            if i not in gameids:
                gameid = i
        return gameid
    # if redis not active
    except:
        print("You havent started Redis!")
        return None


def start_game(gameid=None):
    print("Game has been started finally...")
    winner = 0
    turn = 0
    while winner == 0:
        shot = None
        player = turn % 2+1
        shot = player_shoot(player)
        hit = act_shot(player, shot)
        # if gameid then print boards updates redis database
        print("came to check gameid print boards")
        if gameid:
            print_boards(gameid)
        else:
            print_boards()
        if is_finished(player):
            print(f"Player {player} won!!!")
            player_win(player)
            winner = player
            for conn in player_connections:
                # uncomment this so that the game board gets deleted if game ends
                # redis.delete(gameid)
                conn.close()
            return

        if hit:
            while hit:
                shot = player_shoot_again(player)
                hit = act_shot(player, shot)
                # if gameid then print boards updates redis database
                if gameid:
                    print_boards(gameid)
                else:
                    print_boards()
                if is_finished(player):
                    print(f"Player {player} won!!!")
                    player_win(player)
                    winner = player
                    for conn in player_connections:
                        # uncomment this so that the game board gets deleted if game ends
                        # redis.delete(gameid)
                        conn.close()
                    return

                print(
                    f"Player hit something! Gets to shoot again. hit was {hit}")
        else:
            print("Player missed")
            player_miss(player)

        turn = turn + 1



def handle_client(conn, addr, num, port, restart=None):
    """
        waits for two players to connect
        and submit their boards
    """
    print(f"{addr} connected.")

    # add the player details to lists
    player_connections.append(conn)
    player_addresses.append(addr)

    if not restart:
        # receive the player boards
        msg = conn.recv(HEADER)
        board = pickle.loads(msg)
        player_boards.append(board)

        # generate a new gameid to the game
        gameid = generate_gameId()

        print(f"User board was {board}")
        conn.send(
            f"WAIT Welcome you are player {num} your game id is {gameid}".encode(FORMAT))

        if (num == 2):
            print("gameid: ", gameid)
            # if gameid then store the boards in redis memory under gameid key
            if gameid:
                redis.mset({gameid: "$" + str(player_boards) + str(port)})
                print("these are the boards in redis:", redis.mget(gameid))
                start_game(gameid)
            # else startgame without gameid
            else:
                start_game()
    else:
        boards = redis.mget(RESTART_GAMEID)
        print(boards)
        conn.send(
            f"WAIT Welcome you are player {num} your game id is {RESTART_GAMEID}".encode(FORMAT))
        print("6969restarting game from ", RESTART_GAMEID)
        if ( num == 2 ):
            start_game(RESTART_GAMEID)
    # conn.close()


def start_server(port):
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((SERVER, port))
        server.listen()
    except Exception as e:
        print("Error: ", e)
    print("Sending information to load balancer.")
    send_to_load_balancer(free_port)
    print(f"Server is listening on {SERVER}")
    while True:
        if (int(threading.active_count() - 1) <= 2):
            for i in range(2):
                conn, addr = server.accept()
                thread = threading.Thread(
                    target=handle_client, args=(conn, addr, i+1, port, RESTART_GAMEID))
                thread.start()
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


def send_to_load_balancer(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((SERVER, PORT1))
    message = f"Game server started at {port}"
    server.send(message.encode())
    server.close()


check_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# checking if game is restarted (the server is called with port)
if len(sys.argv) > 1:
    try:
        check_socket.bind((SERVER, int(sys.argv[1])))
    except OSError as e:
        print("Error starting game server, contact support: ", e)
    else:
        free_port = int(sys.argv[1])
        RESTART_GAMEID = int(sys.argv[2])
        print("port now:", free_port)
        print("RESTART_GAMEID: ", RESTART_GAMEID)



else:
    # this is for checking for available PORT to connect game server to
    free_port = ""
    try:
        check_socket.bind((SERVER, PORT2))
    except OSError:
        try:
            check_socket.bind((SERVER, PORT3))
        except OSError:
            print(
                "No available PORTs, maximum server number already exceeded. Press anything to exit.")
            """
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
            """
        else:
            print(f"Connected to {PORT3}")
            free_port = PORT3
    else:
        print(f"Connected to {PORT2}")
        free_port = PORT2

check_socket.close()

print("Starting the server.")
start_server(free_port)
