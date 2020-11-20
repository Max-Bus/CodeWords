import socket
from Message import Message
import pickle
import time
import sys
from threading import Thread

class GameClient:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))

        # todo thread handle incoming

    def gui_interpreter(self, info):
        #todo make into nice gui
        pass

    def one_ping_only(self):
        #make message
        raw = Message("JOIN")

        #serialize message
        msg = pickle.dumps(raw)

        #get size of message in bytes
        sizeOfMsg = sys.getsizeof(msg)

        #serialize the integer into a 8 byte byte stream
        #most significant bit first
        dataSize = sizeOfMsg.to_bytes(8, 'big')

        #send the size of the data
        self.socket.sendall(dataSize)
        #send data
        self.socket.sendall(msg)

        while 1:
            pass

    def play(self):
        listener = self.ServerHandler(self)
        thread = Thread(target=listener, daemon=True)
        thread.start()

        # naming phase (line is the name)
        line = input()
        while not listener.is_named:

            # send the name to the server

            name_msg = Message(TAG="SUBMITNAME", text_message=line)
            # serialize message
            serialized_msg = pickle.dumps(name_msg)
            # get size (represented as int 8 bytes) of message in bytes
            size_of_msg = sys.getsizeof(serialized_msg)
            # serialize the integer into a 8 byte byte stream, most significant bit first
            data_size = size_of_msg.to_bytes(8, 'big')
            # send the size of the data
            self.socket.sendall(data_size)
            # send data
            self.socket.sendall(serialized_msg)

            # if failed, get name again
            line = input()


        # next phase
        self.one_ping_only()



    class ServerHandler:

        def __init__(self, client):
            # client is the gui client instance
            self.client = client

            self.is_named = False

        def __call__(self):

            incoming = 'temp'

            while not incoming is None:
                # get size (represented as int 8 bytes) of the incoming message
                size = self.client.socket.recv(8)
                # turn the byte stream into an integer
                data_size = int.from_bytes(size, 'big')
                # read the corresponding number of bits
                data = self.client.socket.recv(data_size)
                # reconstitute Message from bytes
                incoming = pickle.loads(data)

                if incoming.TAG == 'SUBMITNAME':
                    print('enter your username')

                elif incoming.TAG == 'NAME':
                    self.is_named = True
                    print('welcome ' + incoming.text_message)


if __name__ == '__main__':
    client = GameClient("localhost", 54321)
    client.play()
