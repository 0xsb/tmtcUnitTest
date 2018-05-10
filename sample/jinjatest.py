#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

#test jinja template

from jinja2 import *

env = Environment(
        loader=FileSystemLoader('./'),
        autoescape=select_autoescape(['html', 'xml']))
template = env.get_template('default_report_template.html')

summary = dict()
summary["html_report_name"] = "jinjatest"
summary["time"] = {
    "start_at": "11:00",
    "duration": 6
}
summary["platform"] = {
    "httprunner_version": "1",
    "python_version": "2.7",
    "platform": "linux"
}
summary["stat"] = {
    "testsRun" : 100,
    "successes": 80,
    "failures": 5,
    "errors": 5,
    "skipped": 10
}
summary["records"] = list()
onerecord = {
    "status": "success",
    "name": "test1",
    "response_time": "1.234",
    "meta_data": "./abc",
    "attachment": "./234"
}
summary["records"].append(onerecord)


html = template.render(summary)
with open("./jinja.html", "w+") as file:
    file.write(html)