import select
import socket
import queue
from time import sleep
 
# 创建一个TCP/IP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(True)
 
# Bind the socket to the port
server_address = ('localhost', 8090)
print("starting up on '%s' port %s" % server_address)
server.bind(server_address)
 
# listen for incoming connections
server.listen(10)
# sockets from which we expect to read
inputs = [server]
 
# sockets to which we expect to read
outputs = []
 
# outgoing message queues
message_queues = {}
client_addresses = {}
while inputs:
    # 开始select监听，对input_list中的服务器端server进行监听
    # 一旦调用socket的send,recv函数，将会再次调用此模块
    readable, writeable, exceptional = select.select(inputs, outputs, inputs)
    for s in readable:
        # 判读当前触发的是不是服务器对象，当前触发的是服务器对象，说明有新的客户端连接进来了
        if s is server:
            # 服务器socket监听到可读，接受新的连接，
            connection, client_address = s.accept()
            # 将新的连接设置为非阻塞的方式
            connection.setblocking(False)
            # 将新的连接添加到可读的socket列表中
            inputs.append(connection)
            # 为新连接的客户创建一个消息队列，用来保存客户端发送的消息
            message_queues[connection] = queue.Queue()
            # 用一个字典来存储客户端的socket与ip地址的映射表
            client_addresses[connection] = client_address
 
        else:
            # 有老用户发送消息，处理接受
 
            data = s.recv(1024)
            if data != b'finish!':
                if data != b'':
                    print("receved %s from %s" % (data, s.getpeername()))
                    # 将收到的消息放入到相对应的socket客户端的消息队列中
                    message_queues[s].put(data)
                    # 如果需要进行回复操作，将相应的socket客户端放到outpus列表中，让select监听
                    if s not in outputs:
                        outputs.append(s)
            else:
                print(client_addresses[s])
                print("closing client:   %s:%s" % s.getpeername())
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()
                del message_queues[s]
 
    # Handle outputs
    # 如果现在没有客户端请求, 也没有客户端发送消息时, 开始对发送消息列表进行处理, 是否需要发送消息
    # 存储哪个客户端发送过消息
    for s in writeable:
        try:
            message_queue = message_queues.get(s)
            send_data = ''
            if message_queue is not None:
                send_data = message_queue.get_nowait()
            else:
                print("has closed")
        except queue.Empty:
            # print("%s" % s.getpeername())
            outputs.remove(s)
        else:
            if message_queue is not None:
                print("send data:", send_data)
                s.send(send_data)
            else:
                print("has colsed")
                
    # # Handle "exceptional conditions"
    # 处理异常的情况
    for s in exceptional:
        print("exception condition on %s" % s.getpeername())
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        del message_queues[s]
    sleep(1)