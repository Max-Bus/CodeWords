# i think this is like the executor from java
from concurrent.futures import ThreadPoolExecutor
from ServerClientHandler import ServerClientHandler
from ClientConnectionData import ClientConnectionData
from Board import Board
from Message import *
import random
import string
import socket
import threading


print('server started')

# create thread, add it to the executor, and it runs? maybe theres a better way
executor = ThreadPoolExecutor(max_workers=16)
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 54321  # Port to listen on (non-privileged ports are > 1023)
ROOMS = {}
PUBLIC_ROOMS = []
P_LENGTH = 8
class Server:
    def __init__(self):
        self.lock = threading.Lock()
    def start_game(self,room):
        self.lock.acquire()
        ROOMS[room][2]=True
        board = ROOMS[room][1]
        client_list = ROOMS[room][0]
        cm_board = board.copy()
        p_board = board.copy()
        for i in range(len(board.board)):
            for j in range(len(board.board)):
                cm_board.board[i][j].selected = True
                p_board.board[i][j].color=-1
        for client in client_list:
            if(client.client.is_codemaster):
                client.boardClone = cm_board.copy()
                client.send_msg(Message(TAG="STARTGAME",board=cm_board))
            else:
                client.boardClone = p_board.copy()
                client.send_msg(Message(TAG="STARTGAME", board=p_board))
        self.lock.release()
    def join_make_room(self,client, room):

        self.lock.acquire()
        print("making_rooms")
        global ROOMS
        global PUBLIC_ROOMS
        global P_LENGTH
        print(PUBLIC_ROOMS)
        if(room == None):
            for room in PUBLIC_ROOMS:
                if(room in ROOMS.keys() and len(ROOMS[room][0])<8 and not ROOMS[room][2]):
                    ROOMS[room][0].append(client)
                    self.lock.release()
                    return (ROOMS[room],room)

            # code from pynative.com
            letters = string.ascii_letters
            result_str = ''.join(random.choice(letters) for i in range(P_LENGTH))

            new_room = "!"+result_str
            board = Board(5)
            ROOMS[new_room] = ([client],board,False)
            PUBLIC_ROOMS.append(new_room)
            self.lock.release()
            return (ROOMS[new_room],new_room)

        elif(room in ROOMS.keys() and len(ROOMS[room][0])<8 and not ROOMS[room][2]):
            ROOMS[room][0].append(client)
            self.lock.release()
            return (ROOMS[room],room)

        else:
            new_room = room
            board = Board(5)
            ROOMS[new_room] = ([client], board,False)
            self.lock.release()
            return (ROOMS[new_room],new_room)


    def leave_room(self,client,room):
        self.lock.acquire()
        global ROOMS
        global PUBLIC_ROOMS
        if(room in ROOMS.keys()):
            ROOMS[room][0].remove(client)
            if (len(ROOMS[room][0])<1):
                print(ROOMS[room][0])
                del ROOMS[room]
                if(room in PUBLIC_ROOMS):
                    PUBLIC_ROOMS.remove(room)
            self.lock.release()
            return True
        self.lock.release()
        return False
    def turn(self,room):
        self.lock.acquire()
        ROOMS[room][1].turn = (ROOMS[room][1].turn+1)%2
        self.lock.release()

    def select(self,room,x,y):
        self.lock.acquire()
        ROOMS[room][1].board[x][y].selected = True
        self.lock.release()


server = Server()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        print('Connected by', addr)
        rm = ServerClientHandler(ClientConnectionData(conn, addr), server)
        executor.submit(rm.run)


