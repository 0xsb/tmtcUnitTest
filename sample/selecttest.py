#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

import os
import select, sys, subprocess
import shlex
import time

netstat="netstat -antpu"
vmstat = subprocess.Popen(shlex.split(netstat), shell=True, bufsize=1024,
        stdout=subprocess.PIPE)
vmstat_pipe = vmstat.stdout

iostat_pipe = subprocess.Popen('top', shell=True, bufsize=1024,
        stdout=subprocess.PIPE).stdout

pipe_dict = {vmstat_pipe.fileno():vmstat_pipe, iostat_pipe.fileno():iostat_pipe}

p = select.poll()
p.register(vmstat_pipe, select.POLLIN|select.POLLERR|select.POLLHUP)
p.register(iostat_pipe, select.POLLIN|select.POLLERR|select.POLLHUP)
while 1:
    result = p.poll(5000)
    if len(result) != 0:
        for m in result:
           # Polls the set of registered file descriptors, and returns a possibly-empty list containing (fd, event)
            if m[1] & select.POLLHUP and m[0] == iostat_pipe.fileno():
                print 'Get HUPUP from pipe', m[0]
                exit()
            if m[1] & select.POLLIN:
                #print "Get", pipe_dict[m[0]].readline(), "from pipe", m[0]
                print "Get", pipe_dict[m[0]].readline(), "from pipe", m[0]


