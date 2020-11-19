import socketio

# create a Socket.IO server
sio = socketio.Server()

print(sio)

@sio.event
def my_event(sid, data):
    print(data)

