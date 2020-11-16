# i think this is like the executor from java
from concurrent.futures import ThreadPoolExecutor
from ServerClientHandler import ServerClientHandler
from ClientConnectionData import ClientConnectionData
from Board import Board
import random
import string
import socket


print('server started')

# create thread, add it to the executor, and it runs? maybe theres a better way
executor = ThreadPoolExecutor(max_workers=2)
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 54321  # Port to listen on (non-privileged ports are > 1023)
Rooms = {}
Public = []
Password_Length = 8


def join_make_room(client, room):
    global Rooms
    global Public
    global Password_Length
    if(room == None):
        for room in Public:
            if(room in Rooms.values() and len(Rooms[room][0])<8):
                Rooms[room][0].append(client)
                return (Rooms[room],room)
        # code from pynative.com
        letters = string.ascii_letters
        result_str = ''.join(random.choice(letters) for i in range(LENGTH))

        new_room = "!"+result_str
        board = Board(5)
        Rooms[new_room] = ([client],board)
        return (Rooms[new_room],new_room)

    elif(room in Rooms.values() and len(Rooms[room][0])<8):
        Rooms[room][0].append(client)
        return (Rooms[room],room)

    else:
        new_room = room
        board = Board(5)
        Rooms[new_room] = ([client], board)
        return (Rooms[new_room],new_room)

def leave_room(client,room):
    global Rooms
    global Public
    if(room in Rooms.values()):
        Rooms[room][0].remove(client)
        if (len(Rooms[room][0])<1):
            del Rooms[room]
        if(room in Public):
            Public.remove(room)
        return True
    else:
        return False



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        print('Connected by', addr)
        rm = ServerClientHandler(ClientConnectionData(conn,addr))
        executor.submit(rm.run,daemon=True)


