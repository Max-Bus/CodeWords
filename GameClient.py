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
        msg2 = Message("JOIN")
        msg2 = pickle.dumps(msg2)

        msg1 = pickle.dumps(sys.getsizeof(msg2))
        print(msg2)

        self.socket.sendall(msg1)

        #self.socket.sendall(msg2)

if __name__ == '__main__':
    k = GameClient("localhost",54321)
    k.test()