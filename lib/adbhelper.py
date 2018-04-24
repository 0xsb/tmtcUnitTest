#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

#https://stackoverflow.com/questions/30937829/how-to-get-both-return-code-and-output-from-subprocess-in-python
"""
1. adb root, adb remount
2. adb push libs and resource
2.1 currently use adb cmd, python-adb is optional

"""
from logConf import *
from etask import *

class adbException(Exception):
    def __init__(self, message):
        super(adbException, self).__init__(message)
        self.message = message

"""
adbhelper exec all cmd except adb shell
"""
class adbhelper:
    def __init__(self):
        #device init
        self.logger = logConf()

    def adbCmd(self, cmd='', timeout=None, retry=1):
        adbtask = None
        try:
            adbtask = etask(cmd=cmd, timeout=timeout, retry=retry)
            adbtask.run()
        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            estr = str(etype) + ' ' + str(evalue)
            self.logger.logger.info("Unexpected error: " + estr)

        #add checkResult if cmd failed, raise exception and exit!
        if adbtask:
            adbtask.checkResult()

    def initDevice(self):
        adbroot = "adb root"
        adbremount = "adb remount"
        self.adbCmd(adbroot, retry=3)
        self.adbCmd(adbremount, retry=3)

    def pull(self, destdir, localdir):
        adbpull = "adb pull -p -a " + destdir + ' ' + localdir
        self.adbCmd(adbpull)

    def push(self, filename, destdir):
        #adb push file dest
        adbpush = "adb push -p " + filename + ' ' + destdir
        self.adbCmd(adbpush)

    def mkdirp(self, filename):
        mkdirp = "adb shell mkdir -p " + filename
        self.adbCmd(mkdirp)


#TODO: adb shell need a special handler
# we do not need adb shell's exit code , but shell cmd's exit code
# so etask is not needed here.
#def adb_shell

#https://imsardine.wordpress.com/2012/06/05/android-adb-shell-exit-status/
def adb_shell(shell_cmds):
    #in case , so start a new line
    shell_cmds += '; echo -e \'\n\'$?'
    #NOTE: double quote is a MUST?
    cmds = ['adb', 'shell', shell_cmds]
    stdout = subprocess.Popen(cmds, stdout=subprocess.PIPE).communicate()[0].rstrip()

    lines = stdout.splitlines()
    print repr(stdout), lines
    retcode = int(lines[-1])
    if retcode != 0:
        errmsg = 'failed to execute ADB shell commands (%i)' % retcode
        if len(lines) > 1: errmsg += '\n' + '\n'.join(lines[:-1])
        raise RuntimeError(errmsg)
    return stdout


"""
run adb shell cmd with timeout and get cmd exit code
stdout: EPOLLHUP   break the loop and wait for timeout
stdout: POLLIN     readline
just write a class to copy etask, but add special handling to check shell exit

"""
class eadbshell:
    def __init__(self, cmd='', timeout=1):
        #manually print exit code, remove \n
        self.cmd = cmd + '; echo -e -n \'\n\'$?'
        self.timeout = int(timeout)
        self.logger = logConf()
        self.poller = select.epoll()
        self.wait = None

        #only cmd's exit code is useful
        self.cmdexit = -1


    def run(self):
        try:
            shellcmds = ['adb', 'shell', self.cmd]
            self.sp = subprocess.Popen(shellcmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdoutfd = self.sp.stdout.fileno()
            self.poller.register(stdoutfd, select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR)
            #self.poller.register(stderr, select.EPOLLHUP)
            self.wait = threading.Thread(target=self.waiter)
            self.wait.setDaemon(True)
            self.wait.start()
            self.getResult()

        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            self.logger.logger.info("Unexpected error: " + str(etype) + ' ,' + str(evalue))

        if self.cmdexit != 0:
            raise adbException(self.cmd + ' failed' )



    def waiter(self):
        while True:
            #non-blocking mode
            pairs = self.poller.poll(timeout=0)
            if len(pairs) != 0:
                #self.logger.logger.info(self.cmd + " recv events {}".format(pairs))
                for fd, status in pairs:
                    #add description about status
                    if status == select.POLLIN:
                        self.logger.logger.info(self.cmd + " fd "+ repr(fd) + "eadbshell recv POLLIN")
                    elif status == select.POLLPRI:
                        self.logger.logger.info(self.cmd + " fd "+ repr(fd) + "eadbshell recv POLLPRI")
                    elif status == select.POLLOUT:
                        self.logger.logger.info(self.cmd + " fd "+ repr(fd) + "eadbshell recv POLLOUT")
                    elif status == select.POLLERR:
                        self.logger.logger.info(self.cmd + " fd "+ repr(fd) + "eadbshell recv POLLERR")
                    elif status == select.POLLHUP:
                        self.logger.logger.info(self.cmd + " fd "+ repr(fd) + "eadbshell recv POLLHUP")
                    else:
                        self.logger.logger.info(self.cmd + " fd "+ repr(fd) + 'eadbshell recv ' + repr(status))
                    if status & select.EPOLLHUP:
                        #adb shell return code check
                        #adb shell will return 0 once cmd is execed except receive signal interrupt
                        #
                        stdout, stderr = self.sp.communicate()
                        #self.logger.logger.info('recv hungup , adb shell ret code is ' + str(self.sp.returncode))
                        #self.cmdexit = self.sp.returncode
                        return

                    elif status & select.EPOLLIN:
                        #NOTE: readlines will block until stream close
                        lines = self.sp.stdout.readlines()
                        exitcode = lines[-1].rstrip()
                        self.logger.logger.info("<" + self.cmd + '> exit code is ' + exitcode)
                        #http://tldp.org/LDP/abs/html/exitcodes.html
                        #1: general error
                        #2: misuse of builtin
                        #127: cmd not found
                        if exitcode == '0':
                            self.logger.logger.info(self.cmd + ' exit successfully!')
                            self.cmdexit = int(exitcode)
                            return
                        else:
                            self.cmdexit = int(exitcode)
                            self.logger.logger.info(self.cmd + ' failed.')


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
                    self.logger.logger.info('send SIGUSR1')
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
    #test cmd not found
    adbshell = eadbshell(cmd="abc", timeout=6)
    adbshell.run()

    #normal exit
    adbshell = eadbshell(cmd="ls -l", timeout=6)
    adbshell.run()

    #timeout process
    adbshell = eadbshell(cmd="sleep 7", timeout=3)
    adbshell.run()

    #continous output
    adbshell = eadbshell(cmd="ls -l && sleep 3 && ls -l", timeout=6)
    adbshell.run()

    """
    try:
        adb = adbhelper()
        adb.initDevice()
        adb.push("adbhelper.py", "/system/lib/")
    except:
        etype = sys.exc_info()[0]
        evalue = sys.exc_info()[1]
        print "Unexpected error: " + str(etype) + ' ' + str(evalue)
    """