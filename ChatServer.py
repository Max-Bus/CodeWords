# i think this is like the executor from java
from concurrent.futures import ThreadPoolExecutor
from Room import Room

# class ChatServer:
#
#     def __init__(self):
#         pass

if __name__ == '__main__':
    # server = ChatServer()
    print('server started')

    # create thread, add it to the executor, and it runs? maybe theres a better way
    executor = ThreadPoolExecutor(max_workers=2)
    rm = Room(4)
    executor.submit(rm.run)


    while True:
        break

        # todo do connection stuff

        # todo execute each room in a different thread