#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com
import os
from tmtc_ut import *
from time import gmtime, strftime
from lib.report import *
from lib.htmlgenerator import *
from lib.jinjagenerator import *

class Sdkut(object):
    def __init__(self, casedir='', bindir=''):
        self.casedir =  casedir
        self.brickdir = os.path.realpath(casedir) + '/bricks'
        self.bindir = bindir
        self.utils = logutils()
        self.timestamp = strftime("%Y_%m_%d_%H_%M_%S", gmtime())
        self.outdir = './output/' + self.timestamp
        self.reports = list()
        self.logger = logConf()

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
        fjson = list()
        for index, report in enumerate(self.reports):
            resultstr = "Passed" if report.getresult() else "Failed"
            self.logger.logger.info('Case ' + report.getdesc() + " , run " + repr(report.getruntime()) + " s," + resultstr)
            fjson.append(report.todict())
        #https://www.w3cschool.cn/tryrun/showhtml/tryhtml_table_span

        with open(self.outdir + '/report.json', 'w+') as f:
            f.write(json.dumps(fjson, indent=4))

        #old style html
        """
        hg = htmlgenerator(data=fjson, outdir=self.outdir)
        hg.addstyle()
        hg.genSummary()
        hg.genReportTable()
        hg.dump()
        """
        summary = convert(fjson)
        temphtml = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
            "lib/templates",
            "tmtc_report_sample.html"
        )
        jinja2 = JinjaGenerator(templatehtml=temphtml, data=summary)
        html = jinja2.render()
        with open(self.outdir + "/report.html", "w+") as file:
            file.write(html)

if __name__ == '__main__':
    sdk = Sdkut(casedir="./cases", bindir='./bin')
    sdk.run()
    sdk.dumpreport()