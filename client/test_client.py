import socket
import pickle


HEADER = 1024
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = '127.0.0.1'
ADRR = (SERVER, PORT)


class ShipBoard():
    def __init__(self):
        self.board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]

    def display_board(self):
        print("   0   1   2")
        print("0: " + self.board[0][0] + " | " +
              self.board[0][1] + " | " + self.board[0][2])
        print("  ---+---+---")
        print("1: " + self.board[1][0] + " | " +
              self.board[1][1] + " | " + self.board[1][2])
        print("  ---+---+---")
        print("2: " + self.board[2][0] + " | " +
              self.board[2][1] + " | " + self.board[2][2])
        print()

    def input_board(self):
        ship_positions = 3
        board.display_board()
        while True:
            print(f"You have {ship_positions} ship positions remaining.")
            if (ship_positions == 0):
                return self.board
            row = int(input("What row would you like to put a ship on? (0-2):"))
            col = int(input("What col would you like to put a ship on? (0-2):"))
            if (0 <= row <= 2) and (0 <= col <= 2) and (self.board[row][col] == " "):
                self.board[row][col] = 'X'
                ship_positions = ship_positions - 1
            else:
                print("That is not a valid ship position!")
            board.display_board()


class GameConnection():
    def __init__(self, board):
        """
            Use self.client to send messages
        """
        self.board = board
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADRR)

    def send_board(self, board):
        """
            Client sends the board to server
        """
        package = pickle.dumps(board)
        self.client.send(package)
        print(self.client.recv(HEADER).decode(FORMAT))
        

    def receive_board(self):
        """
            Receives the board from the server (opponent)
        """
        print("Waiting for server to respond...")
        enc = self.client.recv(HEADER)
        self.board = enc.decode(FORMAT)
        return self.board


# set up the game
board = ShipBoard()
player_board = board.input_board()
gc = GameConnection(player_board)
board_to_server = gc.send_board(player_board)


#while True:
    #opponent_board = gc.receive_board()


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
