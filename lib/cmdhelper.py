#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

"""
1. assemble sipp cmd
sipp -sf reg.xml -p 5060 -t u1 -m 1 -trace_err
2. assemble tmtc cmd
echo -n "c-reg" | busybox nc 127.0.0.1 21904

"""

import sys
import json
import os
from logConf import *
from utjsonparser import *


class CmdException(Exception):
    def __init__(self, message):
        super(CmdException, self).__init__(message)
        self.message = message


class cmdObj(dict):
    def __init__(self, *arg, **kw):
        self['cmd'] = ''
        self['timeout'] = None
        super(cmdObj, self).__init__(*arg, **kw)


class cmdhelper:
    def __init__(self, confdir=''):
        self.confdir = confdir
        self.config = dict()
        self.logger = logConf()
        conffile = os.path.realpath(confdir) + '/config.json'
        try:
            with open(conffile, 'r') as conf:
                self.config = json.load(conf)
        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            estr = str(etype) +' '+str(evalue)
            self.logger.logger.error("Unexpected error:"+ estr)
            raise(CmdException(estr))


        #extract info
        self.xmls = list()
        self.timeouts = list()

        #real cmd list
        self.sippcmds = list()
        self.nccmds = list()

    def getDesc(self):
        desc = self.config['description']
        self.logger.logger.info('scenario is ' + desc['scenario'])
        self.logger.logger.info('bug id is ' + str(desc['bugid']) + ', commit id is '+ str(desc['commitid']))

    def getUeConfig(self):
        ueconfig = dict()
        ueconfig['tmtcport'] = 21904
        ueconfig['execdir'] = "/data/data/ut/"
        ueconfig['config'] =  "provision.ini"
        ueconfig['binary'] = 'tmtclient'
        ueconfig['lib'] = [
                  "libavatar_ut.so",
                  "liblemon_ut.so"
        ]

        if 'tmtcport' in self.config['ue']:
            ueconfig['tmtcport'] = self.config['ue']['tmtcport']

        if 'execdir' in self.config['ue']:
            ueconfig['execdir'] = self.config['ue']['execdir']

        if 'config' in self.config['ue']:
            ueconfig['config'] = self.config['ue']['config']

        if 'binary' in self.config['ue']:
            ueconfig['binary'] = self.config['ue']['binary']

        if 'lib' in self.config['ue']:
            ueconfig['lib'] = self.config['ue']['lib']

        return ueconfig

    def buildCmd(self):
        cases = self.config['cases']
        for index,case in enumerate(cases):
            try:
                #init
                sippcmd = cmdObj()
                nccmd = cmdObj()

                xml = case['xml']
                timeout = case['timeout']
                tmtccmd = case['tmtccmd']
                self.xmls.append(xml)
                self.timeouts.append(timeout)

                if validCmd(tmtccmd) is False:
                    tmtccmd = None


                if xml:
                    sippcmd = self.buildsipp(xml, timeout)
                if tmtccmd:
                    nccmd = self.buildnc(tmtccmd)

                self.sippcmds.append(sippcmd)
                self.nccmds.append(nccmd)

            except:
                #most likely KeyError
                etype = sys.exc_info()[0]
                evalue = sys.exc_info()[1]
                estr = str(etype) +' '+str(evalue)
                self.logger.logger.error("Unexpected error:"+ estr)
                raise(CmdException(estr))

    def buildsipp(self, xml='', timeout=None):
        """
        adb shell sipp -sf reg.xml -p 5060 -t u1 -m 1 -trace_err
        :return:
        """
        #FIXME: there is no way to get sipp's return
        #
        sippcmd = cmdObj()
        sippcmd['cmd'] = "adb shell sipp -sf " + xml + ' -p 5060 -t u1 -m 1 -trace_err'
        sippcmd['timeout'] = timeout

        return sippcmd

    def buildnc(self, cmd=''):
        """
        adb shell echo -n "c-reg" | busybox nc 127.0.0.1 21904
        use loopback device and tmtc listening on 21904

        :return:
        """
        tmtcport = 21904
        if 'tmtcport' in self.config['ue']:
            tmtcport = self.config['ue']['tmtcport']

        nccmd = cmdObj()
        nccmd['cmd'] =  "adb shell echo -n " + cmd + ' | busybox nc 127.0.0.1 ' + str(tmtcport)
        #FIXME: nc should be responsed quickly, hardcoded here.
        nccmd['timeout'] = 1
        return nccmd

    def getxmls(self):
        return self.xmls

    def gettimeouts(self):
        return self.timeouts

    def getsippcmds(self):
        return self.sippcmds

    def getnccmds(self):
        return self.nccmds


    def printCmds(self):

        for index, sipp in enumerate(self.sippcmds):
            self.logger.logger.info("< Flow No." + str(index+1) + ' >')
            self.logger.logger.info('sippcmd is  ' + sipp['cmd'] + ', timeout is ' + str(sipp['timeout']))
            self.logger.logger.info('netcat cmd is  ' + self.nccmds[index]['cmd'] +
                                    ', timeout is ' + str(self.nccmds[index]['timeout']))

if __name__ == '__main__':
    cmd = cmdhelper(confdir="../cases/mt/")
    cmd.getDesc()
    ueconfig = cmd.getUeConfig()
    cmd.buildCmd()
    cmd.printCmds()

