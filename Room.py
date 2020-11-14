from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from RoomClientHandler import RoomClientHandler
import time

from Board import Board

class Room(Thread):


    def __init__(self, board_dimension):
        self.MAXPLAYERS = 8
        self.executor = ThreadPoolExecutor(max_workers=self.MAXPLAYERS)

        # list of client connection data
        self.client_list = []

        self.board = Board(board_dimension)

    def run(self):
        # temporary code
        while True:
            time.sleep(1)
            print(1)

    def add_player(self, client):

        # execute a serverclienthandler for the client first,
        player = RoomClientHandler(client_list=self.client_list, client=client)
        self.executor.submit(player.run)
        self.client_list.append(client)



