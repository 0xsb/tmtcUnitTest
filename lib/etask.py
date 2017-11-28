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


class etask:
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
                #if add stdout=subprocess.PIPE, output will not be printing in thread
                self.sp = subprocess.Popen(shlex.split(self.cmd), stderr=subprocess.PIPE)
                fd = self.sp.stderr.fileno()
                self.fds2procs[fd] = self.sp
                self.poller.register(fd, select.EPOLLHUP)
                #start thread to wait
                self.wait = threading.Thread(target=self.waiter)
                print 'cmd is ' + self.cmd
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
            self.logger.logger.error(self.cmd + " " + str(self.curindex) + ' time')
            time.sleep(2)
        self.checkResult()

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
                stdout, stderr = curproc.communicate()
                #actually poll already done, so no output.
                #self.logger.logger.info('stdout is '.format(stdout))
                #self.logger.logger.info('stderr is '.format(stderr))

                #returncode needed to be set by communicate
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


    def checkResult(self):
        for index, result in enumerate(self.returncode):
            if result == 0:
                self.logger.logger.info('<' + self.cmd + '> executed sucessfully.')
                return True
            if result != 0:
                excstr = '<' + self.cmd + '> ' + str(index+1) + ' time, return code is ' + str(result)
                self.logger.logger.error(excstr)
                raise TaskException(excstr)

if __name__ == '__main__':

    def testadb():
        adbroot = "adb root"
        t = etask(cmd=adbroot, timeout=5, retry=3)
        t.run()
        print t.returncode

        adbremount = "adb remount"
        t = etask(cmd=adbremount, timeout=3, retry=3)
        t.run()
        print t.returncode

    def testls():
        lscmd = "ls -l"
        t = etask(cmd=lscmd, timeout=None)
        t.run()
        print lscmd+ " is " + str(t.returncode)

    def testsleep():
        sleep = "sleep 30"
        t = etask(cmd=sleep, timeout=3)
        t.run()
        print sleep + ' is ' + str(t.returncode)
        if abs(t.returncode[0]) == signal.SIGUSR1:
            print 'get SIGUSR1'

    def testnotexist():
        cmdnotexist = "abc "
        t = etask(cmd=cmdnotexist, timeout=3)
        t.run()
        print cmdnotexist + ' is ' + str(t.returncode)

    def testsleepretry():
        sleep = "sleep 30"
        t = etask(cmd=sleep, timeout=38, retry=2)
        t.run()
        print t.returncode

    try:
        #SIGUSR1 will happen , return code should be negetive, SIGUSR1
        testls()
        #testsleep()
        #testls()
        testadb()
    except:
        etype = sys.exc_info()[0]
        evalue = sys.exc_info()[1]
        print "Unexpected error: " + str(etype) + ' ' + str(evalue)