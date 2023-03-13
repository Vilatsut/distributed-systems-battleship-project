import time
import socket
import pickle
import sys
from time import sleep

HEADER = 1024
FORMAT = 'utf-8'
#load balancer port
PORT1 = 16432
#game server ports
PORT2 = 5050
PORT3 = 5051
PORT4 = 5052
SERVER = '127.0.0.1'
CHAT_SERVER = None
CHAT_PORT = None
RESTARTED = False
GAME_ID = None


#ADRR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"


SHIP_TYPES = {
    # 'Carrier': 5,
    # 'Battleship': 4,
    # 'Cruiser': 3,
    # 'Submarine': 3,
    'Destroyer': 1
}
BOARD_SIZE = 3

class ShipBoard():
    def __init__(self):
            self.board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]

    def display_board(self):
        print('  | ' + ' | '.join(str(i) for i in range(BOARD_SIZE)))
        for i in range(BOARD_SIZE):
            print(str(i) + ' | ' + ' | '.join(str(self.board[i][j]) for j in range(BOARD_SIZE)))
        print()


    def input_board(self):
        self.display_board()

        for ship, ship_positions in SHIP_TYPES.items():
            while True:
                while ship_positions > 0:
                    print(f"\nYou have {ship_positions} ship positions for {ship} remaining.")
                    try:
                        row = int(str(input(f"What row would you like to put a ship on? (0-{BOARD_SIZE-1}):")))
                        col = int(str(input(f"What col would you like to put a ship on? (0-{BOARD_SIZE-1}):")))
                    except ValueError as e:
                        print("Thats not an int!!!")
                        continue

                    if (0 <= row <= 2) and (0 <= col <= 2) and (self.board[row][col] == " "):
                        self.board[row][col] = 'X'
                        ship_positions = ship_positions - 1
                    else:
                        print("That is not a valid ship position!")
                    self.display_board()
                break
        return self.board

    def input_shot(self):

        while True:
            # prompt the player to enter the row and column of their shot
            try:
                row = int(input(f"Enter the row of your shot (0-{BOARD_SIZE-1}): "))
                col = int(input(f"Enter the col of your shot (0-{BOARD_SIZE-1}): "))
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 10.")
                continue

            # check that the row and column are within the valid range
            if row < 0 or row > BOARD_SIZE-1 or col < 0 or col > BOARD_SIZE-1:
                print("Invalid input. Please enter a number between 1 and 10.")
                continue

            # return the shot coordinates as a tuple
            return (row, col)

class Client:

    def __init__(self, host, ports, gameid=None, c_host=None, c_port=None) -> None:
        self.server_host = host
        self.server_ports = ports
        self.server_port = None
        self.chat_host = c_host
        self.chat_port = c_port
        self.sock = None
        self.chatsock = None

        self.gameid = gameid

    def start(self):
        print("Starting game...")
        connected = False
        for port in self.server_ports:
            if connected:
                break
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.server_host, int(port)))
                if self.chat_port:
                    print("chat server is online")
                    try:
                        self.chatsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.chatsock.connect((self.chat_host, self.chat_port))
                        print(self.chat_host, self.chat_port)
                        print("connected to chat server succesfully")
                    except Exception as e:
                        print("Unable to connect to chat socket with exception: ", e)

            except Exception as e:
                print("Unable to connect to socket with exception: ", e)
                if self.sock:
                    self.sock.close()
                sys.exit(1)
            else:
                print(f"Connected to port{port}")
                connected = True
        self.play()

    def play(self):
        if not RESTARTED:
            board = ShipBoard()
            board.input_board()
            self.send_board(board.board)
        else:
            msg = "send old board"
            self.sock.send(msg.encode())
            try:
                print("Waiting for server to send old board...")
                response = self.sock.recv(HEADER).decode()
                # print("RESPONSE WAS " + response)
            except TimeoutError as e:
                print("Server connection timed out receiving")
            # tähän jotenkin se boardin asettamine rediksestä
        while True:
            print("got here!")
            # Response is SHOOT when its players turn to shoot, HIT when last shot hit something and its time to shoot again, MISS when last hit missed, WIN when player won
            try:
                print("Waiting for server response...")
                response = self.sock.recv(HEADER).decode()
                # print("RESPONSE WAS " + response)
            except TimeoutError as e:
                print("Server connection timed out receiving")

            for response in response.split("?"):
                if response.startswith("SHOOT"):
                    print("Your turn to shoot!")
                    shot = board.input_shot()
                    package = pickle.dumps(shot)
                    try:
                        self.sock.send(package)
                    except:
                        print("Sending the shot failed")

                elif response.startswith("WAIT"):
                    print("Wait for your turn!")
                elif response.startswith("HIT"):
                    print("You hit an enemy ship! Shoot again!!")
                    shot = board.input_shot()
                    package = pickle.dumps(shot)
                    try:
                        self.sock.send(package)
                    except:
                        print("Sending the shot failed")

                elif response.startswith("MISS"):
                    print("You missed. Wait for your turn.")
                elif response.startswith("WIN"):
                    print("You sunk all enemy ships and won the game!!!")
                    return
                elif response.startswith("LOSE"):
                    print("The other player sunk all your ships!!!")
                    return

                elif response.startswith("PRINT"):
                    print(f"Both Boards look almost like  \n{response}\n")



            # player_input = input("To send a chat start message with C, to check for turn press anything else.")
            # this could perhaps use a better implementation...
            # if player_input.upper().startswith("C"):
                # somehow need to implement user names for chat but lets think about that later lmao
                # print("message sent to chat server.")
                # self.chatsock.send(player_input.encode())
            # prints other players messages
            # print(self.chatsock.recv(HEADER).decode(FORMAT))



    def send_board(self, board):
        """
            Client sends the board to server
        """
        package = pickle.dumps(board)
        self.sock.send(package)
        # print(self.sock.recv(HEADER).decode(FORMAT))



def setup_client(gameid=None):
    data = b''
    ports = b''
    chat_online = b''


    # asks for the ports of online game servers (5050, 5051, 5052)
    ask_for_servers = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ask_for_servers.connect((SERVER, PORT1))
    if gameid:
        message = "reconnect:" + str(gameid)
        print(message)
    else:
        message = "send servers pls!"

    ask_for_servers.send(message.encode())

    if not gameid:
        # waits until it gets response from loadbalancer
        while not data:
            print("Connecting to the queue system...")
            data = ask_for_servers.recv(HEADER)

    while not ports:
        print("Waiting for ports...")
        sleep(0.5)
        ports = ask_for_servers.recv(HEADER)
        ports_de = ports.decode()
        print(f"Found ports {ports}")

    print("received ports: ", ports.decode())

    if ('6969') in ports_de:
        ports_de = ports_de.split('||')[0]
        print(f"Prots_de: {ports_de}")
        CHAT_PORT=int(6969)
        CHAT_SERVER=str("127.0.0.1")
        chat_online = True

    print("received data: ", data.decode())
    print("received ports: ", ports_de)
    if chat_online:
        print("chat server set")
        #chat server ip and port
        CHAT_SERVER = '127.0.0.1'
        CHAT_PORT = 6969

    ask_for_servers.close()
    ports_de = str(ports_de).strip("b,'][").split(',')
    print(ports)
    if CHAT_SERVER:
        print("WITH CHAT")
        cl = Client(SERVER, ports_de, gameid, CHAT_SERVER, CHAT_PORT)
    #else:
    elif gameid:
        print("WITHOUTCHET")
        cl = Client(SERVER, ports_de, gameid)
    else:
        print("ELSE NO CHAT NO ID")
        cl = Client(SERVER, ports_de)
    cl.start()



if __name__ == "__main__":
    while True:
        print("     ~~Welcome to Pattleshibz~~")
        print("1. Quick join game      ")
        print("2. Rejoin a game     ")
        print("3. Exit     ")
        choice = input("Choose: ")
        if choice == "1":
            setup_client()
        if choice == "2":
            gameid = input("Give game id of previous game: ")
            RESTARTED = True
            setup_client(gameid)
        if choice == "3":
            sys.exit()
