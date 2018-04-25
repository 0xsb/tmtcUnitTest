#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

from configobj import ConfigObj,ConfigObjError
import sys


def changeUE(ini, pref):
    """
    :param ini:
    :param pref:  pref is a dict copied from config.json
    :return:
    """
    try:
        config = ConfigObj(ini)
        for key, value in pref.iteritems():
            config['RCS_SIP'][key] = value
        config.write()

    except:
        etype = sys.exc_info()[0]
        evalue = sys.exc_info()[1]
        print "get Unexpected error:"+ str(etype) +' '+str(evalue)


if __name__ == "__main__":
    pref = {
        "VIDEO_CALL": 1,
        "PRECONDITION": 0
    }
    changeUE("../bin/provision.initmp", pref=pref)