#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com
"""
actually quite simple name/value pairs
just add some error handling
"""

import os
import sys

#tmtc cmds constants
TMTC_CMDS = list()
TMTC_CMDS.append('c-reg')
TMTC_CMDS.append('c-unreg')
TMTC_CMDS.append('t-call')
TMTC_CMDS.append('t-answer')
TMTC_CMDS.append('t-bye')

def validCmd(cmd):
    if cmd in TMTC_CMDS:
        return True
    else:
        return False

