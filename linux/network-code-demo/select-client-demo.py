import socket
from time import sleep
messages = ['this is the message', "it will be sent", "in parts", "finish!"]
server_address = ('localhost', 8090)
 
socks = [socket.socket(socket.AF_INET, socket.SOCK_STREAM),
         socket.socket(socket.AF_INET, socket.SOCK_STREAM)]
 
for s in socks:
    s.connect(server_address)
    s.setblocking(True)
 
for index, message in enumerate(messages):
    for s in socks:
        s.send(message.encode("utf-8"))
        data = s.recv(1024)
        print("received data: %s" % data)
        sleep(2)
        if data == b"finish!":
            print("closed")
            s.close()