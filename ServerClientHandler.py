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
            #this may need to be locked as it may not be thread safe

            #get size of the incoming message
            size = self.client.socket.recv(8)

            #turn the byte stream into an integer
            data_size = int.from_bytes(size,'big')

            #read the corresponding number of bits
            k = self.client.socket.recv(data_size)

            #reconstitute message from bytes
            request = pickle.loads(k)

            lock = threading.Lock()
            if request.TAG == "JOIN":
                lock.acquire()
                #this function should be locked
                info, self.room = self.server.join_make_room(self.client, request.text_message)
                lock.release()
                self.client_list = info[0]
                self.board = info[1]
                print("huzzah")
                break
            if request.TAG == "LEAVE":
                lock.acquire()
                # this function should be locked
                self.server.leave_room(self.client, self.room)
                lock.release()
        return