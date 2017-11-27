#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

"""
1. this class is used to create a process
2. process timeout will be checked, send SIGUSR1 if timeout
3. process returncode will be checked
"""
import select
import os
import sys
import subprocess
import shlex
from logConf import *
import threading
import signal
import time

class TaskException(Exception):
    def __init__(self, message):
        super(TaskException, self).__init__(message)
        self.message = message


class task:
    def __init__(self, cmd='', timeout=None, retry=1):
        """

        :param cmd:
        :param timeout:
        :param retry:
        :return:
        """
        self.cmd = cmd
        self.timeout = timeout
        self.retry = retry
        self.logger = logConf()
        self.poller = select.epoll()
        self.fds2procs = dict()
        self.wait = None
        #returncode should be a list too
        self.curindex = 0
        self.returncode = [-1024] * retry

    def run(self):
        #start the real task
        for index in range(1, self.retry+1):
            try:
                self.sp = subprocess.Popen(shlex.split(self.cmd), stdout=open(os.devnull, 'wb'), stderr=subprocess.PIPE)
                fd = self.sp.stderr.fileno()

                self.fds2procs[fd] = self.sp
                self.poller.register(fd, select.EPOLLHUP)
                #start thread to wait
                self.wait = threading.Thread(target=self.waiter)
                self.wait.setDaemon(True)
                self.wait.start()
                self.getResult()
            except:
                etype = sys.exc_info()[0]
                evalue = sys.exc_info()[1]
                self.logger.logger.info("Unexpected error: " + str(etype) + ' ' + str(evalue))

            #check task exit code
            if self.returncode[self.curindex] == 0:
                break
            self.curindex = self.curindex + 1

    def waiter(self):
        """
        check the return code
        :return:
        """
        pairs = self.poller.poll()
        self.logger.logger.info("recv hangup {}".format(pairs))
        for fd, status in pairs:
            if self.fds2procs:
                curproc = self.fds2procs[fd]
                streamdata = curproc.communicate()[0]
                self.returncode[self.curindex] = curproc.returncode
            else:
                raise TaskException("fds2procs None.")


    def getResult(self):
        """
        thread timeout and send signal
        :return:
        """
        if self.wait:
            if self.wait.is_alive():
                #this timeout is
                self.wait.join(self.timeout)
                if self.wait.is_alive():
                    self.sp.send_signal(signal.SIGUSR1)
                    #just wait
                    self.wait.join(timeout=1)

                #pysipp still retry three times, we add one more time
                if self.wait.is_alive():
                    self.sp.send_signal(signal.SIGUSR1)

                    if self.wait.is_alive():
                        #raise exception
                        raise RuntimeError("Unable to kill cmd: " + self.cmd)




if __name__ == '__main__':
    lscmd = "ls -l"
    #SIGUSR1 will happen , return code should be negetive, SIGUSR1
    sleep = "sleep 30"
    cmdnotexist = "abc "
    t = task(cmd=lscmd, timeout=None)
    t.run()
    print lscmd+ " is " + str(t.returncode)
    t = task(cmd=sleep, timeout=3)
    t.run()
    print sleep + ' is ' + str(t.returncode)
    if abs(t.returncode[0]) == signal.SIGUSR1:
        print 'get SIGUSR1'
    t = task(cmd=cmdnotexist, timeout=3)
    t.run()
    print cmdnotexist + ' is ' + str(t.returncode)

    adbroot = "adb root"
    """
    t = task(cmd=sleep, timeout=38, retry=2)
    t.run()
    print t.returncode
    """
    t = task(cmd=adbroot, timeout=5, retry=3)
    t.run()
    print t.returncode

