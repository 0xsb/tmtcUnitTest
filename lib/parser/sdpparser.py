import os
import re
import sys
from sipconstants import *
path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(path+'/../'))

from logConf import *

# one sample
# https://github.com/sparkslabs/kamaelia/blob/master/Code/Python/Kamaelia/Kamaelia/Protocol/SDP.py


class SdpParser(object):
    def __init__(self):
        pass

    def parse(self, msg):
        # 1. split the sdp audio/media part:  m= line as the seperator
        # 2. codec, payload type
        # 3. precondition/stream direct
        #

        #scan the whole body and split

        sdppattern = SipPattern['sdppattern']
        sdpregex = re.compile(sdppattern)
        for index, line in enumerate(msg):
            sdp = sdpregex.search(line)
            if sdp:
                type = sdp.group(1).strip()
                value = sdp.group(2).strip()
                print type + '=' + value

    def splitSdp(self):
        pass

    def parsesdp(self, subpart):
        pass

    def getsdp(self):
        pass

    def dump(self):
        pass

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
