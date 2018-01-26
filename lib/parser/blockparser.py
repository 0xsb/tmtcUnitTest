#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

"""
try to get sip msg block in SIPp output msgs
1.  msg may be sent or received.
2.  seperator
"""

import os
import sys
import re
import sipparser


class Block(dict):
    def __init__(self, *arg, **kw):
        super(Block, self).__init__(*arg, **kw)
        self['startnum'] = 0
        self['endnum'] = 0
        self['direct'] = None
        self['size'] = 0

class bparserException(Exception):
    def __init__(self, msg):
        super(bparserException, self).__init__(msg)
        self.message = msg


class BlockParser(object):
    def __init__(self, srcfile=''):
        self.file = srcfile
        self.lines = list()
        self.blocks = list()
        self.msgs = list()

        if os.path.exists(self.file):
            with open(self.file, 'r') as mfile:
                self.lines = mfile.readlines()
        else:
            raise bparserException(self.file + " not exists")

    def dump(self):
        for block in self.blocks:
            print 'direct is ' + block['direct'] + ', start to end is ' \
                  + str(block['startnum']) + '-' + str(block['endnum'])

        for msg in self.msgs:
            print msg['content']
            sp = sipparser.SipParser()
            sp.parse(msg=msg)

    def getmsg(self):
        return self.msgs

    def parse(self):
        recvpattern = "message received \[(\d+)\] bytes"
        recvregex = re.compile(recvpattern)
        sendpatern = "message sent \((\d+) bytes\)"
        sendregex = re.compile(sendpatern)
        endpattern = "-----------------------------------------------"

        blockfound = False
        size = 0
        #start linenum, end linenum
        startnum = 0
        endnum = 0
        direct = None

        #get blocks
        for index, line in enumerate(self.lines):
            recv = recvregex.search(line)
            send = sendregex.search(line)
            if send:
                blockfound = True
                size = str(send.group(1))
                startnum = index + 1
                direct = 'send'

            if recv:
                blockfound = True
                size = str(recv.group(1))
                startnum = index + 1
                direct = 'recv'

            if endpattern in line and blockfound:
                blockfound = False
                endnum = index - 1
                oneblock = Block()
                oneblock['startnum'] = startnum
                oneblock['endnum'] = endnum
                oneblock['size'] = size
                oneblock['direct'] = direct
                self.blocks.append(oneblock)
                #print 'index is ' + str(oneblock['endnum'])

        if blockfound == True:
            oneblock = Block()
            oneblock['startnum'] = startnum
            oneblock['endnum'] = len(self.lines)
            oneblock['size'] = size
            oneblock['direct'] = direct
            self.blocks.append(oneblock)


        for block in self.blocks:
            msg = dict()
            msg['direct'] = block['direct']
            msg['size'] = block['size']
            msg['content'] = self.lines[block['startnum']: block['endnum']]
            self.msgs.append(msg)



if __name__ == '__main__':
    bp = BlockParser(srcfile="../../output/MT_call_07_13_28/mt.msg")
    bp.parse()
    bp.dump()


