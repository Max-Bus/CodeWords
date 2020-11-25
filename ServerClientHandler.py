from threading import Thread
import pickle
import socket
import sys
from Message import *
import re


class ServerClientHandler(Thread):

    # list of other clients in the room, as well as the clientconnectiondata for this individual client
    def __init__(self, client, server):
        super(ServerClientHandler, self).__init__()
        self.MAXPLAYERS = 8
        self.client_list = None
        self.room = None
        self.client = client
        self.board = None
        self.server = server

    def send_msg(self,msg):
        # serialize message
        serialized_msg = pickle.dumps(msg)
        # get size (represented as int 8 bytes) of message in bytes
        size_of_msg = sys.getsizeof(serialized_msg)
        # serialize the integer into a 8 byte byte stream, most significant bit first
        data_size = size_of_msg.to_bytes(8, 'big')
        # send the size of the data
        self.client.socket.sendall(data_size)
        # send data
        self.client.socket.sendall(serialized_msg)

    def get_msg(self):
        # get size of the incoming message
        size = self.client.socket.recv(8)

        # turn the byte stream into an integer
        data_size = int.from_bytes(size, 'big')

        # read the corresponding number of bits
        data = self.client.socket.recv(data_size)

        # reconstitute message from bytes
        request = pickle.loads(data)

        return request

    def run(self):
        try:
            print('i am here ')
            # naming portion

            # name_msg = Message(TAG="SUBMITNAME")
            # self.send_msg(name_msg)

            # listening loop
            while(True):
                # this may need to be locked as it may not be thread safe

                request = self.get_msg()
                print('msg received: ' + request.TAG)

                if request.TAG == "JOIN":
                    # this function should be locked
                    info, self.room = self.server.join_make_room(self.client, request.text_message)
                    self.client_list = info[0]
                    self.board = info[1]

                    # print("huzzah")
                    # print(self.board)
                    # print(self.client_list)
                    # print(self.room)

                    self.send_msg(Message(TAG='JOINSUCCESSFUL', text_message='joined room'))

                    # log on server
                    if request.text_message is None:
                        print(request.name + ' has joined public room.')
                    else:
                        print(request.name + ' had joined private room ' + request.text_message + '.')

                    continue

                elif request.TAG == "LEAVE":
                    # this function should be locked
                    self.server.leave_room(self.client, self.room)

                # send their accepted name and send back the id if valid
                elif request.TAG == 'SUBMITNAME':
                    # todo
                    requested_name = request.name
                    if len(requested_name) > 3 and re.search(r'^[a-zA-Z0-9]*$', requested_name):
                        # public room
                        if request.text_message is None:
                            self.send_msg(Message(TAG='ALLOWJOIN', name=requested_name))

                        # private room
                        else:
                            room_id = request.text_message
                            self.send_msg(Message(TAG='ALLOWJOIN', name=requested_name, text_message=room_id))

                    # invalid name
                    else:
                        # todo, how will errors be handled?
                        self.send_msg(Message(TAG='ERROR', text_message='name must be alphanumeric and at least length 4'))





        except socket.error:
            print('error: ' + str(self.client.ip_address) + ' leaving room')
            x = self.server.leave_room(self.client, self.room)
            if x:
                print(str(self.client.ip_address)+" Exited successfully")
            else:
                print(str(self.client.ip_address)+" Failed to exit room")
                print("shutting down connection")
            return

        return
