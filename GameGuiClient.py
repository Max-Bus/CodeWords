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
        self.player_name = ''
        self.is_codemaster = False


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
            self.in_game = False

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
                    self.gui_client.player_name = incoming.name
                    self.is_named = True
                    print('welcome ' + incoming.name)

                    # send JOIN protocol
                    self.send(Message(TAG='JOIN', name=incoming.name, text_message=incoming.text_message))

                elif incoming.TAG == 'TEAMSELECTED':
                    self.team = incoming.text_message
                    self.gui_client.root.lobby.change_team(self.team)

                elif incoming.TAG == "CODEMASTER":
                    self.gui_client.root.lobby.codemaster(incoming.text_message)
                    self.gui_client.is_codemaster = incoming.text_message

                elif incoming.TAG == 'LOBBYTEAMUPDATE':
                    # [team num]:name
                    team = int(incoming.text_message.split(':')[0])
                    nm = incoming.text_message.split(':')[1]
                    self.gui_client.root.lobby.adjust_teams(nm, team)

                elif incoming.TAG == 'STARTGAME':
                    # open gameboard
                    print(len(incoming.board.board[0]))
                    self.in_game = True
                    self.gui_client.root.go_to_game(incoming.board.board,
                                                    (not incoming.text_message and self.gui_client.team == '0') or (incoming.text_message and self.gui_client.team == '1'))


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

                elif incoming.TAG == 'UPDATEPARTICIPANTS':
                    print('updating participants')
                    # options
                    # game;[team num]:name1,[team num]:name2,[team num]:name3....
                    # lobby;[team num]:name1,[team num]:name2,[team num]:name3....

                    which_screen = incoming.text_message.split(';')[0]
                    names_str = incoming.text_message.split(';')[1]

                    # modify string to add 'you' and 'cm' (codemaster)
                    str_to_add = ' (you)'

                    i = names_str.index(self.gui_client.player_name) + len(self.gui_client.player_name)
                    names_str = names_str[:i] + str_to_add + names_str[i:]

                    if which_screen == 'game':
                        self.gui_client.root.gamegui.game_chat.update_participants(names_str)
                    elif which_screen == 'lobby':
                        self.gui_client.root.lobby.readd_all_participants(names_str)


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
    gui = GameGUIClient('localhost', 54321)
    gui.run()