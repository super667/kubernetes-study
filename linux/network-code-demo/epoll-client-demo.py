#!/bin/env python3

import socket
import time
from common import logger
from common import InitLog
 
InitLog("client")
 
try:
    conn_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
except socket.error as msg:
    logger.error(msg)
 
try:
    conn_fd.connect(("127.0.0.1", 8090))
    logger.debug("connect to network server success")
except socket.error as msg:
    logger.error(msg)
 
for i in range(1, 11):
    data = "The Number is %d" % i
    if conn_fd.send(data) != len(data):
        logger.error("send data to network server failed")
        break
    readdata = conn_fd.recv(1024)
    print(readdata)
    time.sleep(1)
conn_fd.close()