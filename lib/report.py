#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

#use getter and setter is better
#https://stackoverflow.com/questions/1641219/does-python-have-private-variables-in-classes
import json
from logutils import *

class subreport(dict):
    def __init__(self, *arg, **kw):
        self.__result = False
        self.__desc = None
        self.__cmd = None
        self.__timeout = None
        super(subreport, self).__init__(*arg, **kw)

    def setresult(self, result):
        self.__result = result

    def setdesc(self,desc):
        self.__desc = desc

    def setcmd(self, cmd):
        self.__cmd = cmd

    def settimeout(self,timeout):
        self.__timeout = timeout

    def getresult(self):
        return self.__result

    def getdesc(self):
        return self.__desc

    def getcmd(self):
        return self.__cmd

    def gettimeout(self):
        return self.__timeout

    def todict(self):
        rstr = dict()
        rstr['result'] = self.__result
        rstr['desc'] = self.__desc
        rstr['cmd'] = self.__cmd
        rstr['timeout'] = self.__timeout
        return rstr

class report(dict):
    def __init__(self, *arg, **kw):
        self.__result = False
        self.__desc = None
        self.__subreports = list()
        self.__runtime = 0
        self.__category = "TMTC"
        super(report, self).__init__(*arg, **kw)

    def setresult(self ,result):
        self.__result = result

    def getresult(self):
        return self.__result

    def setdesc(self, desc):
        self.__desc = desc

    def getdesc(self):
        return self.__desc

    def addsubreport(self, subreport):
        self.__subreports.append(subreport)

    def setsubreports(self, subreports):
        self.__subreports = subreports

    def getsubreports(self):
        return self.__subreports

    def setruntime(self, runtime):
        self.__runtime = runtime

    def getruntime(self):
        return self.__runtime

    def setcategroy(self, category):
        self.__category = category

    def getcategory(self):
        return self.__category

    def todict(self):
        rstr = dict()
        rstr["result"] = self.__result
        rstr["desc"] = self.__desc
        rstr["runtime"] = self.__runtime
        rstr["subreports"] = list()
        rstr["category"] = self.__category

        for index, subr in enumerate(self.__subreports):
            rstr["subreports"].append(subr.todict())
        return rstr

#write a report generator for test
def genTestReport(reportmax=4, subrepmax=3):
    utils = logutils()
    reportnum = utils.int_generator(1,reportmax)
    reportlist = list()
    for num in range(reportnum):
        onereport = report()
        onereport.setdesc(utils.asciistr_generator())
        onereport.setcategroy(utils.asciistr_generator())
        tf=utils.int_generator(1,2)
        if tf % 2 == 1:
            onereport.setresult(True)
        else:
            onereport.setresult(False)
        onereport.setruntime(num)
        subrptnum = utils.int_generator(1,subrepmax)

        subrptlist = list()
        for num in range(subrptnum):
            onesubrpt = subreport()
            tf =utils.int_generator(1,2)
            if tf % 2 == 1:
                onesubrpt.setresult(True)
            else:
                onesubrpt.setresult(False)
            onesubrpt.setdesc(utils.asciistr_generator())
            onesubrpt.setcmd(utils.asciistr_generator())
            onesubrpt.settimeout(num)
            subrptlist.append(onesubrpt)
        onereport.setsubreports(subrptlist)

        reportlist.append(onereport.todict())
    return reportlist

if __name__ == '__main__':
    r1 = subreport()
    print json.dumps(r1.todict())
    r2 = subreport()
    r2.setresult(True)
    r2.setdesc("Reg")
    r2.setcmd("c-reg")
    print json.dumps(r2.todict())
    r3 = report()
    r3.addsubreport(r1)
    r3.addsubreport(r2)
    r3.setdesc("Case Report")
    r3.setruntime(10)
    print json.dumps(r3.todict())
    with open('./fjson', 'w+') as f:
        f.write(json.dumps(r3.todict()))

    rl = genTestReport()
    print rl