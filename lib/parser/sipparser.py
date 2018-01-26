#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

"""
1. parse sip header, too verbose, reuse old logic
2. parse sip msg body including sdp/xml
"""

import os
import re
import sys
from sipconstants import *
path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(path+'/../'))

from logConf import *

class SipMsg(dict):
    def __init__(self, *arg, **kw):
        super(SipMsg, self).__init__(*arg, **kw)
        self['reqline'] = dict()
        self['reqline']['line'] = None
        self['reqline']['method'] = None
        self['reqline']['uri'] = None
        self['rspline'] = dict()
        self['rspline']['line'] = None
        self['rspline']['statuscode'] = None
        self['rspline']['phrase'] = None
        self['headers'] = dict()
        self['content'] = dict()
        self['content']['size'] = 0
        self['content']['body'] = None


class SipParser(object):
    def __init__(self):
        self.sipmsg = None
        self.logger = logConf()

    def parse(self, msg):
        # req/rsp line come first
        # parse header
        # \r\n is the seperator of content
        # only parse sdp
        self.sipmsg = SipMsg()

        sdpregex = re.compile(SipPattern['sdppattern'])

        seperator = SipPattern['seperator']
        sdpbody = list()

        for index, line in enumerate(msg):
            print line
            if self.parseReq(line):
                continue

            if self.parseRsp(line):
                continue

            if self.parseHeader(line):
                continue

            if seperator in line:
                #need to check Content-Type and Content-Length

                if 'Content-Type' in self.sipmsg['headers'] and 'Content-Length' in self.sipmsg['headers']:
                    ct = self.sipmsg['headers']['Content-Type']
                    cl = self.sipmsg['headers']['Content-Length']
                    self.logger.logger.info('content length is ' + str(cl) + ', content type is ' + str(ct))
                    if ct == "application/sdp" and int(cl) >= 0:
                        #only parse sdp
                        self.sipmsg['content']['size'] = cl
                        self.sipmsg['content']['body'] = msg[index + 1:len(msg)]
                break


        if sdpbody:
            self.parseSdp(sdpbody)

    def parseReq(self, line):
        reqregex = re.compile(SipPattern['reqline'])
        req = reqregex.search(line)
        if req:
            #already done in regex

            self.sipmsg['reqline']['line'] = req.group(0)
            self.sipmsg['reqline']['method'] = req.group(1)
            self.sipmsg['reqline']['uri'] = req.group(2)
            return True
        else:
            return False

    def parseRsp(self, line):
        rspregex = re.compile(SipPattern['rspline'])
        rsp = rspregex.search(line)
        if rsp:
            #already done in regex
            self.sipmsg['rspline']['line'] = rsp.group(0)
            self.sipmsg['rspline']['statuscode'] = rsp.group(1)
            self.sipmsg['rspline']['phrase'] = rsp.group(2)
            return True
        else:
            return False

    def checkCompact(self):
        pass

    def parseHeader(self, line):
        headregex = re.compile(SipPattern['headerline'])
        headerline = headregex.search(line)

        if headerline:
            header = headerline.group(1).strip()
            content = headerline.group(2).strip()
            oneheader = dict()
            if header in SipCompactReverse:
                #if abbr header, use full name
                header = SipCompactReverse[header]

            self.sipmsg['headers'][header] = content


    def parseSdp(self, sdp):
        # Content-Type is application/sdp
        # Content-Length is not 0
        pass

    def parseXml(self, xml):
        #TODO: later
        pass

    def dumpmsg(self):
        print repr(self.sipmsg)

    def getmsg(self):
        return self.sipmsg

if __name__ == '__main__':
    sp = SipParser()
    onereq = list()
    onereq.append("INVITE sip:service@127.0.0.1:5065 SIP/2.0")
    onereq.append("v: SIP/2.0/UDP 127.0.0.1:5060;branch=z9hG4bK-22142-1-0")
    onereq.append('Contact: sip:sipp@127.0.0.1:5060')
    onereq.append('Content-Type: application/sdp')
    onereq.append('Content-Length:   136')
    onereq.append('\r\n')
    onereq.append('v=0')
    onereq.append('o=user1 53655765 2353687637 IN IP4 127.0.0.1')
    onereq.append('s=-')

    for index, req in enumerate(onereq):
        print req
    sp.parse(msg=onereq)
    sp.dumpmsg()
    onersp = list()
    onersp.append("SIP/2.0 100 Trying")
    onersp.append("To: sut <sip:service@127.0.0.1:5065>")
    sp.parse(msg=onersp)
    sp.dumpmsg()

    #add sdp later