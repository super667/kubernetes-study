#!/usr/bin/env python3
 
import logging
import time
import os
 
 
 
logger = logging.getLogger("network-server")
 
 
def InitLog(program="server"):
    logger.setLevel(logging.DEBUG)
 
    # step 2: create a handler, write log into file.
    rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
    log_path = os.path.join(os.getcwd(), "Logs")
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_name = program + '-' + rq + '.log'
    log_file = os.path.join(log_path, log_name)
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
 
    # step 3: define the output format of handler
    formater = logging.Formatter("%(asctime)s-%(filename)s[line:%(lineno)d] - %(levelname)s:%(message)s")
    fh.setFormatter(formater)
    ch.setFormatter(formater)
 
    # step 4: add logger into handler
    logger.addHandler(fh)
    logger.addHandler(ch)
 
def Logtest():
    InitLog()
    logger.debug('this is a logger debug message')
    logger.info('this is a logger info message')
    logger.warning('this is a logger warning message')
    logger.error('this is a logger error message')
    logger.critical('this is a logger critical message')
 
 
if __name__ == "__main__":
    Logtest()