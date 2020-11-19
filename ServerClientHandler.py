from threading import Thread
import pickle
import threading
class ServerClientHandler(Thread):

    # list of other clients in the room, as well as the clientconnectiondata for this individual client
    def __init__(self, client,server):
        super(ServerClientHandler, self).__init__()
        self.MAXPLAYERS = 8
        self.client_list = None
        self.room = None
        self.client = client
        self.board = None
        self.server = server

    def run(self):
        print(' i am here ')
        while(True):


            size = self.client.socket.recv(8)
            print(size)
            data_size = int.from_bytes(size,'big')
            print(data_size)

            k = self.client.socket.recv(data_size)
            print(k)
            request = pickle.loads(k)
            print(request)
            print(request.TAG)
            lock = threading.Lock()
            if request.TAG == "JOIN":
                lock.acquire()
                info, self.room = self.server.join_make_room(self.client, request.text_message)
                lock.release()
                self.client_list = info[0]
                self.board = info[1]
                print("huzzah")
                break
            if request.TAG == "LEAVE":
                lock.acquire()
                self.server.leave_room(self.client, self.room)
                lock.release()
        return