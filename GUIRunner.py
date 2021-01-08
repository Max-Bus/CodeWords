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
        self.padding = (100, 100, 100, 100)
        self.spacing = 10
        self.add_widget(Label(text="Codewords"))

        self.private_button = Button(text="Join Private Lobby", on_press=self.open_private)
        self.add_widget(self.private_button)
        self.public_button = Button(text="Join Public Lobby", on_press=self.open_public)
        self.public_button.padding = (10, 10)
        self.add_widget(self.public_button)

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
        content.padding = 100

        self.name_input = TextInput(multiline=False)
        self.name_label = Label(text="Name:")
        content.add_widget(self.name_label)
        content.add_widget(self.name_input)
        

        self.room_id_input = TextInput(multiline=False)
        self.room_label = Label(text="Room Code:")
        content.add_widget(self.room_label)
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
        content.padding = 100
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

        self.red_names = []
        self.blue_names = []

        self.participant_area = GridLayout(rows=1, cols=2)
        self.red_participants = Label(text="\nRED\n")
        self.participant_area.add_widget(self.red_participants)
        self.blue_participants = Label(text="\nRED\n")
        self.participant_area.add_widget(self.blue_participants)
        self.add_widget(self.participant_area)

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

    # todo remove participant


    def readd_all_participants(self, name_str):
        self.red_names = []
        self.blue_names = []

        for name in name_str.split(','):
            team = int(name.split(':')[0])

            if team == 1:
                self.red_names.append(name.split(':')[1])
            elif team == 0:
                self.blue_names.append(name.split(':')[1])

        self.update_participants()

    # redraws the names (in case of team switch etc.)
    def update_participants(self):
        redtxt = '\nRED\n'
        bluetxt = '\nBLUE\n'

        print(self.red_names)
        for person in self.red_names:
            redtxt += person + '\n'

        for person in self.blue_names:
            bluetxt += person + '\n'

        self.red_participants.text = redtxt
        self.blue_participants.text = bluetxt

    def change_team(self, color_int):
        # color int is equivalent to team number

        # adjust color
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

    # when people change teams, swap their names
    def adjust_teams(self, name, team_num):
        possible_names = [name, name + ' (you)', name + ' (you) (cm)']
        for n in possible_names:
            try:
                if team_num == 0:
                    # switching to blue
                    self.red_names.remove(n)
                    self.blue_names.append(n)
                elif team_num == 1:
                    # switching to red
                    self.blue_names.remove(n)
                    self.red_names.append(n)

                break
            except:
                continue

        self.update_participants()


    def codemaster(self,bool):
        if(bool):
            self.codemaster_button.text="Become player"
        else:
            self.codemaster_button.text = "Become Codemaster"

class GameGUI(GridLayout):
    def __init__(self, socket, board_dims, is_codemaster, **kwargs):
        super(GameGUI, self).__init__(**kwargs)
        self.socket = socket
        self.cols = 2
        self.rows = 1

        self.left_side = GridLayout()
        self.left_side.cols = 1
        self.left_side.rows = 2
        self.word_board = WordBoard(self.socket, board_dims, is_codemaster)
        self.word_board.size_hint = (1, 0.7)
        self.hint_area = HintArea()
        self.hint_area.size_hint = (1, 0.3)
        self.left_side.add_widget(self.word_board)
        self.left_side.add_widget(self.hint_area)
        self.left_side.size_hint = (0.6, 1)
        self.add_widget(self.left_side)

        self.game_chat = GameChat(self.socket)
        self.game_chat.size_hint = (0.4, 1)

        self.add_widget(self.game_chat)

    def win_lose(self,win):
        self.popup = Popup(title="Private Lobby")
        self.popup.size = (40, 40)

        content = GridLayout()
        self.popup.content = content
        content.cols = 1
        content.rows = 2
        result = "LOSE"
        if(win):
            result="WIN"

        content.add_widget(Label(text="YOU "+result))

        content.add_widget(Button(text="Back", on_press=self.popup.dismiss))

        self.popup.open()

class WordBoard(GridLayout):

    def __init__(self, socket, board, is_codemaster, **kwargs):
        super(WordBoard, self).__init__(**kwargs)
        self.socket = socket
        self.cols = len(board[0])
        self.rows = len(board)
        self.btn_board = [(['temp'] * self.cols) for row in range(self.rows)]
        for i in range(self.rows):
            for j in range(self.cols):

                # if is player's team's turn, send move; if not, send None
                b = Button(text=board[i][j].word,
                           on_press=lambda event, i=i, j=j:
                           send_msg(self.socket, Message(TAG='GAMEREQUEST', move=(i, j))))

                self.add_widget(b)
                self.btn_board[i][j] = b
        self.update_board(board, is_codemaster)

    # todo update board
    def update_board(self, board, is_codemaster):

        opacity = 1
        if(is_codemaster):
            opacity = 0.5

        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col].selected:
                    color_int = board[row][col].color
                    color = None
                    if color_int == 1:
                        color = (1, 0, 0.25, opacity)
                    elif color_int == 0:
                        color = (0.25, 0, 1, opacity)
                    elif color_int == -1:
                        color = (0.5, 0.5, 0.75, opacity)
                    else:
                        color = (0.25, 0.75, 0.25, opacity)

                    self.btn_board[row][col].background_color = color

    # self.board[i][j].text = words[i][j]

class HintArea(GridLayout):
    def __init__(self, **kwargs):
        super(HintArea, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 1
        self.blues_turn = -1

        self.current_hint = Label(text="", markup=True)
        self.add_widget(self.current_hint)

    def receive_hint(self, word, count):
        self.current_hint.text = word + ", " + str(count)
        if (self.blues_turn):
            self.current_hint.text = "[color=#8888ff]" + word + ", " + str(count) + "[/color]"
        else:
            self.current_hint.text = "[color=#ff8888]" + word + ", " + str(count) + "[/color]"

    def prompt_hint(self, name, blues_turn):
        self.blues_turn = blues_turn
        if (blues_turn):
            self.current_hint.text = "[color=#8888ff]" + name + "'s turn to give a hint.[/color]"
        else:
            self.current_hint.text = "[color=#ff8888]" + name + "'s turn to give a hint.[/color]"

class GameChat(GridLayout):
    def __init__(self, socket, **kwargs):
        super(GameChat, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 3
        self.socket = socket

        self.participant_area = GridLayout(rows=1, cols=2)
        self.red_participants = Label(text="\nRED\n", halign='center', valign='middle')
        self.participant_area.add_widget(self.red_participants)
        self.blue_participants = Label(text="\nBLUE\n", halign='center', valign='middle')
        self.participant_area.add_widget(self.blue_participants)
        self.participant_area.size_hint = (1, 0.3)
        self.add_widget(self.participant_area)

        self.chat_log = TextInput(multiline=True, readonly=True)
        self.chat_log.size_hint = (1, 0.65)
        self.add_widget(self.chat_log)

        self.message_area = GridLayout(rows=1, cols=3)

        self.pass_button = Button(text="Pass",
                                    on_press = lambda event:
                                    send_msg(self.socket, Message(TAG='PASS')))
        self.pass_button.size_hint = (0.15, 1)
        self.message_area.add_widget(self.pass_button)

        self.message_bar = TextInput(multiline=False)
        self.message_bar.size_hint = (0.7, 1)
        self.message_area.add_widget(self.message_bar)

        self.message_button = Button(text="Send", on_press=self.chat)
        self.message_button.size_hint = (0.15, 1)
        self.message_area.add_widget(self.message_button)

        self.message_area.size_hint = (1, 0.05)
        self.add_widget(self.message_area)

    def display(self, msg):
        print("here")
        self.chat_log.text += msg + "\n"

    def update_participants(self, names_str):
        # [team num]:name1,[team num]:name2,[team num]:name3....

        # add names to display label
        for name in names_str.split(','):
            team = int(name.split(':')[0])

            if team == 1:
                self.red_participants.text += name.split(':')[1] + '\n'
            elif team == 0:
                self.blue_participants.text += name.split(':')[1] + '\n'

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
        if (self.gamegui is not None) :
            self.remove_widget(self.gamegui)
        self.lobby = Lobby(self.socket)
        self.add_widget(self.lobby)
        self.do_layout()

    def go_to_game(self, board, is_codemaster):
        self.remove_widget(self.lobby)
        self.gamegui = GameGUI(self.socket, board, is_codemaster)
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

