#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

#https://stackoverflow.com/questions/30937829/how-to-get-both-return-code-and-output-from-subprocess-in-python
"""
1. adb root, adb remount
2. adb push libs and resource
2.1 currently use adb cmd, python-adb is optional

"""
from logConf import *
from task import *

class ResourceException(Exception):
    def __init__(self, message):
        super(ResourceException, self).__init__(message)
        self.message = message

class reshelper:
    def __init__(self):
        #device init
        #adb root, retry 3 times
        #adb remount, retry 3 times
        pass

    def push(self, filename, destdir):
        #adb push file dest
        pass