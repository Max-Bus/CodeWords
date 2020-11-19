class Message:
    def __init__(self,TAG = None,text_message = None,board =None,clients=None):
        self.TAG = TAG
        self.text_message = text_message
        self.board = board
        self.clients = clients
