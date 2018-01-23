#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com
import os
from tmtc_ut import *


class Sdkut(object):
    def __init__(self, casedir='', bindir=''):
        self.casedir =  casedir
        self.brickdir = os.path.realpath(casedir) + '/bricks'
        self.bindir = bindir

    def run(self):
        for cdir in os.listdir(self.casedir):
            if cdir != 'bricks':
                confdir = self.casedir + '/' + cdir
                onetmtc = TmtcUt(confdir=confdir, brickdir=self.brickdir,bindir=self.bindir)
                onetmtc.envsetup()
                onetmtc.run()


if __name__ == '__main__':
    sdk = Sdkut(casedir="./cases", bindir='./bin')
    sdk.run()