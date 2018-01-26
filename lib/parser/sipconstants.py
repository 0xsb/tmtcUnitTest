#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com
"""
1. compact header
2. regex of req, rsp, header
"""
import os
import sys
path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(path+'/../'))

from logutils import *

utils = logutils()

SipCompact = dict()
SipCompact['Accept-Contact'] = 'a'
SipCompact['Referred-By'] = 'b'
SipCompact['Content-Type'] = 'c'
SipCompact['Content-Encoding'] = 'e'
SipCompact['From'] = 'f'
SipCompact['Call-ID'] = 'i'
SipCompact['Supported'] = 'k'
SipCompact['Content-Length'] = 'l'
SipCompact['Contact'] = 'm'
SipCompact['Event'] = 'o'
SipCompact['Refer-To'] = 'r'
SipCompact['Subject'] = 's'
SipCompact['To'] = 't'
SipCompact['Allow-Events'] = 'u'
SipCompact['Via'] = 'v'

SipCompactReverse = utils.revertdict(SipCompact)

SipPattern = dict()
#INVITE sip:service@127.0.0.1:5065 SIP/2.0
SipPattern['reqline'] = "(\w+) ((sip|tel):.*) SIP/2.0"
#SIP/2.0 100 Trying
SipPattern['rspline'] = "SIP/2.0 (\d+) (.*)"
#From: sipp <sip:sipp@127.0.0.1:5060>;tag=22142SIPpTag001
SipPattern['headerline'] = "(.*?):(.*)"
SipPattern['sdppattern'] = "(.)=(.*)"
SipPattern['seperator'] = '\r\n'


SipContent = dict()
SipContent['sdp'] = "application/sdp"
