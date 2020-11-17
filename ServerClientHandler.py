from threading import Thread
import pickle
class ServerClientHandler(Thread):

    # list of other clients in the room, as well as the clientconnectiondata for this individual client
    def __init__(self, client,server):
        self.MAXPLAYERS = 8
        self.client_list = None
        self.room = None
        self.client = client
        self.board = None
        self.server = server

    def run(self):
        print(' i am here ')
        while(True):

            size = self.client.socket.recv(4)
            print(size)
            data_size = pickle.loads(size)
            print(size)
            print(data_size)
            request = pickle.loads(self.client_list.socket.recv(size))

            # todo handle messages
            if request.TAG == "JOIN":
                info,self.room = self.server.join_make_room(self.client,request.text_message)
                self.client_list = info[0]
                self.board = info[1]
                print("huzzah")
            if request.TAG == "LEAVE":
                self.server.leave_room(self.client, self.room)
