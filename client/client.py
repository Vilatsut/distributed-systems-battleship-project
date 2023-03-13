import sys
import socket
import signal
import pickle
from ast import literal_eval
import time

HEADER = 4096

LB_SERVER = '127.0.0.1'
LB_PORT = 6969
LB_ADDR = (LB_SERVER, LB_PORT)

SHIP_TYPES = {
    # 'Carrier': 5,
    # 'Battleship': 4,
    # 'Cruiser': 3,
    # 'Submarine': 3,
    'Destroyer': 1
}
BOARD_SIZE = 3


class Client:
    def __init__(self) -> None:
        self.lb_sock = None
        self.sock = None
        self.board = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]

        self.game_server_address = None

        # Trap keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)
    def sighandler(self, signum, frame):
        print("\nShutting down the client")
        if self.lb_sock:
            self.lb_sock.close()
        if self.sock:
            self.sock.close()
        sys.exit(1)
    
    def display_board(self):
        print('  | ' + ' | '.join(str(i) for i in range(BOARD_SIZE)))
        for i in range(BOARD_SIZE):
            print(str(i) + ' | ' + ' | '.join(str(self.board[i][j]) for j in range(BOARD_SIZE)))
        print()

    def get_board(self):
        try:
            board = self.sock.recv(HEADER)
        except Exception as e:
            print(f"Error receiving board from game server: {e}")
            self.sock.close()
            sys.exit()
        print(board)
        self.board = literal_eval(board.decode())[0]
        print(self.board)
        self.display_board()
    
    def send_board(self):
        package = str(self.board).encode()
        self.sock.send(package)

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

    def reconnect(self, gameid):
        try:
            self.lb_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.lb_sock.connect(LB_ADDR)
            message = "reconnect:" + str(gameid)
            self.lb_sock.send(message.encode())
            response = self.lb_sock.recv(HEADER)

            print(f"Received address: {response.decode()}")

            self.game_server_address = literal_eval(response.decode())
        except Exception as e:
            print(f'Error using loadbalancer to reconnect: {e}')
        
        finally:
            if self.lb_sock:
                self.lb_sock.close()
        
        # Connect to gameserver
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(self.game_server_address)
            
        except Exception as e:
            print("Unable to connect to socket with exception: ", e)
            if self.sock:
                self.sock.close()
            sys.exit(1)
        else:
            print(f"Connected to address: {self.game_server_address}")

        client_status = f"reconnect:{gameid}"
        self.sock.send(client_status.encode())

        self.get_board()
        self.start()

    def connect(self):
        
        # Get game server address from load balancer
        try:
            self.lb_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.lb_sock.connect(LB_ADDR)

            message = "send servers pls!"
            self.lb_sock.send(message.encode())
            response = self.lb_sock.recv(HEADER).decode()
            print(f"Received address: {response}")
            if "N/A" in response:
                print("No game servers available!!!")
                sys.exit()
            self.game_server_address = literal_eval(response)
        except Exception as e:
            print(f'Error using loadbalancer to reconnect: {e}')
        
        finally:
            if self.lb_sock:
                self.lb_sock.close()

        # Connect to gameserver
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(self.game_server_address)
            
        except Exception as e:
            print("Unable to connect to socket with exception: ", e)
            if self.sock:
                self.sock.close()
            sys.exit(1)
        else:
            print(f"Connected to address: {self.game_server_address}")

        client_status = "connect"
        self.sock.send(client_status.encode())

        self.input_board()
        self.start()

    def start(self):

        self.send_board()

        while True:
            # Response is SHOOT when its players turn to shoot, HIT when last shot hit something and its time to shoot again, MISS when last hit missed, WIN when player won
            try:
                print("Waiting for server command...")
                response = self.sock.recv(HEADER).decode()
            except Exception as e:
                print(f"Error receiving command from server with error: {e}")

            for response in response.split("?"):
                if response.startswith("SHOOT"):
                    print("Your turn to shoot!")
                    shot = self.input_shot()
                    package = pickle.dumps(shot)
                    try:
                        self.sock.send(package)
                    except:
                        print("Sending the shot failed")

                elif response.startswith("START"):
                    print(response)
                elif response.startswith("WAIT"):
                    print("Wait for your turn!")
                elif response.startswith("HIT"):
                    print("You hit an enemy ship! Shoot again!!")
                    shot = self.input_shot()
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
                
                elif response == "":
                    # print("Server sent empty string!!!")
                    continue
                    # return
                else:
                    print(f"Unknown message from server: {response}")



if __name__ == "__main__":

    while True:
        cl = Client()

        print("     ~~Welcome to Pattleshibz~~")
        print("1. Quick join game      ")
        print("2. Rejoin a game     ")
        print("3. Exit     ")
        choice = input("Choose: ")
        if choice == "1":
            cl.connect()
        if choice == "2":
            gameid = input("Give game id of previous game: ")
            cl.reconnect(gameid)
        if choice == "3":
            sys.exit()
        
