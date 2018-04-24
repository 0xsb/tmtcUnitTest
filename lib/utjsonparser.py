#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com
"""
actually quite simple name/value pairs
just add some error handling
"""

import os
import sys

DUMMY_CMD = "dummycmd"
#tmtc cmds constants
#should add a new valiator
#some cmd should be matched
#some cmd should add arguments.


TMTC_CMDS = list()
TMTC_CMDS.append('c-reg')
TMTC_CMDS.append('c-unreg')
TMTC_CMDS.append('t-call')
TMTC_CMDS.append('t-answer')
TMTC_CMDS.append('t-bye')

def validCmd(cmd):
    cmd = cmd.strip()
    if cmd in TMTC_CMDS:
        return True
    else:
        #get prefix cmd
        prefix = cmd.split(' ')
        if prefix[0] in TMTC_CMDS:
            return True
        else:
            return False

