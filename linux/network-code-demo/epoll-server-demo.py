#!/usr/bin/env python3
 
import socket
from common import logger
import select
import errno
from common import InitLog
 
 
 
def epoll_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    except socket.error as msg:
        logger.error("create socket failed!")
 
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as msg:
        logger.error("setsocketopt SO_REUSEADDR failed!")
 
    try:
        server.bind(("", 8090))
        logger.info("start up on %s:%d" % ("", 8090))
    except socket.error as msg:
        logger.error("bind failed!")
 
    try:
        server.listen(10)
    except socket.error as msg:
        logger.error(msg)
 
    try:
        epoll_fd = select.epoll()
        epoll_fd.register(server.fileno(), select.EPOLLIN)
    except socket.error as msg:
        logger.error(msg)
 
    connections = {}
    addresses = {}
    datalist = {}
    while True:
        epoll_list = epoll_fd.poll()
        for fd, events in epoll_list:
            if fd == server.fileno():
                conn, addr = server.accept()
                logger.debug("accept connection from %s, %d, fd=%d" % (addr[0], addr[1], conn.fileno()))
                conn.setblocking(0)
                epoll_fd.register(conn.fileno(), select.EPOLLIN | select.EPOLLET)
                connections[conn.fileno()] = conn
                addresses[conn.fileno()] = addr
            elif select.EPOLLIN & events:
                datas = ''
                while True:
                    try:
                        data = connections[fd].recv(10)
                        if not data and not datas:
                            epoll_fd.unregister(fd)
                            connections[fd].close()
                            logger.debug("%s, %d closed" % (addresses[fd][0], addresses[fd][1]))
                            break
                        else:
                            datas += data
                    except socket.error as msg:
                        if msg.errno == errno.EAGAIN:
                            logger.debug("%s receved %s" % (fd, datas))
                            datalist[fd] = datas
                            epoll_fd.modify(fd, select.EPOLLET | select.EPOLLOUT)
                            break
                        else:
                            epoll_fd.unregister(fd)
                            connections[fd].close()
                            logger.error(msg)
                            break
            elif select.EPOLLHUP & events:
                epoll_fd.unregister(fd)
                connections[fd].close()
                logger.debug("%s, %d closed" % (addresses[fd][0], addresses[fd][1]))
            elif select.EPOLLOUT & events:
                sendLen = 0
                while True:
                    sendLen += connections[fd].send(datalist[fd][sendLen:])
                    if sendLen == len(datalist[fd]):
                        break
                epoll_fd.modify(fd, select.EPOLLIN | select.EPOLLET)
            else:
                continue

 
    
 
if __name__ == '__main__':
    InitLog("server")
    epoll_server()
    a = [1,2,3]
    a.sort()
