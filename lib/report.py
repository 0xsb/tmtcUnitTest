#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

#use getter and setter is better
#https://stackoverflow.com/questions/1641219/does-python-have-private-variables-in-classes

class subreport(dict):
    def __init__(self, *arg, **kw):
        self.result = False
        self.__desc = None
        self.__cmd = None
        self.__timeout = None
        super(subreport, self).__init__(*arg, **kw)

    def setresult(self, result):
        self.result = result

    def setdesc(self,desc):
        self.__desc = desc

    def setcmd(self, cmd):
        self.__cmd = cmd

    def settimeout(self,timeout):
        self.__timeout = timeout

    def getresult(self):
        return self.result

    def getdesc(self):
        return self.__desc

    def getcmd(self):
        return self.__cmd

    def gettimeout(self):
        return self.__timeout

class report(dict):
    def __init__(self, *arg, **kw):
        self.__result = False
        self.__desc = None
        self.__subreports = list()
        self.__runtime = 0
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