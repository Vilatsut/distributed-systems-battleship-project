import socket
import threading
import sys
import signal
from ast import literal_eval
import time
import redis
import pickle

HEADER = 4096

LB_SERVER = '127.0.0.1'
LB_PORT = 6969
LB_ADDR = (LB_SERVER, LB_PORT)

GS_SERVER = '127.0.0.1'
GS_PORT = 50557
GS_ADDR = (GS_SERVER, GS_PORT)

PORT_RANGE_START    = 50555
PORT_RANGE_END      = 50560

redis = redis.Redis()


def generate_gameId():
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
    

class Gameserver:
    def __init__(self) -> None:
        self.address = None
        self.player_connections = []
        self.player_addresses = []
        self.player_boards = []
        self.sock = None

        self.gameid = None
        self.status = None

        self.server = None
        self.port = None
        self.address = None

        # Trap keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)
    def sighandler(self, signum, frame):
        print("\nShutting down the gameserver")
        if self.sock:
            self.sock.close()
        for conn in self.player_connections:
            conn.close()
        sys.exit(1)

    def handle_client(self, conn, addr, num):
        print(f"{addr} connected.")

        # add the player details to lists
        self.player_connections.append(conn)
        self.player_addresses.append(addr)


        client_status = conn.recv(HEADER).decode()
        print(f'Client status when connecting is : {client_status}')

        if self.status == "RECONNECT_STARTED":
            conn.send(str(self.player_boards[1]).encode())
            time.sleep(0.5)
            for conn in self.player_connections:
                message = f"Game is starting! Your game id is: {self.gameid}"
                conn.send(message.encode())
            self.start_game()

        if "reconnect" in client_status:
            self.status = "RECONNECT_STARTED"
            self.gameid = client_status.split(":")[1]
            data = redis.mget(self.gameid)
            print(f"Reconnecting data received by gameserver: {data[0].decode()}")
            self.player_boards = literal_eval(data[0].decode())
            conn.send(str(self.player_boards[0]).encode())
        else:
            print(f"Receiving board from client {num}")
            player_board_str = conn.recv(HEADER).decode()
            player_board = literal_eval(player_board_str)
            self.player_boards.append(player_board)

            print(f"User board was {player_board}")

            conn.send(f"START Welcome you are player {num}".encode())

            if num == 2:
                # generate a new gameid to the game
                self.gameid = generate_gameId()
                redis.mset({self.gameid:f"[{str(self.player_boards[0])}],[{str(self.player_boards[1])}]"})

                for conn in self.player_connections:
                    message = f"Game is starting! Your game id is: {self.gameid}"
                    conn.send(message.encode())
                self.start_game()



    def player_shoot(self, player):

        msg = f'SHOOT player {player}'.encode()
        print("sending player_shoot:", msg)
        try:
            self.player_connections[player-1].send(msg)
            response = self.player_connections[player-1].recv(HEADER)
            shot = pickle.loads(response)
        except:
            print("Client sent an empty shot")
            sys.exit()

        return shot


    def player_shoot_again(self, player):

        msg = f'HIT player {player}'.encode()
        print("sending player_shoot:", msg)
        self.player_connections[player-1].send(msg)

        response = self.player_connections[player-1].recv(HEADER)
        shot = pickle.loads(response)
        # TODO Make sure shot is valid tuple (int, int) inside boundaries 0-BOARD_SIZE and not hit yet
        return shot


    def act_shot(self, player, shot):
        hit = False
        opposite_board = self.player_boards[player % 2]
        if opposite_board[shot[0]][shot[1]] == "X":
            print("Player hit something")
            hit = True
        self.player_boards[player % 2][shot[0]][shot[1]] = "O"
        return hit


    def is_finished(self, player):
        opposite_board = self.player_boards[player % 2]
        return not any('X' in sublist for sublist in opposite_board)


    def player_win(self, player):

        msg = f'WIN player {player}?'.encode()
        print("sending player_win:", msg)
        self.player_connections[player-1].send(msg)

        msg = f'LOSE player {player%2+1}?'.encode()
        print("sending player_lose:", msg)
        self.player_connections[player % 2].send(msg)


    def player_miss(self, player):
        msg = f'MISS player {player - 1}?'.encode()
        print("sending player_miss:", msg)
        self.player_connections[player - 1].send(msg)


    def print_boards(self):
        redis.mset({self.gameid:f"[{str(self.player_boards[0])}],[{str(self.player_boards[1])}]"})
        msg = f'PRINT {self.player_boards}?'.encode()
        for conn in self.player_connections:
            print("sending print_boards:", msg)
            conn.send(msg)



    def start_game(self):
        print("Game has been started finally...")
        winner = 0
        turn = 0
        while winner == 0:
            shot = None
            player = turn % 2+1
            shot = self.player_shoot(player)
            hit = self.act_shot(player, shot)
            self.print_boards()
            if self.is_finished(player):
                print(f"Player {player} won!!!")
                self.player_win(player)
                winner = player
                for conn in self.player_connections:
                    # uncomment this so that the game board gets deleted if game ends
                    redis.delete(self.gameid)
                    conn.close()
                return

            if hit:
                while hit:
                    shot = self.player_shoot_again(player)
                    hit = self.act_shot(player, shot)
                    self.print_boards()
                    if self.is_finished(player):
                        print(f"Player {player} won!!!")
                        self.player_win(player)
                        winner = player
                        for conn in self.player_connections:
                            # uncomment this so that the game board gets deleted if game ends
                            # redis.delete(gameid)
                            conn.close()
                        return

                    print(
                        f"Player hit something! Gets to shoot again. hit was {hit}")
            else:
                print("Player missed")
                self.player_miss(player)

            turn = turn + 1

    def register_to_load_balancer(self, address):
        lb = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lb.connect(LB_ADDR)
        message = f"Game server started at addr:{address}"
        lb.send(message.encode())
        lb.close()


    def start_server(self):

        PORT_RANGE = range(PORT_RANGE_START, PORT_RANGE_END) # Port range to bind to
        for port in PORT_RANGE:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.bind((GS_SERVER, port))
                self.sock.listen()
                print(f"Successfully bound to port {port}")
                self.port = port
                self.server = GS_SERVER
                self.address = (GS_SERVER, port)
                break

            except OSError as e:
                # Print an error message if the socket failed to bind to the current port
                print(f"Failed to bind to port {port}: {e}")
                continue
            except:
                if self.sock:
                    self.sock.close()
                sys.exit()
        if not self.port:
            print("FAILED TO BIND TO PORTS")
            sys.exit()
        

        print("Sending information to load balancer.")
        self.register_to_load_balancer(self.address)
        print(f"Server is listening on {self.address}")
        while (int(threading.active_count() - 1) <= 2):
                for i in range(2):
                    conn, addr = self.sock.accept()
                    thread = threading.Thread(
                        target=self.handle_client, args=(conn, addr, i+1))
                    thread.start()
                    print(f"[ACTIVE CONNECTIONS] {len(self.player_connections)}")


if __name__ == "__main__":
    gs = Gameserver()
    gs.start_server()
