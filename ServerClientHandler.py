from threading import Thread
import pickle
import socket
import sys
from Message import *
import re


class ServerClientHandler(Thread):

    # list of other clients in the room, as well as the clientconnectiondata for this individual client
    def __init__(self, client, server):
        super(ServerClientHandler, self).__init__()
        self.MAXPLAYERS = 8
        self.client_list = None
        self.room = None
        self.client = client
        self.board = None
        self.server = server
        self.clued = False

    def broadcast(self,msg,team):
        print(msg.TAG)
        for recipient in self.client_list:
            if(not team or (team and self.client.team == recipient.client.team)):
                recipient.send_msg(msg)

    def pchatprep(self,request):
        msg = request.text_message
        loc = msg.rfind("@")
        for i in range(loc,len(request)):
            if( msg[i]==' '):
                msg = request.text_message[0:i]
                request.text_message = self.client.name +" "+ request.text_message[i:]
                break
        recipients = [x.strip() for x in msg.split("@").strip()]
        recipients.append(self.client.name)
        return recipients

    def privatebroadcast(self,recipients,message):
        for recipient in self.client_list:
            if(recipient.client.name in recipients):
                recipient.send_msg(message)

    def send_msg(self,msg):
        # serialize message
        serialized_msg = pickle.dumps(msg)
        # get size (represented as int 8 bytes) of message in bytes
        size_of_msg = sys.getsizeof(serialized_msg)
        # serialize the integer into a 8 byte byte stream, most significant bit first
        data_size = size_of_msg.to_bytes(8, 'big')
        # send the size of the data
        self.client.socket.sendall(data_size)
        # send data
        self.client.socket.sendall(serialized_msg)

    def maketurn(self,turn):
        # print(str(turn[0])+" "+str(turn[1]))

        if(self.board.board[turn[0]][turn[1]].selected):
            return

        self.board.board[turn[0]][turn[1]].selected = True
        if(self.board.board[turn[0]][turn[1]].color != self.client.team):
            self.board.turn = (1,0)[self.board.turn==1]
            self.clued = False

        msg = Message(TAG="BOARDUPDATE", board=self.board)
        self.broadcast(msg, False)

        # todo win code
        # if (self.board.board[turn[0]][turn[1]].color == -2):
        #     msg = Message(TAG="WIN", text_message=((self.client.team+1)%2))
        #     self.broadcast(msg, False)
        #
        # Win = True
        # for i in range(self.board.dim):
        #     if(not Win):
        #         break
        #     for j in range(self.board.dim):
        #         if(self.board.board[i][j].selected == False and self.board.board[i][j].color==self.client.team):
        #             Win=False
        #             break
        #
        # if(Win):
        #     msg = Message(TAG="WIN",text_message=self.client.team)
        #     self.broadcast(msg, False)


    def get_msg(self):
        # get size of the incoming message
        size = self.client.socket.recv(8)

        # turn the byte stream into an integer
        data_size = int.from_bytes(size, 'big')

        # read the corresponding number of bits
        data = self.client.socket.recv(data_size)

        # reconstitute message from bytes
        request = pickle.loads(data)

        return request

    def run(self):
        try:
            print('i am here ')
            # naming portion

            # name_msg = Message(TAG="SUBMITNAME")
            # self.send_msg(name_msg)

            # listening loop
            while(True):
                # this may need to be locked as it may not be thread safe

                request = self.get_msg()
                print('msg received: ' + request.TAG)
                if request.TAG == "JOIN":
                    # this function should be locked
                    #self.send_msg(Message(TAG='GOTOLOBBY'))

                    info, self.room = self.server.join_make_room(self, request.text_message)
                    self.client_list = info[0]
                    self.board = info[1]

                    self.send_msg(Message(TAG='GOTOLOBBY'))

                    # log on server
                    if request.text_message is None:
                        print(request.name + ' has joined public room.')
                    else:
                        print(request.name + ' had joined private room ' + request.text_message + '.')

                    continue

                elif request.TAG=="CHAT":
                    print('chat received: ' + request.text_message)
                    self.broadcast(request,False)

                elif request.TAG == "TEAMCHAT":
                    self.broadcast(request,True)

                elif request.TAG == "PCHAT":
                    recipients = self.pchatprep(request)
                    self.privatebroadcast(recipients,request)

                elif request.TAG == "CHOOSETEAM":
                    if(self.client.team != request.text_message):
                        self.client.is_codemaster = False
                    self.client.team = request.text_message

                    self.send_msg(Message(TAG='TEAMSELECTED', text_message=self.client.team))

                elif request.TAG == "CHOOSECODEMASTER":
                    # todo team is a number right? + check for teamates?
                    if not self.client.is_codemaster and self.client.team is not None:
                        self.client.is_codemaster = True


                elif request.TAG == 'STARTGAME':
                    # distribute initial board
                    # todo randomize start team
                    self.send_msg(Message(TAG='STARTGAME', board=self.board, text_message=True))

                # todo perhaps consider renaming this
                elif request.TAG == "GAMEREQUEST":
                    print(request.move)
                    #if (self.board.turn == self.client.team and not self.client.is_codemaster):
                    self.maketurn(request.move)

                elif request.TAG == "CLUE":
                    if self.client.is_codemaster and self.board.turn == self.client.team and not self.clued:
                        self.clued = True
                        msg = Message(TAG="CLUE",text_message=request.text_message)
                        self.broadcast(msg,False)

                elif request.TAG == "LEAVE":
                    # this function should be locked
                    self.server.leave_room(self.client, self.room)


                # send their accepted name and send back the id if valid
                elif request.TAG == 'LOBBYREQUEST':
                    # todo
                    requested_name = request.name
                    if len(requested_name) > 3 and re.search(r'^[a-zA-Z0-9]*$', requested_name):
                        print(request.name)
                        # public room
                        if request.roomid is None:
                            self.send_msg(Message(TAG='ALLOWJOINGAME', name=requested_name))

                        # private room
                        else:
                            room_id = request.roomid
                            self.send_msg(Message(TAG='ALLOWJOINGAME', name=requested_name, roomid=room_id))

                    # invalid name
                    else:
                        # todo, how will errors be handled?
                        self.send_msg(Message(TAG='ERROR', text_message='name must be alphanumeric and at least length 4'))




        except socket.error:
            print('error: ' + str(self.client.ip_address) + ' leaving room')
            x = self.server.leave_room(self, self.room)
            if x:
                print(str(self.client.ip_address)+" Exited successfully")
            else:
                print(str(self.client.ip_address)+" Failed to exit room")
                print("shutting down connection")
            return

        return
