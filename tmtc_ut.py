#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com
from lib.logConf import *
# 1. env setup
# 2. process goes
# 3. result check

class TmtcUt(object):
    def __init__(self, outdir = './output', loglevel='DEBUG'):
        self.logger = logConf(debuglevel=loglevel)
        self.outdir = outdir


    def envsetup(self):
        """
        1. parse conf
        2. prepare env setup
        :return:
        """
        pass

    def run(self):
        """
        1. run tmtclient process
        2. run SIPp xmls
        3. collect the report after each sce
        :return:
        """
        pass