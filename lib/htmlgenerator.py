#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

#0. initial version is just list all cases, no categories
# https://stackoverflow.com/questions/9830506/how-do-you-use-colspan-and-rowspan-in-html-tables
#1. genindex
#2. overall report
#3. category report
#99. TODO: use jinja2, copy from http://cn.httprunner.org/report/
#    https://www.computerhope.com/htmcolor.htm
#    https://github.com/HttpRunner/HttpRunner/blob/master/httprunner/templates/default_report_template.html


import os
import dominate
from dominate.tags import *
from report import *


class htmlgenerator():
    def __init__(self,  data=[]):
        self.data = data
        self.doc = dominate.document(title="tmtc report", doctype="<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN http://www.w3.org/TR/html4/loose.dtd\">")
        metastring=meta(http_equiv="Content-Type", content="text/html; charset=utf-8")
        self.doc.head.add(metastring)

    def addstyle(self):
        stylecontent = "table {border-collapse: collapse;}\n"
        stylecontent += "td {padding: 0px;text-align: center;}\n"
        stylestring=style(stylecontent,type="text/css")
        self.doc.head.add(stylestring)

    def genIndex(self):
        pass

    def genReportTable(self):
        """
        overall case report
        :return:
        """
        tab = table(border=1)
        cap = caption(b("Cases Report"))
        tab.add(cap)
        theaders = ["No", "Case", "Result", "SubCase", "SubResult"]
        for theader in theaders:
            tab.add(th(theader))

        #start to add cases
        for index, data in enumerate(self.data):
            #each data is a row
            #data is object report
            firsttr = tr()
            sublen = len(data["subreports"])
            notd = td(index+1, rowspan=sublen)
            casetd = td(data["desc"], rowspan=sublen)

            if data["result"] == True:
                resulttd = td("Passed", style="background-color: green", rowspan=sublen)
            else:
                resulttd = td("Failed", style="background-color: red", rowspan=sublen)
            firsttr.add(notd)
            firsttr.add(casetd)
            firsttr.add(resulttd)

            for index, subreport in enumerate(data["subreports"]):
                trinuse = None
                if index == 0:
                    #the first tr is already gened.
                    trinuse = firsttr
                else:
                    trinuse = tr()
                subtd = td(subreport["desc"])
                #FIXME:just write verbose code
                if subreport["result"] == True:
                    subresulttd = td("Passed", style="background-color: green")
                else:
                    subresulttd = td("Failed", style="background-color: red")
                trinuse.add(subtd)
                trinuse.add(subresulttd)
                tab.add(trinuse)

        self.doc.add(tab)




    def genCategoryTable(self):
        """
        reg, call category table
        :return:
        """
        pass

    def dump(self):
        print self.doc

if __name__ == '__main__':


    reportjson = [
        {
            "desc": "MT call", 
            "result": True, 
            "runtime": 16.837204, 
            "subreports": [
                {
                    "cmd": "MT_cmd1",
                    "desc": "Register", 
                    "result": True, 
                    "timeout": 10
                }, 
                {
                    "cmd": "MT_cmd2",
                    "desc": "Subscribe/Notify", 
                    "result": True, 
                    "timeout": 10
                }, 
                {
                    "cmd": "MT_cmd3",
                    "desc": "MT call", 
                    "result": True, 
                    "timeout": 10
                }
            ]
        }, 
        {
            "desc": "RegSub", 
            "result": False,
            "runtime": 11.411985, 
            "subreports": [
                {
                    "cmd": "cmd4",
                    "desc": "Register", 
                    "result": True, 
                    "timeout": 10
                }, 
                {
                    "cmd": "cmd5",
                    "desc": "Subscribe/Notify", 
                    "result": False,
                    "timeout": 10
                }
            ]
        }
    ]

    reportlist = genTestReport()

    # construct test data...
    hg = htmlgenerator(data=reportlist)
    hg.addstyle()
    hg.genReportTable()
    hg.dump()
