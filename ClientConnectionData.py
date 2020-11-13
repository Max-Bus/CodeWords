class ClientConnectionData:

    def __init__(self, socket, input_stream, output_stream, name):
        self.socket = socket
        self.input = input_stream
        self.output_stream = output_stream
        self.ip_address = name

        self.username = None
        self.team = None
        self.is_codemaster = False

