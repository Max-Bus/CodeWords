import pickle
import socket
import sys

class ClientServerHandler:

    def __init__(self, socket):
        self.socket = socket
        self.is_named = False

    def __call__(self):

        incoming = 'temp'

        while not incoming is None:
            # get size (represented as int 8 bytes) of the incoming message
            size = self.socket.recv(8)
            # turn the byte stream into an integer
            data_size = int.from_bytes(size, 'big')
            # read the corresponding number of bits
            data = self.socket.recv(data_size)
            # reconstitute Message from bytes
            incoming = pickle.loads(data)

            if incoming.TAG == 'SUBMITNAME':
                print('enter your username')

            elif incoming.TAG == 'NAME':
                self.is_named = True
                print('welcome ' + incoming.text_message)








