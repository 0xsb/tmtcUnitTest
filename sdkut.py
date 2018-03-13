#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com
import os
from tmtc_ut import *
from time import gmtime, strftime
from lib.report import *



class Sdkut(object):
    def __init__(self, casedir='', bindir=''):
        self.logger = logConf()
        self.casedir =  casedir
        self.brickdir = os.path.realpath(casedir) + '/bricks'
        self.bindir = bindir
        self.utils = logutils()
        self.timestamp = strftime("%Y_%m_%d_%H_%M_%S", gmtime())
        self.outdir = './output/' + self.timestamp
        self.reports = list()


    def run(self):
        for cdir in os.listdir(self.casedir):
            if cdir != 'bricks':
                confdir = self.casedir + '/' + cdir
                onetmtc = TmtcUt(confdir=confdir, brickdir=self.brickdir,bindir=self.bindir, outdir=self.outdir)
                try:
                    onetmtc.envsetup()
                    onetmtc.run()
                except :
                    #try to catch exception, continue to execute.
                    etype = sys.exc_info()[0]
                    evalue = sys.exc_info()[1]
                    estr = str(etype) + ' ' + repr(evalue)
                    self.logger.logger.error("Unexpected error:" + estr)
                self.reports.append(onetmtc.getreport())

    def dumpreport(self):
        for index, report in enumerate(self.reports):
            self.logger.logger.info('Case ' + report.getdesc() + " , run " + repr(report.getruntime()) + " s, Passed" if report.getresult() else "Failed")
        #https://www.w3cschool.cn/tryrun/showhtml/tryhtml_table_span
        #TODO: dump report data to json

if __name__ == '__main__':
    sdk = Sdkut(casedir="./cases", bindir='./bin')
    sdk.run()
    sdk.dumpreport()