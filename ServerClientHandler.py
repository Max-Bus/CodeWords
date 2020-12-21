from threading import Thread
import pickle
import socket
import sys
from Message import *
import re
import random
import time


class ServerClientHandler(Thread):

    # list of other clients in the room, as well as the clientconnectiondata for this individual client
    def __init__(self, client, server):
        super(ServerClientHandler, self).__init__()
        self.MAXPLAYERS = 8
        self.client_list = None
        self.room = None
        self.client = client
        self.client.team = random.choice([0,1])
        print(str(self.client.team))
        self.board = None
        self.server = server
        self.clued = False
        self.boardClone = None

    def broadcast(self,msg,team):
        print(msg.TAG)
        if(msg.TAG=="CHAT"):
            print("hi")
            msg.text_message = self.client.name+": "+msg.text_message
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
        message.text_message = self.client.name+"(private): "+message.text_message
        for recipient in self.client_list:
            if(recipient.client.name in recipients):
                recipient.send_msg(message)

    def send_msg(self,msg):
        time.sleep(0.01)
        # serialize message
        serialized_msg = pickle.dumps(msg)
        # get size (represented as int 8 bytes) of message in bytes
        size_of_msg = sys.getsizeof(serialized_msg)
        # serialize the integer into a 8 byte byte stream, most significant bit first
        data_size = size_of_msg.to_bytes(8, 'big')
        # send the size of the data
        print(size_of_msg)
        self.client.socket.sendall(data_size)
        # send data
        self.client.socket.sendall(serialized_msg)

    def maketurn(self,turn):
        # print(str(turn[0])+" "+str(turn[1]))
        print(str(self.board.board[turn[0]][turn[1]].color))
        if(self.board.board[turn[0]][turn[1]].selected):
            return

        self.server.select(self.room,turn[0],turn[1])
        #self.board.board[][].selected = True


        winner = None
        if (self.board.board[turn[0]][turn[1]].color == -2):
            winner = ((self.board.turn+1)%2)
        Win = True
        for i in range(self.board.dim):
            for j in range(self.board.dim):
                if (self.board.board[i][j].selected == False and self.board.board[i][j].color == self.client.team):
                    Win = False
                    break
        if (Win):
            winner = self.client.team
        self.boardClone.board[turn[0]][turn[1]].color=self.board.board[turn[0]][turn[1]].color
        self.boardClone.board[turn[0]][turn[1]].selected = True
        msg = Message(TAG="BOARDUPDATE", board=self.boardClone,text_message=winner)
        self.broadcast(msg, False)

        if (self.board.board[turn[0]][turn[1]].color != self.client.team):
            self.server.turn(self.room)
            self.clued = False


    def get_msg(self):
        time.sleep(0.01)
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
                if (self.client.is_codemaster):
                    if(request.TAG=="CHAT" and not self.clued and self.board.turn == self.client.team):
                        request.TAG="CLUE"
                if request.TAG == "JOIN":
                    # this function should be locked
                    #self.send_msg(Message(TAG='GOTOLOBBY'))
                    self.client.team = random.choice([0,1])
                    info, self.room = self.server.join_make_room(self, request.text_message)
                    self.client_list = info[0]
                    self.board = info[1]
                    self.boardClone = self.board.copy()
                    print(self.boardClone.board)
                    for i in range(len(self.boardClone.board)):
                        for j in range(len(self.boardClone.board[i])):
                            if(not self.boardClone.board[i][j].selected):
                                self.boardClone.board[i][j].color=0
                    self.send_msg(Message(TAG='GOTOLOBBY',text_message=self.client.team))

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

                elif request.TAG == "SWITCHTEAM":
                    #if(self.client.team != request.text_message):
                    self.client.is_codemaster = False
                    #self.client.team = request.text_message
                    self.client.team = (1 + self.client.team) % 2
                    print("new team:"+str(self.client.team))
                    self.send_msg(Message(TAG='TEAMSELECTED', text_message=self.client.team))

                elif request.TAG == "CHOOSECODEMASTER":
                    # todo team is a number right? + check for teamates?
                    if(self.client.is_codemaster):
                        self.client.is_codemaster=False
                        self.send_msg(Message(TAG="CODEMASTER", text_message=False))
                    else:
                        team = True
                        for client in self.client_list:
                            print(client.client.team)
                            print(self.client.team)
                            if(client.client.team == self.client.team):
                                if(client.client.is_codemaster):
                                    team=False
                                    break

                        if team and not self.client.is_codemaster and self.client.team is not None:
                            self.client.is_codemaster = True
                            self.send_msg(Message(TAG="CODEMASTER", text_message=True))
                        else:
                            self.send_msg(Message(TAG="CODEMASTER",text_message=False))


                elif request.TAG == 'STARTGAME':
                    team_0_ready = False
                    team_1_ready = False
                    print(self.client_list)
                    for client in self.client_list:
                        if(client.client.is_codemaster):
                            if(client.client.team==0):
                                team_0_ready =True
                            else:
                                team_1_ready =True

                    if(team_0_ready and team_1_ready):
                        # distribute initial board
                        if (self.client.is_codemaster):
                            for i in range(len(self.board.board)):
                                for j in range(len(self.board.board[i])):
                                    self.boardClone.board[i][j].color = self.board.board[i][j].color
                                    self.boardClone.board[i][j].selected = True
                        self.broadcast(Message(TAG='STARTGAME', board=self.boardClone, text_message=True),False)

                # todo perhaps consider renaming this
                elif request.TAG == "GAMEREQUEST":
                    print(request.move)
                    if(self.client.team is None):
                        break
                    if (self.board.turn == self.client.team and not self.client.is_codemaster):
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
                        self.client.name=requested_name
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
