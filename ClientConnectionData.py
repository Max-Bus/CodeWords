class ClientConnectionData:

    def __init__(self, socket, name):
        self.socket = socket
        self.ip_address = name

        self.username = None
        self.team = None
        self.is_codemaster = False

