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

    def test(self):
        raw = Message("JOIN")
        msg = pickle.dumps(raw)

        sizeOfMsg = sys.getsizeof(msg)
        print(msg)
        print(type(sizeOfMsg))
        print(sizeOfMsg)



        data_size = sizeOfMsg.to_bytes(8,'big')

        print(data_size)
        self.socket.sendall(data_size)

        self.socket.sendall(msg)

if __name__ == '__main__':
    k = GameClient("localhost",54321)
    k.test()