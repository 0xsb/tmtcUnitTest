#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com


from lib.adbhelper import *
from lib.logutils import *
from lib.cmdhelper import *
from lib.logConf import *
import sys
import os
# 1. env setup
# 2. process goes
# 3. result check

class TmtcUt(object):
    def __init__(self, outdir = './output', loglevel='DEBUG', confdir='', brickdir='',bindir=''):
        self.logger = logConf(debuglevel=loglevel)
        self.outdir = outdir
        self.confdir = confdir
        self.brickdir = brickdir
        self.bindir = bindir
        self.utils = logutils()
        """
        1. parse conf
        2. prepare env setup
        """
        self.cmdenv = cmdhelper(confdir=self.confdir)
        self.cmdenv.buildCmd()

        self.adb = adbhelper()
        self.adb.initDevice()


    def envsetup(self):
        desc = self.cmdenv.getDesc()
        ueconfig = self.cmdenv.getUeConfig()
        xmls = self.cmdenv.getxmls()
        #push ue's res
        #UE binary: tmtclicent, libavatar_ut.so, liblemon_ut.so,
        bindir = os.path.realpath(self.bindir)
        binary = bindir + '/' + ueconfig['binary']
        self.adb.push(binary, "/system/bin/")
        for index, lib in enumerate(ueconfig['lib']):
            lib = bindir + '/' + lib
            self.adb.push(lib, "/system/lib/")
        #UE config: Provision.ini
        proini = bindir + '/' + ueconfig['config']
        execdir = ueconfig['execdir']
        self.adb.mkdirp(execdir)
        self.adb.push(proini, execdir)

        #sipp xml
        brickdir = os.path.realpath(self.brickdir)
        for index, xml in enumerate(xmls):
            xml = brickdir + '/' + xml
            self.adb.push(xml, execdir)



    def run(self):
        """
        1. run tmtclient process
        2. run SIPp xmls
        3. collect the report after each sce
        :return:
        """
        pass

if __name__ == '__main__':
    tmtc = TmtcUt(confdir="cases/mt/", brickdir="cases/bricks/",bindir="bin")
    tmtc.envsetup()