import kivy
from threading import Thread
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from GUIRunner import *
import socket
import pickle
from Message import Message


class GameGUIClient(App):
    def __init__(self, ip, port):
        super(GameGUIClient, self).__init__()

        # socket connection stuff
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))


    def build(self):
        self.root = FullGUI(self.socket)

        listener = self.ServerHandler(self)
        thread = Thread(target=listener)
        thread.start()


    class ServerHandler:
        def __init__(self, client):
            # client is the gui client instance
            self.gui_client = client

            self.is_named = False

        def __call__(self):

            incoming = 'temp'

            while incoming is not None:
                # get size (represented as int 8 bytes) of the incoming message
                size = self.gui_client.socket.recv(8)
                # turn the byte stream into an integer
                data_size = int.from_bytes(size, 'big')
                # read the corresponding number of bits
                data = self.gui_client.socket.recv(data_size)
                # reconstitute Message from bytes
                incoming = pickle.loads(data)

                if incoming.TAG == 'SUBMITNAME':
                    # todo delete (naming period is defined by user actions, not the server)
                    print('enter your username')

                elif incoming.TAG == 'NAMEACCEPT':
                    self.is_named = True
                    print('welcome ' + incoming.name)

                elif incoming.TAG == 'ERROR':
                    # todo, error console?
                    print(incoming.text_message)

if __name__ == "__main__":
    gui = GameGUIClient('localhost', 54321)
    gui.run()