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

class reportObj(dict):
    def __init__(self, *arg, **kw):
        self['result'] = None
        self['desc'] = None
        self['cmd'] = None
        self['timeout'] = None
        super(reportObj, self).__init__(*arg, **kw)


    def addresult(self,result):
        self['result'] =  result

    def adddesc(self,desc):
        self['desc'] = desc

    def addcmd(self, cmd):
        self['cmd'] = cmd

    def addtimeout(self,timeout):
        self['timeout'] = timeout


class TmtcUt(object):
    def __init__(self, outdir = './output', loglevel='DEBUG', confdir='', brickdir='',bindir=''):
        self.logger = logConf(debuglevel=loglevel)
        self.outdir = outdir
        self.confdir = confdir
        self.brickdir = brickdir
        self.bindir = bindir
        self.utils = logutils()

        #process report
        self.report = list()

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
        casename = self.cmdenv.getCasename()
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
        #UE config: provision.ini
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


    def termtmtc(self):
        #adb shell echo -n exit | busybox nc 127.0.0.1 21904
        #FIXME: tmtclient's exit DOES NOT work now...

        termcmd = self.cmdenv.gettermcmd()
        cmd = termcmd['cmd']
        timeout = termcmd['timeout']
        try:
            termtask = eadbshell(cmd=cmd, timeout=timeout)
            termtask.run()
        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            estr = str(etype) + ' ' + str(evalue)
            self.logger.logger.info("Unexpected error: " + estr)

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


        #add one more cmd to exit zsh


    def sippthread(self):
        """
        sipp xml thread
        :return:
        """
        sippcmds = self.cmdenv.getsippcmds()

        #multiprocess , ue need time to start
        time.sleep(self.ueconfig['startuptime'])

        for index, sippcmd in enumerate(sippcmds):
            cmd = sippcmd['cmd']
            timeout = sippcmd['timeout']
            desc = sippcmd['desc']
            try:
                self.logger.logger.info('NOTE: start to run '+ cmd + ' with timeout ' + str(timeout))
                sipptask = eadbshell(cmd=cmd, timeout=timeout)
                sipptask.run()
                #NOTE: if reach here, case PASS.
                onereport = reportObj()
                onereport.addresult(True)
                onereport.addcmd(cmd)
                onereport.addtimeout(timeout)
                onereport.adddesc(desc)
                self.report.append(onereport)
                self.logger.logger.error('report num is ' + str(len(self.report)))
            except:
                etype = sys.exc_info()[0]
                evalue = sys.exc_info()[1]
                estr = str(etype) + ' ' + str(evalue)
                self.logger.logger.info("Unexpected error: " + estr)
                self.checkResult()
                raise utException('case ' + str(index+1) + ' failed\n error is ' + estr)

        #CAUTION: multiprocessing variable is not shared
        #FIXME: maybe use Manager in future
        #so do the check in sipp process
        # add case result check
        self.checkResult()
        self.termtmtc()

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


    def printReport(self):
        #TODO: maybe print all result in html file
        sippcmds = self.cmdenv.getsippcmds()
        casenum = len(sippcmds)
        passnum = len(self.report)
        index = 0
        while index < passnum:
            self.logger.logger.info('Case '+ str(index + 1) + ": " + self.report[index]['desc'] + " Pass")
            index = index + 1

        while index < casenum:
            self.logger.logger.info('Case '+ str(index + 1) + ": " + sippcmds[index]['desc'] + " Failed")
            index = index + 1

    def checkResult(self):
        #just compare the case number.
        casenum = len(self.cmdenv.getsippcmds())
        self.logger.logger.info('report is ' + repr(self.report))
        passnum = len(self.report)
        if casenum == passnum:
            self.logger.logger.info('All the ' + str(casenum) +  " Cases Passed.")
        else:
            self.logger.logger.error("Totally " + str(casenum) + ', Passed: ' + str(passnum))

        self.printReport()


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
        #tmtcprocess = Process(target=self.tmtclientthread)
        #tmtcprocess.daemon = True
        #tmtcprocess.start()


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

        #tmtcprocess.join()


if __name__ == '__main__':
    tmtc = TmtcUt(confdir="cases/mt/", brickdir="cases/bricks/",bindir="bin")
    tmtc.envsetup()
    tmtc.run()
    #TODO: report collect and html?
    #TODO: log collect: cap log is not needed, all log config file in one dir
    #TODO: add some cases check about failed scenarioes