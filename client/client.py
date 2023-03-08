import socket
import pickle
import sys

HEADER = 1024
FORMAT = 'utf-8'
#load balancer port
PORT1 = 16432
#game server ports
PORT2 = 5050
PORT3 = 5051
PORT4 = 5052
SERVER = '127.0.0.1'
#ADRR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"


SHIP_TYPES = {
    # 'Carrier': 5,
    # 'Battleship': 4,
    # 'Cruiser': 3,
    'Submarine': 3,
    'Destroyer': 2
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
                        row = int(str(input("What row would you like to put a ship on? (0-2):")))
                        col = int(str(input("What col would you like to put a ship on? (0-2):")))
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

    

class Client:

    def __init__(self, host, port) -> None:
        self.server_host = host
        self.server_port = port
        self.sock = None

    def start(self):
        print("Starting game...")

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_host, self.server_port))
        except Exception as e:
            print("Unable to connect to socket with exception: ", e)
            if self.sock:
                self.sock.close()
            sys.exit(1)
        self.play()

    def play(self):
        board = ShipBoard()
        board.input_board()
        self.send_board(board.board)


    def send_board(self, board):
        """
            Client sends the board to server
        """
        package = pickle.dumps(board)
        self.sock.send(package)
        print(self.sock.recv(HEADER).decode(FORMAT))

if __name__ == "__main__":
    data = b''
    ask_for_servers = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ask_for_servers.connect((SERVER, PORT1))
    message = "send servers pls!"
    ask_for_servers.send(message.encode())
    while not data:
        data = ask_for_servers.recv(HEADER)
    print("received data: ", data.decode())
    ask_for_servers.close()
    cl = Client(SERVER, PORT2)
    cl.start()


"""
example of a msg send to chat server

   def send_chat(self):

        while True:
            msg = input("send message: ")
            if msg == self.DISCONNECT_MESSAGE:
                break
            message = msg.encode(self.FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(self.FORMAT)
            send_length += b' ' * (self.HEADER - len(send_length))
            self.client.send(send_length)
            self.client.send(message)
            print(self.client.recv(2048).decode(self.FORMAT))
            print("sent!")

"""
