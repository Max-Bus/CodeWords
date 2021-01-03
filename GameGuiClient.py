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
import time
from Message import Message


class GameGUIClient(App):
    def __init__(self, ip, port):
        super(GameGUIClient, self).__init__()

        # socket connection stuff
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.team = '1'


    def build(self):
        self.root = FullGUI(self.socket)

        listener = self.ServerHandler(self)
        thread = Thread(target=listener,daemon= True)
        thread.start()


    class ServerHandler:
        def __init__(self, client):
            # client is the gui client instance
            self.gui_client = client

            self.is_named = False

        def __call__(self):

            incoming = 'temp'

            while incoming is not None:
                time.sleep(0.01)
                # get size (represented as int 8 bytes) of the incoming message
                size = self.gui_client.socket.recv(8)
                # turn the byte stream into an integer
                data_size = int.from_bytes(size, 'big')
                print(data_size)
                # read the corresponding number of bits
                data = self.gui_client.socket.recv(data_size)
                # reconstitute Message from bytes
                incoming = pickle.loads(data)

                print(incoming.TAG)
                if incoming.TAG == 'ALLOWJOINGAME':
                    self.is_named = True
                    print('welcome ' + incoming.name)

                    # send JOIN protocol
                    self.send(Message(TAG='JOIN', name=incoming.name, text_message=incoming.text_message))

                elif incoming.TAG == 'TEAMSELECTED':
                    self.team = incoming.text_message
                    print(str(self.team))
                    print(str(type(self.team)))
                    self.gui_client.root.lobby.change_team(self.team)
                elif incoming.TAG == "CODEMASTER":
                    self.gui_client.root.lobby.codemaster(incoming.text_message)
                elif incoming.TAG == 'STARTGAME':
                    # open gameboard
                    print(len(incoming.board.board[0]))
                    self.gui_client.root.go_to_game(incoming.board.board,
                                                    (not incoming.text_message and self.gui_client.team == '0') or (incoming.text_message and self.gui_client.team == '1'))


                    # # todo make nicer + fix logic
                    # if (not incoming.text_message and self.gui_client.team == '0') or (incoming.text_message and self.gui_client.team == '1'):
                    #     self.gui_client.root.gamegui.word_board.set_initial_board(incoming.board, True)
                    # else:
                    #     self.gui_client.root.gamegui.word_board.set_initial_board(incoming.board, False)

                elif incoming.TAG == 'BOARDUPDATE':
                    print('updating board')
                    print(str(incoming.text_message))
                    if(incoming.text_message is None):
                        #todo
                        self.gui_client.root.gamegui.word_board.update_board(incoming.board.board, False)
                    else:
                        self.gui_client.root.gamegui.win_lose(incoming.text_message==self.team)
                        self.gui_client.root.go_to_lobby()
                elif incoming.TAG == "CLUE":
                    word = incoming.text_message.split(" ")
                    word.append("")
                    self.gui_client.root.gamegui.hint_area.receive_hint(word[0],word[1])

                elif incoming.TAG == 'GOTOLOBBY':
                    print('i am here now')
                    self.gui_client.root.go_to_lobby()
                    self.team= incoming.text_message
                    time.sleep(0.01)
                    self.gui_client.root.lobby.change_team(self.team)



                elif incoming.TAG == 'CHAT':
                    self.gui_client.root.gamegui.game_chat.display(incoming.text_message)
                    print(incoming.text_message)

                # elif incoming.TAG == 'GOTOGAME':
                #     self.gui_client.root.go_to_game()

                elif incoming.TAG == 'ERROR':
                    # todo, error console?
                    print(incoming.text_message)

        def send(self, msg):
            time.sleep(0.01)
            # serialize message
            serialized_msg = pickle.dumps(msg)
            # get size (represented as int 8 bytes) of message in bytes
            size_of_msg = sys.getsizeof(serialized_msg)
            # serialize the integer into a 8 byte byte stream, most significant bit first
            data_size = size_of_msg.to_bytes(8, 'big')
            # send the size of the data
            self.gui_client.socket.sendall(data_size)
            # send data
            self.gui_client.socket.sendall(serialized_msg)

if __name__ == "__main__":
    gui = GameGUIClient('ec2-13-58-169-82.us-east-2.compute.amazonaws.com', 59001)
    gui.run()