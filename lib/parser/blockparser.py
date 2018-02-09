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
path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(path+'/../'))

from logConf import *

class Block(dict):
    def __init__(self, *arg, **kw):
        super(Block, self).__init__(*arg, **kw)
        self['startnum'] = 0
        self['endnum'] = 0
        self['direct'] = None
        self['size'] = 0
        self['text'] = None

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
        self.logger = logConf()

        if os.path.exists(self.file):
            with open(self.file, 'r') as mfile:
                self.lines = mfile.readlines()
        else:
            raise bparserException(self.file + " not exists")

    def dump(self):
        for block in self.blocks:
            print 'direct is ' + block['direct'] + ', start to end is ' \
                  + str(block['startnum']) + '-' + str(block['endnum'])
            sp = sipparser.SipParser()
            sp.prepare(block)
            sp.parse()
            onesip = sp.getmsg()
            self.msgs.append(onesip)
            #sp.dumpmsg()

        for msg in self.msgs:
            #self.logger.logger.info('msg is ' + repr(msg))
            if msg['direct'] == 'send':
                self.logger.logger.info('req line is ' + msg.getreqline())
                self.logger.logger.info('callid is ' + msg.getheader('Call-ID'))
                sdp = msg.getsdp()
                if sdp:
                    self.logger.logger.info('sdp is ' + repr(sdp))

            elif msg['direct'] == 'recv':
                self.logger.logger.info('rsp line is ' + msg.getrspline())
                self.logger.logger.info('callid is ' + msg.getheader('Call-ID'))
                sdp = msg.getsdp()
                if sdp:
                    self.logger.logger.info('sdp is ' + repr(sdp))

            self.logger.logger.info('---------------------------------------')


    def parse(self):
        #pattern is from sipp's msg format
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
                oneblock['text'] = self.lines[oneblock['startnum']:oneblock['endnum']]
                self.blocks.append(oneblock)
                #print 'index is ' + str(oneblock['endnum'])

        if blockfound == True:
            oneblock = Block()
            oneblock['startnum'] = startnum
            oneblock['endnum'] = len(self.lines)
            oneblock['size'] = size
            oneblock['direct'] = direct
            oneblock['text'] = self.lines[oneblock['startnum']:oneblock['endnum']]
            self.blocks.append(oneblock)





if __name__ == '__main__':
    bp = BlockParser(srcfile="../../output/MT_call_07_13_28/mt.msg")
    bp.parse()
    bp.dump()


