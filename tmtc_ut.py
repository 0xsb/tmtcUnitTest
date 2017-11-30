#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com


from lib.adbhelper import *
from lib.logutils import *
from lib.cmdhelper import *
from lib.logConf import *
import sys
import os
import threading

# 1. env setup
# 2. process goes
# 3. result check

class TmtcUt(object):
    def __init__(self, outdir = './output', loglevel='DEBUG', confdir='', brickdir='',bindir=''):
        self.logger = logConf(debuglevel=loglevel)
        self.outdir = outdir
        self.confdir = confdir
        self.brickdir = brickdir
        self.bindir = bindir
        self.utils = logutils()

        #process report
        self.report = dict()
        """
        1. parse conf
        2. prepare env setup
        """
        self.cmdenv = cmdhelper(confdir=self.confdir)
        self.cmdenv.buildCmd()

        self.adb = adbhelper()
        self.adb.initDevice()
        self.ueconfig = self.cmdenv.getUeConfig()

    def envsetup(self):
        desc = self.cmdenv.getDesc()
        xmls = self.cmdenv.getxmls()
        ueconfig = self.ueconfig
        #push ue's res
        #UE binary: tmtclicent, libavatar_ut.so, liblemon_ut.so,
        bindir = os.path.realpath(self.bindir)
        binary = bindir + '/' + ueconfig['binary']
        self.adb.push(binary, "/system/bin/")
        for index, lib in enumerate(ueconfig['lib']):
            lib = bindir + '/' + lib
            self.adb.push(lib, "/system/lib/")
        #UE config: Provision.ini
        proini = bindir + '/' + ueconfig['config']
        execdir = ueconfig['execdir']
        self.adb.mkdirp(execdir)
        self.adb.push(proini, execdir)

        #sipp xml
        brickdir = os.path.realpath(self.brickdir)
        for index, xml in enumerate(xmls):
            xml = brickdir + '/' + xml
            self.adb.push(xml, execdir)


    def tmtclientthread(self):
        """
        tmtclient thread
        :return:
        """
        binary = self.ueconfig['binary']
        timeouts = self.cmdenv.gettimeouts()

        #tmtclient timeout is the sum of all timeout plus 2
        curtimeout = 2
        for index, timeout in enumerate(timeouts):
            curtimeout = curtimeout + timeout

        tmtccmd = 'adb shell ' + binary

        try:
            self.logger.logger.info('NOTE: start to run '+ tmtccmd + ' with timeout ' + str(curtimeout))
            tmtctask = etask(cmd=tmtccmd, timeout=curtimeout, retry=1)
            tmtctask.run()
        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            estr = str(etype) + ' ' + str(evalue)
            self.logger.logger.info("Unexpected error: " + estr)

        #TODO: add one more check about if all cases are finished.


    def sippthread(self):
        """
        sipp xml thread
        :return:
        """
        sippcmds = self.cmdenv.getsippcmds()
        print str(sippcmds)
        for index, sippcmd in enumerate(sippcmds):
            cmd = sippcmd['cmd']
            timeout = sippcmd['timeout']
            try:
                self.logger.logger.info('NOTE: start to run '+ cmd + ' with timeout ' + str(timeout))
                sipptask = etask(cmd= cmd, timeout=timeout, retry=1)
                sipptask.run()
            except:
                etype = sys.exc_info()[0]
                evalue = sys.exc_info()[1]
                estr = str(etype) + ' ' + str(evalue)
                self.logger.logger.info("Unexpected error: " + estr)



    def ncthread(self):
        """
        netcat thread
        :return:
        """
        nccmds = self.cmdenv.getnccmds()


    def run(self):
        """
        1. run tmtclient process
        2. run SIPp xmls
        3. collect the report after each sce
        4. run nc
        :return:
        """
        #FIXME: etask will block so should use multiprocessing instead!
        """
        tmtcworker = threading.Thread(target=self.tmtclientthread)
        sippworker =  threading.Thread(target=self.sippthread)

        tmtcworker.setDaemon(True)
        sippworker.setDaemon(True)
        tmtcworker.start()
        sippworker.start()
        #tmtclient will end due to etask timeout
        #it will take the longest time to finish.
        sippworker.join()
        tmtcworker.join()
        """
        # run SIPp xml series

        # run nc


if __name__ == '__main__':
    tmtc = TmtcUt(confdir="cases/mt/", brickdir="cases/bricks/",bindir="bin")
    tmtc.envsetup()
    tmtc.run()