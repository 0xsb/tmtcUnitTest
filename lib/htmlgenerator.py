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
    def __init__(self,  data=[], outdir=""):
        self.outdir = outdir
        self.file = outdir + '/report.html'
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

    def genSummary(self):
        # gen summary
        # Total Pass Fail
        tab = table(border=1)
        cap = caption(b("Summary"))
        tab.add(cap)
        theaders = ["RunTime","Total", "Pass", "Failed"]
        for theader in theaders:
            tab.add(th(theader))
        totalnum = len(self.data)
        passnum = 0
        failnum = 0
        for data in self.data:
            if data["result"] == True:
                passnum += 1
        failnum = totalnum - passnum
        onetr = tr()

        timesum = 0
        for data in self.data:
            timesum = timesum + data["runtime"]

        timetd = td(format(timesum,'.3f') + 's')
        totaltd = td(totalnum)
        passtd = td(passnum,style="background-color: green")
        if failnum > 0:
            failtd = td(failnum, style="background-color: red")
        else:
            failtd = td(failnum)
        onetr.add(timetd)
        onetr.add(totaltd)
        onetr.add(passtd)
        onetr.add(failtd)
        tab.add(onetr)
        self.doc.add(tab)

    def genReportTable(self):
        """
        overall case report
        :return:
        """
        tab = table(border=1)
        cap = caption(b("Cases Report"))
        tab.add(cap)
        theaders = ["No", "Case", "RunTime","Result", "SubCase", "RunTime","SubResult"]
        for theader in theaders:
            tab.add(th(theader))

        #start to add cases
        for index, data in enumerate(self.data):
            #each data is a row
            #data is object report
            firsttr = tr()
            sublen = len(data["subreports"])
            notd = td(index+1, rowspan=sublen)
            timetd = td(format(data["runtime"], '.3f') + 's', rowspan=sublen)
            casetd = td(data["desc"], rowspan=sublen)

            if data["result"] == True:
                resulttd = td("Passed", style="background-color: green", rowspan=sublen)
            else:
                resulttd = td("Failed", style="background-color: red", rowspan=sublen)
            firsttr.add(notd)
            firsttr.add(casetd)
            firsttr.add(timetd)
            firsttr.add(resulttd)

            for index, subreport in enumerate(data["subreports"]):
                trinuse = None
                if index == 0:
                    #the first tr is already gened.
                    trinuse = firsttr
                else:
                    trinuse = tr()
                desctd = td(subreport["desc"])
                subtimetd = td(format(subreport["runtime"], '.3f') + 's')
                #FIXME:just write verbose code
                if subreport["result"] == True:
                    subresulttd = td("Passed", style="background-color: green")
                else:
                    subresulttd = td("Failed", style="background-color: red")
                trinuse.add(desctd)
                trinuse.add(subtimetd)
                trinuse.add(subresulttd)
                tab.add(trinuse)

            #in case no subreports
            if len(data["subreports"]) == 0:
                tab.add(firsttr)

        self.doc.add(tab)


    def genCategoryTable(self):
        """
        reg, call category table
        subSection details
        :return:
        """
        pass

    def dump(self):
        print self.doc
        with open(self.file, 'w+') as f:
            f.write(str(self.doc))

if __name__ == '__main__':


    reportjson = [
            {
                "category": "TMTC",
                "subreports": [
                         {
                        "cmd": "cd /data/data/ut/RegSub_2018_03_15_15_06_08&& sipp -sf reg.xml  -p 5060 -t u1 -m 1 -trace_err  -trace_msg -message_file reg.msg  -trace_shortmsg -shortmessage_file regshort.msg ",
                        "result": True,
                        "timeout": 10,
                        "desc": "MT call",
                        "runtime": 1.1
                        }
                ],
                "runtime": 17.844057,
                "result": False,
                "desc": "MT call"
            },
            {
                "category": "TMTC",
                "subreports": [
                    {
                        "cmd": "cd /data/data/ut/RegSub_2018_03_15_15_06_08&& sipp -sf reg.xml  -p 5060 -t u1 -m 1 -trace_err  -trace_msg -message_file reg.msg  -trace_shortmsg -shortmessage_file regshort.msg ",
                        "result": True,
                        "timeout": 10,
                        "desc": "Register",
                        "runtime": 1.1
                    },
                    {
                        "cmd": "cd /data/data/ut/RegSub_2018_03_15_15_06_08&& sipp -sf subs_notify.xml  -p 5060 -t u1 -m 1 -trace_err  -trace_msg -message_file subs_notify.msg  -trace_shortmsg -shortmessage_file subs_notifyshort.msg ",
                        "result": True,
                        "timeout": 10,
                        "desc": "Subscribe/Notify",
                        "runtime": 10
                    }
                ],
                "runtime": 11.792572,
                "result": True,
                "desc": "RegSub"
            }
        ]

    reportlist = genTestReport()
    """
    # construct test data...
    hg = htmlgenerator(data=reportlist)
    hg.addstyle()
    hg.genReportTable()
    hg.dump()
    """
    hg = htmlgenerator(data=reportjson,outdir='./')
    hg.addstyle()
    hg.genSummary()
    hg.genReportTable()
    hg.dump()
