from threading import Thread
import pickle
import socket
import sys
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
            try:
                #this may need to be locked as it may not be thread safe

                #get size of the incoming message
                size = self.client.socket.recv(8)

                #turn the byte stream into an integer
                data_size = int.from_bytes(size,'big')

                #read the corresponding number of bits
                data = self.client.socket.recv(data_size)

                #reconstitute message from bytes
                request = pickle.loads(data)

                if request.TAG == "JOIN":
                    #this function should be locked
                    info, self.room = self.server.join_make_room(self.client, request.text_message)
                    self.client_list = info[0]
                    self.board = info[1]
                    print("huzzah")
                    print(self.board)
                    print(self.client_list)
                    print(self.room)
                    continue
                elif request.TAG == "LEAVE":
                    # this function should be locked
                    self.server.leave_room(self.client, self.room)
                #elif :


            except Exception:
                print('error: ' + self.client.ip_address + ' leaving room')
                x = self.server.leave_room(self.client, self.room)
                if x:
                    print(self.client.ip_address+" Exited successfully")
                else:
                    print(self.client.ip_address+" Failed to exit")
                return
        return