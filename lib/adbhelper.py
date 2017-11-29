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

class adbhelper:
    def __init__(self):
        #device init
        self.logger = logConf()

    def adbCmd(self, cmd='', timeout=None, retry=1):
        try:
            adbtask = etask(cmd=cmd, timeout=timeout, retry=retry)
            adbtask.run()
        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            estr = str(etype) + ' ' + str(evalue)
            self.logger.logger.info("Unexpected error: " + estr)


    def initDevice(self):
        adbroot = "adb root"
        adbremount = "adb remount"
        self.adbCmd(adbroot)
        self.adbCmd(adbremount)


    def push(self, filename, destdir):
        #adb push file dest
        adbpush = "adb push " + filename + ' ' + destdir
        self.adbCmd(adbpush)

    def mkdirp(self, filename):
        mkdirp = "adb shell mkdir -p " + filename
        self.adbCmd(mkdirp)

if __name__ == '__main__':
    try:
        adb = adbhelper()
        adb.initDevice()
        adb.push("adbhelper.py", "/system/lib/")
    except:
        etype = sys.exc_info()[0]
        evalue = sys.exc_info()[1]
        print "Unexpected error: " + str(etype) + ' ' + str(evalue)