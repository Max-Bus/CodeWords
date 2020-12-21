import kivy
import threading
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
import pickle
import sys
from Message import *
import re
import time

class StartMenu(GridLayout):
    def __init__(self, socket, **kwargs):
        super(StartMenu, self).__init__(**kwargs)
        self.client_socket = socket
        self.cols = 1
        self.rows = 3
        self.add_widget(Label(text="Codewords"))

        self.add_widget(Button(text="Join Private Lobby", on_press=self.open_private))
        self.add_widget(Button(text="Join Public Lobby", on_press=self.open_public))
        self.name_input = None
        self.room_id_input = None
        self.popup = None

    def scrub(self):
        self.popup.dismiss()

    def open_private(self, instance):
        self.popup = Popup(title="Private Lobby")
        self.popup.size = (40, 40)

        content = GridLayout()
        self.popup.content = content
        content.cols = 2
        content.rows = 3


        self.name_input = TextInput(multiline=False)
        content.add_widget(Label(text="Name:"))
        content.add_widget(self.name_input)

        self.room_id_input = TextInput(multiline=False)
        content.add_widget(Label(text="Room Code:"))
        content.add_widget(self.room_id_input)

        content.add_widget(Button(text="Back", on_press=self.popup.dismiss))

        # send name and room id to server to join lobby
        content.add_widget(Button(text="Join Private Lobby",
                                  on_press=lambda event:
                                  send_msg(self.client_socket, Message(TAG='LOBBYREQUEST', name=self.name_input.text, roomid=self.room_id_input.text))))


        self.popup.open()

    def open_public(self, instance):
        self.popup = Popup(title="Public Lobby")
        content = GridLayout()
        self.popup.content = content
        content.cols = 2
        content.rows = 2
        content.add_widget(Label(text="Name:"))

        self.name_input = TextInput(multiline=False)
        content.add_widget(self.name_input)
        content.add_widget(Button(text="Back", on_press=self.popup.dismiss))

        # send name to server for verification when clicked
        content.add_widget(Button(text="Join Public Lobby",
                                  on_press=lambda event:
                                  send_msg(self.client_socket, Message(TAG='LOBBYREQUEST', name=self.name_input.text))))

        self.popup.open()

class Lobby(GridLayout):
    def __init__(self, socket, **kwargs):
        super(Lobby, self).__init__(**kwargs)
        self.client_socket = socket
        self.cols = 1
        self.rows = 5
        self.label = Label(text="Lobby")
        self.add_widget(self.label)
        self.role_table = GridLayout()
        self.role_table.cols = 2
        self.role_table.rows = 4
        self.add_widget(self.role_table)

        self.switch_button = Button(text="Switch Team",
                                    on_press = lambda event:
                                    send_msg(self.client_socket, Message(TAG='SWITCHTEAM')))
        self.add_widget(self.switch_button)


        self.codemaster_button = Button(text="Become Codemaster",
                                        on_press=lambda event:
                                        send_msg(self.client_socket, Message(TAG='CHOOSECODEMASTER')))
        self.add_widget(self.codemaster_button)

        # send request to join game
        self.start_button = Button(text="Start Game",
                                   on_press=lambda event:
                                   send_msg(self.client_socket, Message(TAG='STARTGAME')))

        self.add_widget(self.start_button)
    def change_team(self,color_int):
        color = None
        if color_int == 1:
            color = (1, 0, 0, 1)
        elif color_int == 0:
            color = (0, 0, 1, 1)
        elif color_int == -1:
            color = (0.5, 0.5, 0.5, 0.5)
        else:
            color = (1, 1, 1, 1)
        with self.label.canvas:
            print(color)
            Color(color[0],color[1],color[2],color[3])
            Rectangle(pos=self.label.pos, size=self.label.size)
    def codemaster(self,bool):
        if(bool):
            self.codemaster_button.text="Become player"
        else:
            self.codemaster_button.text = "Become Codemaster"

class GameGUI(GridLayout):
    def __init__(self, socket, board_dims, is_turn, **kwargs):
        super(GameGUI, self).__init__(**kwargs)
        self.socket = socket
        self.cols = 2
        self.rows = 1

        self.left_side = GridLayout()
        self.left_side.cols = 1
        self.left_side.rows = 2
        self.word_board = WordBoard(self.socket, board_dims, is_turn)
        self.hint_area = HintArea()
        self.left_side.add_widget(self.word_board)
        self.left_side.add_widget(self.hint_area)
        self.add_widget(self.left_side)

        self.game_chat = GameChat(self.socket)
        self.game_chat.size_hint = (None, None)

        self.add_widget(self.game_chat)
        self.game_chat.width = self.game_chat.parent.width * 2
        self.game_chat.height = self.game_chat.parent.height * 8

        self.left_side.size = (self.left_side.parent.width, self.left_side.parent.height)


class WordBoard(GridLayout):
    # def __init__(self, board, is_turn, **kwargs):
    #     super(WordBoard, self).__init__(**kwargs)
    #     self.is_turn = is_turn
    #     self.cols = len(board.board[0])
    #     self.rows = len(board.board)
    #
    #     self.btn_board = []
    #     for i in range(self.cols):
    #         row = []
    #         for j in range(self.rows):
    #             b = Button(text="Word")
    #             row.append(b)
    #             self.add_widget(b)
    #         self.btn_board.append(row)

    # def __init__(self, socket, **kwargs):
    #     super(WordBoard, self).__init__(**kwargs)
    #     self.socket = socket
    #     self.is_turn = False
    #     self.cols = 5
    #     self.rows = 5
    #
    #     self.board = []
    #     for i in range(5):
    #         col = []
    #         for j in range(5):
    #             b = Button(text="Word")
    #             col.append(b)
    #             self.add_widget(b)
    #         self.board.append(col)
    #     # print(self.board)

    def __init__(self, socket, board, is_turn, **kwargs):
        super(WordBoard, self).__init__(**kwargs)
        self.socket = socket
        self.is_turn = is_turn
        self.cols = len(board[0])
        self.rows = len(board)
        self.btn_board = [(['temp'] * self.cols) for row in range(self.rows)]
        for i in range(self.rows):
            for j in range(self.cols):

                # if is player's team's turn, send move; if not, send None
                b = Button(text=board[i][j].word,
                           on_press=lambda event, i=i, j=j:
                           send_msg(self.socket, Message(TAG='GAMEREQUEST', move=(i, j))) if self.is_turn else None)

                self.add_widget(b)
                self.btn_board[i][j] = b
        self.update_board(board,False)

    # todo update board
    def update_board(self, board, switch_turns):
        if switch_turns:
            self.is_turn = not self.is_turn

        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col].selected:
                    color_int = board[row][col].color
                    color = None
                    if color_int == 1:
                        color = (1, 0, 0, 1)
                    elif color_int == 0:
                        color = (0, 0, 1, 1)
                    elif color_int == -1:
                        color = (0.5, 0.5, 0.5, 0.5)
                    else:
                        color = (1, 1, 1, 1)

                    self.btn_board[row][col].background_color = color

    # self.board[i][j].text = words[i][j]

class HintArea(GridLayout):
    def __init__(self, **kwargs):
        super(HintArea, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 1

        self.current_hint = Label(text="")
        self.add_widget(self.current_hint)

    def receive_hint(self, word, count):
        self.current_hint.text = word + ", " + str(count)

class GameChat(GridLayout):
    def __init__(self, socket, **kwargs):
        super(GameChat, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 2

        self.socket = socket

        self.chat_log = TextInput(multiline=True,readonly=True)
        self.add_widget(self.chat_log)
        self.message_bar = TextInput(multiline=True)
        self.message_area = GridLayout(rows=1,cols=2)
        self.message_area.add_widget(self.message_bar)
        self.message_button = Button(text="Send", on_press=self.chat)
        self.message_area.add_widget(self.message_button)
        self.add_widget(self.message_area)
    def display(self,msg):
        print("here")
        self.chat_log.text += (msg+"\n")

    # rough method to be attached to button or command for sending a message
    def chat(self, instance):
        # todo process whether it should be sent to team or everyone
        chat_msg = self.message_bar.text.strip()

        # one or more @ followed by a name would be sent as pchat
        # todo make a better regex for this
        if re.search(r'^(@[a-zA-Z0-9]+)+$', chat_msg):
            send_msg(self.socket, Message(TAG='PCHAT', text_message=chat_msg))
        else:
            send_msg(self.socket, Message(TAG='CHAT', text_message=chat_msg))
        self.message_bar.text=""


class FullGUI(GridLayout):
    def __init__(self, socket, **kwargs):
        super(FullGUI, self).__init__(**kwargs)
        self.socket = socket
        self.cols = 1
        self.rows = 1
        self.start_menu = StartMenu(socket)
        self.lobby = None
        self.gamegui = None
        self.add_widget(self.start_menu)

    def go_to_lobby(self):
        self.start_menu.scrub()
        self.remove_widget(self.start_menu)
        self.lobby = Lobby(self.socket)
        self.add_widget(self.lobby)
        self.do_layout()

    def go_to_game(self, board, is_turn):
        self.remove_widget(self.lobby)
        self.gamegui = GameGUI(self.socket, board, is_turn)
        self.add_widget(self.gamegui)
        self.do_layout()

    def return_to_lobby(self):
        self.remove_widget(self.gamegui)
        self.start_menu = StartMenu(self.socket)
        self.add_widget(self.start_menu)


def send_msg(socket, msg):
    time.sleep(0.01)
    # serialize message
    serialized_msg = pickle.dumps(msg)
    # get size (represented as int 8 bytes) of message in bytes
    size_of_msg = sys.getsizeof(serialized_msg)
    # serialize the integer into a 8 byte byte stream, most significant bit first
    data_size = size_of_msg.to_bytes(8, 'big')
    # send the size of the data
    socket.sendall(data_size)
    # send data
    socket.sendall(serialized_msg)

