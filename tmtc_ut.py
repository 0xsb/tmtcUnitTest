#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com


from lib.adbhelper import *
from lib.logutils import *
from lib.cmdhelper import *
from lib.logConf import *
import sys
# 1. env setup
# 2. process goes
# 3. result check

class TmtcUt(object):
    def __init__(self, outdir = './output', loglevel='DEBUG', brickdir='', confdir=''):
        self.logger = logConf(debuglevel=loglevel)
        self.outdir = outdir
        self.brickdir = brickdir
        self.confdir = confdir
        self.configfile = 'config.ini'
        self.utils = logutils()

    def envsetup(self):
        """
        1. parse conf
        2. prepare env setup

        :return:
        """
        cmdbuilder = cmdhelper()

        pass

    def run(self):
        """
        1. run tmtclient process
        2. run SIPp xmls
        3. collect the report after each sce
        :return:
        """
        pass

if __name__ == '__main__':
    tmtc = TmtcUt(brickdir='cases/bricks/', confdir="cases/mt/")
    tmtc.envsetup()