#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

#generate html report based on jinja template

from jinja2 import *


#define function to convert original data into jinja preferred data
def convert(reports):
    #ugle coupling in todict in report.py
    summary = dict()
    summary['html_report_name'] = "VoWiFi TMTC case report"

    starttime = 0
    testnum = len(reports)
    successnum = 0
    failnum = 0
    duration = 0
    summary["reports"] = list()
    
    for index, report in enumerate(reports):

        if index == 0:
            starttime = report["starttime"]
        #1. add "index" and "subnum" into report
        report["index"] = index + 1
        report["subnum"] = len(report["subreports"])
        #2. change result to css class in template html, True->success, False->failure
        if report["result"]:
            report["result"] = "success"
            successnum += 1
        else:
            report["result"] = "failure"
            failnum += 1

        for subreport in report["subreports"]:
            if subreport["result"]:
               subreport["result"] = "success"
            else:
               subreport["result"] = "failure"

        summary["reports"].append(report)
        duration += report["runtime"]

    summary["stat"] = {
        "testsRun" : testnum,
        "successes": successnum,
        "failures": failnum,
        "errors": 0,
        "skipped": 0
    }

    summary["time"] = {
        "start_at": starttime,
        "duration": duration
    }
    return summary


class JinjaGenerator():
    def __init__(self, templatehtml='', data=None):
        with open(templatehtml, 'r') as th:
            self.__template = Template(th.read())
        self.__data = data

    def getTemplate(self):
        return self.__template

    def getdata(self):
        return self.__data

    def render(self):
        return self.__template.render(self.__data)


"""
env = Environment(
        loader=FileSystemLoader('./'),
        autoescape=select_autoescape(['html', 'xml']))

template = env.get_template('tmtc_report_sample.html')
"""

def sampletest():
    summary = dict()
    summary['html_report_name'] = "VoWiFi TMTC"
    summary['time'] = {
        "start_at": "11:00",
        "duration": 6
    }
    summary["stat"] = {
        "testsRun" : 100,
        "successes": 80,
        "failures": 5,
        "errors": 5,
        "skipped": 10
    }
    summary['reports'] = list()
    onereport = {
        "subnum": 2,
        "index": 1,
        "desc": "register",
        "runtime": 15,
        "result": "success",
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
                    ]
    }

    tworeport = {
        "subnum": 1,
        "index": 2,
        "desc": "register",
        "runtime": 15,
        "result": "success",
        "subreports":[
                        {
                            "cmd": "cd /data/data/ut/RegSub_2018_03_15_15_06_08&& sipp -sf reg.xml  -p 5060 -t u1 -m 1 -trace_err  -trace_msg -message_file reg.msg  -trace_shortmsg -shortmessage_file regshort.msg ",
                            "result": True,
                            "timeout": 10,
                            "desc": "Register",
                            "runtime": 1.1
                        }
                    ]
    }

    summary["reports"].append(onereport)
    summary["reports"].append(tworeport)

    jinja = JinjaGenerator(templatehtml='./tmtc_report_sample.html', data=summary)
    html = jinja.render()

    with open("./jinja1.html", "w+") as file:
        file.write(html)

def sampletest2():
    onereport = {
    "category": "Call",
    "subreports": [
        {
            "runtime": 1.501622,
            "cmd": "cd /data/data/ut/mo_status_confirm_2018_05_10_08_04_07&& sipp -sf reg.xml  -p 5060 -t u1 -m 1 -trace_err  -trace_msg -message_file reg.msg  -trace_shortmsg -shortmessage_file regshort.msg ",
            "result": True,
            "timeout": 3,
            "desc": "Register"
        },
        {
            "runtime": 1.150326,
            "cmd": "cd /data/data/ut/mo_status_confirm_2018_05_10_08_04_07&& sipp -sf subs_notify.xml  -p 5060 -t u1 -m 1 -trace_err  -trace_msg -message_file subs_notify.msg  -trace_shortmsg -shortmessage_file subs_notifyshort.msg ",
            "result": True,
            "timeout": 3,
            "desc": "Subscribe/Notify"
        },
        {
            "runtime": 6.91914,
            "cmd": "cd /data/data/ut/mo_status_confirm_2018_05_10_08_04_07&& sipp -sf mo_status_confirm.xml  127.0.0.1:5065 -p 5060 -t u1 -m 1 -trace_err  -trace_msg -message_file mo_status_confirm.msg  -trace_shortmsg -shortmessage_file mo_status_confirmshort.msg ",
            "result": True,
            "timeout": 8,
            "desc": "MO call"
        },
        {
            "runtime": 2.119142,
            "cmd": "cd /data/data/ut/mo_status_confirm_2018_05_10_08_04_07&& sipp -sf uebye.xml  127.0.0.1:5065 -p 5060 -t u1 -m 1 -trace_err  -trace_msg -message_file uebye.msg  -trace_shortmsg -shortmessage_file uebyeshort.msg ",
            "result": True,
            "timeout": 6,
            "desc": "UE bye"
        }
    ],
    "result": True,
    "starttime": "2018.05.10 16:04:07",
    "runtime": 20.866517,
    "desc": "mo_status_confirm"
    }

    tworeport = {
    "category": "Call",
    "subreports": [
        {
            "runtime": 0.500622,
            "cmd": "cd /data/data/ut/mo_status_confirm_2018_05_10_08_04_07&& sipp -sf reg.xml  -p 5060 -t u1 -m 1 -trace_err  -trace_msg -message_file reg.msg  -trace_shortmsg -shortmessage_file regshort.msg ",
            "result": True,
            "timeout": 3,
            "desc": "Register"
        },
        {
            "runtime": 1.150326,
            "cmd": "cd /data/data/ut/mo_status_confirm_2018_05_10_08_04_07&& sipp -sf subs_notify.xml  -p 5060 -t u1 -m 1 -trace_err  -trace_msg -message_file subs_notify.msg  -trace_shortmsg -shortmessage_file subs_notifyshort.msg ",
            "result": False,
            "timeout": 3,
            "desc": "Subscribe/Notify"
        },
    ],
    "result": False,
    "starttime": "2018.05.10 18:04:07",
    "runtime": 10.866517,
    "desc": "register "
    }
    realdata = list()
    realdata.append(onereport)
    realdata.append(tworeport)
    summary = convert(realdata)
    jinja = JinjaGenerator(templatehtml='./tmtc_report_sample.html', data=summary)
    html = jinja.render()
    with open("./jinja.html", "w+") as file:
        file.write(html)

if __name__ == '__main__':
    sampletest2()
    pass
