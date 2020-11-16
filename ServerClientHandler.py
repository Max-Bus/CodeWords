from threading import Thread
from ChatServer import join_make_room,leave_room
class ServerClientHandler(Thread):

    # list of other clients in the room, as well as the clientconnectiondata for this individual client
    def __init__(self, client):
        self.MAXPLAYERS = 8
        self.client_list = None
        self.room = None
        self.client = client
        self.board = None
    def run(self):
        print(' i am here ')
        request = self.client.socket.recieveall()

        # todo handle messages

        if request.TAG == "JOIN":
            info,self.room = join_make_room(self.client,request.text_message)
            self.client_list = info[0]
            self.board = info[1]
        if request.TAG == "LEAVE":
            leave_room(self.client, self.room)
