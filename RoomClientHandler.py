from threading import Thread

class RoomClientHandler(Thread):

    # list of other clients in the room, as well as the clientconnectiondata for this individual client
    def __init__(self, client_list, client):
        self.client_list = client_list
        self.client = client

    def run(self):
        print(' i am here ')

        # todo receive input from user here