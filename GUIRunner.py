import kivy
import threading
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

class Lobby(GridLayout):
    def __init__(self, **kwargs):
        super(Lobby, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 3
        self.add_widget(Label(text="Codewords"))
        self.add_widget(Button(text="Join Private Lobby", on_press=self.open_private))
        self.add_widget(Button(text="Join Public Lobby", on_press=self.open_public))

    def open_private(self, instance):
        popup_window = Popup(title="Private Lobby")
        popup_window.size = (40, 40)

        content = GridLayout()
        popup_window.content = content
        content.cols = 2
        content.rows = 3
        content.add_widget(Label(text="Name:"))
        content.add_widget(TextInput(multiline=False))
        content.add_widget(Label(text="Room Code:"))
        content.add_widget(TextInput(multiline=False))
        content.add_widget(Button(text="Back", on_press=popup_window.dismiss))
        content.add_widget(Button(text="Join Private Lobby"))

        popup_window.open()

    def open_public(self, instance):
        popup_window = Popup(title="Public Lobby")

        content = GridLayout()
        popup_window.content = content
        content.cols = 2
        content.rows = 2
        content.add_widget(Label(text="Name:"))
        content.add_widget(TextInput(multiline=False))
        content.add_widget(Button(text="Back", on_press=popup_window.dismiss))
        content.add_widget(Button(text="Join Public Lobby"))

        popup_window.open()

class GameGUI(GridLayout):
    def __init__(self, **kwargs):
        super(GameGUI, self).__init__(**kwargs)
        self.cols = 2
        self.rows = 1

        self.left_side = GridLayout()
        self.left_side.cols = 1
        self.left_side.rows = 2
        self.word_board = WordBoard()
        self.hint_area = HintArea()
        self.left_side.add_widget(self.word_board)
        self.left_side.add_widget(self.hint_area)
        self.add_widget(self.left_side)

        self.game_chat = GameChat()
        self.game_chat.size_hint = (None, None)

        self.add_widget(self.game_chat)
        self.game_chat.width = self.game_chat.parent.width * 2
        self.game_chat.height = self.game_chat.parent.height * 8

        self.left_side.size = (self.left_side.parent.width, self.left_side.parent.height)

class WordBoard(GridLayout):
    def __init__(self, **kwargs):
        super(WordBoard, self).__init__(**kwargs)
        self.cols = 5
        self.rows = 5

        self.board = []
        for i in range(5):
            col = []
            for j in range(5):
                b = Button(text="Word")
                col.append(b)
                self.add_widget(b)
            self.board.append(col)
        print(self.board)

    def set_words(self, words):
        for i in range(5):
            for j in range(5):
                self.board[i][j].text = words[i][j]

class HintArea(GridLayout):
    def __init__(self, **kwargs):
        super(HintArea, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 2

        self.current_hint = Label(text="country, 2")
        self.add_widget(self.current_hint)

    def receive_hint(self, word, count):
        self.current_hint.text = word + ", " + str(count)

class GameChat(GridLayout):
    def __init__(self, **kwargs):
        super(GameChat, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 2

        self.chat_log = TextInput(multiline=True)
        self.add_widget(self.chat_log)
        self.message_bar = TextInput(multiline=True)
        self.add_widget(self.message_bar)

class FullGUI(GridLayout):
    def __init__(self, **kwargs):
        super(FullGUI, self).__init__(**kwargs)
        self.cols = 1
        self.rows = 1
        self.lobby = Lobby()
        self.add_widget(self.lobby)

    def go_to_game(self):
        self.remove_widget(self.lobby)
        self.gamegui = GameGUI()
        self.add_widget(self.gamegui)

    def return_to_lobby(self):
        self.remove_widget(self.gamegui)
        self.lobby = Lobby()
        self.add_widget(self.lobby)

class GUIRunner(App):
    def __init__(self):
        super(GUIRunner, self).__init__()
        self.fullgui = FullGUI()

    def build(self):
        return self.fullgui

if __name__ == "__main__":
    gui = GUIRunner()
    gui.run()