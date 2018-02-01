import os
import re
import sys
from sipconstants import *
path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(path+'/../'))

from logConf import *

# one sample
# https://github.com/sparkslabs/kamaelia/blob/master/Code/Python/Kamaelia/Kamaelia/Protocol/SDP.py

class SdpMsg(dict):
    def __init__(self,*arg, **kw):
        super(SdpMsg, self).__init__(*arg, **kw)
        self['version'] = 0

        origin = dict()
        origin['usrname'] = None
        origin['sessid'] = 0
        origin['sessver'] = 0
        origin['nettype'] = None
        origin['addrtype'] = None
        origin['uniaddr'] = None
        self['origin'] = origin

        self['sessname'] = None
        self['sessinfo'] = None
        self['uri'] = None
        self['email'] = None
        self['phone'] = None

        conndata = dict()
        conndata['nettype'] = None
        conndata['addrtype'] = None
        conndata['connaddr'] = None
        self['conndata'] = conndata

        bw = dict()
        bw['bwtype'] = None
        bw['bw'] = 0
        self['bw'] = bw

        time = dict()
        time['start'] = 0
        time['end'] = 0
        self['time'] = time

        #repeat and timezone is not used and complex.
        repeat = dict()
        repeat['rinterval'] = 0
        repeat['activeduation'] = 0
        repeat['offsets'] = 0
        self['repeat'] = repeat

        self['tz'] = list()  #adjust time + offset


        encrypt = dict()
        encrypt['method'] = None
        encrypt['enkey'] = None
        self['encrypt'] = encrypt

        # most complex
        self['attrlist'] = list()

        media = dict()
        media['media'] = None
        media['port'] = 0
        media['numports'] = 0
        media['proto'] = None
        media['fmt'] = None

        self['media'] = media



class SdpParser(object):
    def __init__(self):
        #blocks splited by media line
        self.blocks = list()
        self.sdpmsgs = list()


    def parse(self, msg):
        # 1. split the sdp audio/media part:  m= line as the seperator
        # 2. codec, payload type
        # 3. precondition/stream direct
        #

        #scan the whole body and split
        self.splitSdp(msg)

        #start to parse
        sdppattern = SipPattern['sdppattern']
        sdpregex = re.compile(sdppattern)
        for block in self.blocks:
            onesdpmsg = SdpMsg()
            for index, line in enumerate(block):
                sdp = sdpregex.search(line)
                if sdp:
                    type = sdp.group(1).strip()
                    value = sdp.group(2).strip()
                    print type + '=' + value
                    self.parsesdp(type, value, onesdpmsg)
            self.sdpmsgs.append(onesdpmsg)

    def splitSdp(self, msg):
        start = 0
        mediaregex = re.compile(SipPattern['mediapattern'])
        for index, line in enumerate(msg):
            if mediaregex.search(line):
                print 'media line is ' + line
                oneblock = msg[start:index]
                self.blocks.append(oneblock)
                start = index

        oneblock = msg[start:len(msg)]
        self.blocks.append(oneblock)
        """
        for block in self.blocks:
            print 'oneblock is ' +repr(block)
        """

    def parsesdp(self, type, value, onesdpmsg):
        if type == 'v':
            onesdpmsg['version'] = value
        elif type == 'o':
            originpattern="(\S+) (\d+) (\d+) (IN) (IP[46]) (.+)"
            origin = dict()
            origin['usrname'] = None
            origin['sessid'] = 0
            origin['sessver'] = 0
            origin['nettype'] = None
            origin['addrtype'] = None
            origin['uniaddr'] = None
            origin['usrname'], origin['sessid'], origin['sessver'], origin['nettype'], origin['addrtype'], origin['uniaddr'] \
                = re.match(originpattern, value).groups()
            onesdpmsg['origin'] = origin
        elif type == 's':
            onesdpmsg['sessname'] = value
        elif type == 'i':
            onesdpmsg['sessinfo'] = value
        elif type == 'u':
            onesdpmsg['uri'] = value
        elif type == 'e':
            onesdpmsg['email'] = value
        elif type == 'p':
            onesdpmsg['email'] = value
        elif type == 'c':
            conndata = dict()
            conndata['nettype'] = None
            conndata['addrtype'] = None
            conndata['connaddr'] = None
            cpattern = "(IN) (IP[46]) (.+)"
            conndata['nettype'],conndata['addrtype'], conndata['connaddr'] = re.match(cpattern, value).groups()
            onesdpmsg['conndata'] = conndata
        elif type == 'b':
            bw = dict()
            bw['bwtype'] = None
            bw['bw'] = 0
            bwpattern = "(\w+):(\d+)"
            bw['bwtype'], bw['bw'] = re.match(bwpattern, value).groups()
            onesdpmsg['bw'] = bw
        elif type == 't':
            time = dict()
            time['start'] = 0
            time['end'] = 0
            tpattern =  "(\d+) (\d+)"
            time['start'], time['end'] = re.match(tpattern, value).groups()
            onesdpmsg['time'] = time
        elif type == 'k':
            encrypt = dict()
            encrypt['method'] = None
            encrypt['enkey'] = None
            kpattern="(\w+)(?::(.*))"
            kgroups = re.match(kpattern, value).groups()
            if kgroups:
                encrypt['method'] = kgroups[0]
                if kgroups[1]:
                    encrypt['enkey'] = kgroups[1]
            onesdpmsg['encrypt'] = encrypt
        elif type == 'm':
            media = dict()
            media['media'] = None
            media['port'] = 0
            media['numports'] = 1
            media['proto'] = None
            media['fmt'] = None
            mpattern = "(\w+) (\d+)(?:[/](\d+))? ([^ ]+) (.+)"
            media['media'], media['port'], media['numports'], media['proto'], media['fmt'] = re.match(mpattern, value).groups()
            if not media['numports']:
                media['numports'] = 1
            onesdpmsg['media'] = media
        elif type == 'a':
            onesdpmsg['attrlist'].append(value)

    def parseAttr(self):
        pass

    def parseMediaPl(self):
        pass

    def getsdp(self):
        pass

    def dump(self):
        for sdpmsg in self.sdpmsgs:
            print repr(sdpmsg)

if __name__ == "__main__":
    onesdp = list()
    onesdp.append("v=0")
    onesdp.append("o=anritsu 809 951810 IN IP4 192.168.1.12")
    onesdp.append("s=-")
    onesdp.append("i=A VOIP Session")
    onesdp.append("c=IN IP4 192.168.1.12")
    onesdp.append("t=0 0")
    onesdp.append("m=audio 60000 RTP/AVP 96 97 98 99 100 8 0 101 102")
    onesdp.append("b=AS:153")
    onesdp.append("b=RS:800")
    onesdp.append("b=RR:2400")
    onesdp.append("a=ptime:20")
    onesdp.append("a=maxptime:240")
    onesdp.append("a=rtpmap:96 EVS/16000/1")
    onesdp.append("a=fmtp:96 max-red=220")
    onesdp.append("a=rtpmap:97 AMR-WB/16000/1")
    onesdp.append("a=fmtp:97 mode-change-capability=2")
    onesdp.append("a=rtpmap:98 AMR-WB/16000/1")
    onesdp.append("a=fmtp:98 octet-align=1; mode-change-capability=2")
    onesdp.append("a=rtpmap:99 AMR/8000/1")
    onesdp.append("a=fmtp:99 mode-change-capability=2")
    onesdp.append("a=rtpmap:100 AMR/8000/1")
    onesdp.append("a=fmtp:100 octet-align=1; mode-change-capability=2")
    onesdp.append("a=rtpmap:8 PCMA/8000/1")
    onesdp.append("a=rtpmap:0 PCMU/8000/1")
    onesdp.append("a=rtpmap:101 telephone-event/16000")
    onesdp.append("a=fmtp:101 0-15")    
    onesdp.append("a=rtpmap:102 telephone-event/8000")
    onesdp.append("a=fmtp:102 0-15")
    onesdp.append("a=mid:0")
    onesdp.append("a=rtcp:60001")
    onesdp.append("a=curr:qos local none")
    onesdp.append("a=curr:qos remote none")
    onesdp.append("a=des:qos mandatory local sendrecv")
    onesdp.append("a=des:qos optional remote sendrecv")
    onesdp.append("a=sendrecv")
    onesdp.append("m=video 60002 RTP/AVP 113 114 34")
    onesdp.append("b=AS:416")
    onesdp.append("b=RR:2000")
    onesdp.append("b=RS:600")
    onesdp.append("a=rtpmap:113 H264/90000")
    onesdp.append("a=fmtp:113 profile-level-id=42000B;packetization-mode=0")
    onesdp.append("a=rtpmap:114 H264/90000")
    onesdp.append("a=fmtp:114 profile-level-id=42000B;packetization-mode=1")
    onesdp.append("a=rtpmap:34 H263/90000")
    onesdp.append("a=fmtp:34 profile=0;level=10")
    onesdp.append("a=sendrecv")
    onesdp.append("a=curr:qos local none")
    onesdp.append("a=curr:qos remote none")
    onesdp.append("a=des:qos mandatory local sendrecv")
    onesdp.append("a=des:qos optional remote sendrecv")
    onesdp.append("a=rtcp:60003")
    sp = SdpParser()
    sp.parse(msg=onesdp)    
    sp.dump()
