class Message:
    def __init__(self,TAG=None,text_message=None, name=None, move=None,board=None,clients=None, roomid=None):
        self.TAG = TAG
        self.text_message = text_message
        self.move = move
        self.board = board
        self.clients = clients
        self.name = name
        self.roomid = roomid
