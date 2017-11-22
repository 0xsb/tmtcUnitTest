#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

"""
write a class to check if process is timeout
check the returncode

1. start to process to execute
2. start thread to check if process is ended by checking the SIGHUP and return code
3. join with timeout,  time fires up, send SIGUSR1 to end process

"""

import subprocess
import os
import sys
import select
import threading
import signal

DEVNULL = open(os.devnull, 'wb')
#user will kill it
#process=subprocess.Popen(["sleep", "1000"],stdout=DEVNULL,stderr=subprocess.PIPE)

#emulate error code 2
process=subprocess.Popen(["ls", "1000"],stdout=DEVNULL,stderr=subprocess.PIPE)

#emulate sipp timeout
#process=subprocess.Popen(["adb", "shell", "sipp", "-sf", "/data/data/ut/reg.xml", "-p", "5060", "-t","u1", "-m", "1", "-trace_err"], stdout=DEVNULL,stderr=subprocess.PIPE)

epoll=select.epoll()

fds2procs = dict()
fd = process.stderr.fileno()
print 'fd is ' + str(fd)
fds2procs[fd] = process
#listen on stderr's EPOLLHUP event
epoll.register(fd, select.EPOLLHUP)

#start a thread to check the
def checkStatus():
    pairs = epoll.poll()
    print 'recv hangup {}'.format(pairs)
    for fd, status in pairs:
        if fds2procs:
            curproc = fds2procs[fd]
            #get subprocess return code
            streamdata = curproc.communicate()[0]
            if curproc.returncode != 0 :
                print 'return code is ' + str(curproc.returncode)
        else:
            print 'it is impossible that '

worker = threading.Thread(target=checkStatus)
worker.setDaemon(True)
worker.start()

timeout=10
worker.join(timeout)
if worker.is_alive():
    print 'worker alive, send SIGUSR1'
    process.send_signal(signal.SIGUSR1)
else:
    print 'worker died...'



