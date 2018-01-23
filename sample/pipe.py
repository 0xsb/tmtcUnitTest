#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com
#just emulate ls -l | grep py
#https://stackoverflow.com/questions/6780035/how-to-run-ps-cax-grep-something-in-python

import subprocess
import sys
import shlex

lsp = subprocess.Popen(shlex.split("ls -l"), stdout=subprocess.PIPE)
"""
stdout, stderr = lsp.communicate()
print('stdout: {0}'.format(stdout))
"""

grepp = subprocess.Popen(shlex.split("grep start"), stdin=lsp.stdout, stdout=subprocess.PIPE)
stdout, stderr = grepp.communicate()
print('stdout: {0}'.format(stdout))

