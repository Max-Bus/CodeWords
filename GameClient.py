import socket
from Message import Message
import pickle
import time
import sys
class GameClient:

    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip,port))
        # todo thread handle incoming

    def gui_interpreter(self,info):
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
        dataSize = sizeOfMsg.to_bytes(8,'big')

        #send the size of the data
        self.socket.sendall(dataSize)
        #send data
        self.socket.sendall(msg)
        while 1:
            pass

if __name__ == '__main__':
    k = GameClient("localhost",54321)
    k.one_ping_only()