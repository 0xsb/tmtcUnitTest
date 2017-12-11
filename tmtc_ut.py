#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com


from lib.adbhelper import *
from lib.logutils import *
from lib.cmdhelper import *
from lib.logConf import *
import sys
import os
from multiprocessing import Process

# 1. env setup
# 2. process goes
# 3. result check

class utException(Exception):
    def __init__(self, msg):
        super(utException, self).__init__(msg)
        self.message = msg


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
        #get ueconfig first
        self.ueconfig = self.cmdenv.getUeConfig()
        self.execdir = ''
        #build cmd
        self.cmdenv.buildCmd()

        self.adb = adbhelper()
        self.adb.initDevice()


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
        self.execdir = execdir
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

        #tmtclient timeout is the sum of all timeout plus
        curtimeout = self.ueconfig['startuptime'] + 2
        for index, timeout in enumerate(timeouts):
            curtimeout = curtimeout + timeout

        tmtccmd = 'adb shell ' + ' cd ' + self.execdir+ '&&' + binary

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
        #add one more cmd to exit zsh


    def sippthread(self):
        """
        sipp xml thread
        :return:
        """
        sippcmds = self.cmdenv.getsippcmds()

        #multiprocess , ue need time to start
        time.sleep( self.ueconfig['startuptime'])

        for index, sippcmd in enumerate(sippcmds):
            cmd = sippcmd['cmd']
            timeout = sippcmd['timeout']
            try:
                self.logger.logger.info('NOTE: start to run '+ cmd + ' with timeout ' + str(timeout))
                sipptask = eadbshell(cmd=cmd, timeout=timeout)
                sipptask.run()

            except:
                etype = sys.exc_info()[0]
                evalue = sys.exc_info()[1]
                estr = str(etype) + ' ' + str(evalue)
                self.logger.logger.info("Unexpected error: " + estr)
                #raise utException('case ' + str(index+1) + 'failed :' + estr)

    def ncthread(self):
        """
        netcat thread
        :return:
        """
        nccmds = self.cmdenv.getnccmds()
        sippcmds = self.cmdenv.getsippcmds()

        time.sleep( self.ueconfig['startuptime'])
        for index, nccmd in enumerate(nccmds):
            cmd = nccmd['cmd']
            timeout = nccmd['timeout']
            try:

                #nccmd need to exec after previous sipp is running
                if index > 0:
                    waitsipptime = sippcmds[index-1]['timeout']
                    waitsippcmd = sippcmds[index-1]['cmd']
                    self.logger.logger.info('wait sipp ' + waitsippcmd + ' to exec ' + str(waitsipptime))
                    time.sleep(waitsipptime)

                self.logger.logger.info('NOTE: start to run '+ cmd + ' with timeout ' + str(timeout))
                nctask = eadbshell(cmd=cmd, timeout=timeout)
                nctask.run()
            except:
                etype = sys.exc_info()[0]
                evalue = sys.exc_info()[1]
                estr = str(etype) + ' ' + str(evalue)
                self.logger.logger.info("Unexpected error: " + estr)

    def run(self):
        """
        1. run tmtclient process
        2. run SIPp xmls
        3. collect the report after each sce
        4. run nc
        :return:
        """
        #NOTE: etask will block so should use multiprocessing instead!
        # run tmtclient
        tmtcprocess = Process(target=self.tmtclientthread)
        tmtcprocess.daemon = True
        tmtcprocess.start()


        # run SIPp xml series
        sippprocess = Process(target=self.sippthread)
        sippprocess.daemon = True
        sippprocess.start()

        # run nc
        ncprocess = Process(target=self.ncthread)
        ncprocess.daemon = True
        ncprocess.start()


        ncprocess.join()
        sippprocess.join()
        tmtcprocess.join()

        # sipp have the timeout
        #nc will not hang so no need to timeout

if __name__ == '__main__':
    tmtc = TmtcUt(confdir="cases/mt/", brickdir="cases/bricks/",bindir="bin")
    tmtc.envsetup()
    tmtc.run()