#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com


from lib.adbhelper import *
from lib.logutils import *
from lib.cmdhelper import *
from lib.logConf import *
from lib.ueconfig import *
from lib.jinjagenerator import *
from datetime import datetime
import sys
import os
from multiprocessing import Process, Manager, Value
from lib.report import *
import shutil


# 1. env setup
# 2. process goes
# 3. result check

class utException(Exception):
    def __init__(self, msg):
        super(utException, self).__init__(msg)
        self.message = msg


class TmtcUt(object):
    def __init__(self, outdir = './output', loglevel='DEBUG', confdir='', brickdir='',bindir=''):
        #logConf is single instance
        self.logger = logConf(debuglevel=loglevel)
        self.outdir = outdir
        self.confdir = confdir
        self.brickdir = brickdir
        self.bindir = bindir
        self.utils = logutils()

        self.starttime = datetime.now()
        self.endtime = 0

        #whole case report
        self.casereport = report()


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


    def checkFile(self, file):
        """
        used to avoid duplicated push library or exes
        :return:
        """
        # file exist, check md5
        md5file = file + '.md5'
        if os.path.exists(md5file):
            with open(md5file, 'r') as mfile:
                oldmd5val = mfile.read()
                newmd5val = self.utils.md5sum(file)
            if newmd5val != oldmd5val:
                with open(md5file, 'w+') as mfile:
                    mfile.write(newmd5val)
                    return True
        else:
            #not exist, write md5
            md5val = self.utils.md5sum(file)
            with open(md5file, 'w+') as mfile:
                mfile.write(md5val)
            return True

        return False

    def envsetup(self):
        scenario = self.cmdenv.getDesc()
        xmls = self.cmdenv.getxmls()
        ueconfig = self.ueconfig
        #push ue's res
        #UE binary: tmtclicent, libavatar_ut.so, liblemon_ut.so,
        bindir = os.path.realpath(self.bindir)
        binary = bindir + '/' + ueconfig['binary']
        new = self.checkFile(binary)

        if new:
            self.adb.push(binary, "/system/bin/")

        for index, lib in enumerate(ueconfig['lib']):
            lib = bindir + '/' + lib
            new = self.checkFile(lib)
            if new:
                self.adb.push(lib, "/system/lib/")

        proini = bindir + '/' + ueconfig['config']
        tmpini = proini + '.tmp'
        shutil.copyfile(proini, tmpini)

        changeUE(tmpini,pref=ueconfig['preference'])
        execdir = ueconfig['execdir']
        self.execdir = execdir
        self.adb.mkdirp(execdir)
        dstini = execdir + '/' + ueconfig['config']
        self.adb.push(tmpini, dstini)
        os.remove(tmpini)

        #sipp xml
        brickdir = os.path.realpath(self.brickdir)
        for index, xml in enumerate(xmls):
            xml = brickdir + '/' + xml
            self.adb.push(xml, execdir)

    def getLog(self):
        casestamp = self.execdir.split('/')[-1]
        #casestamp is like MT_call_2018_xxxx
        outputdir = self.outdir + '/' + casestamp
        self.utils.mkdirp(outputdir)
        self.adb.pull(destdir=self.execdir,localdir=outputdir)
        # reorg the dir structures
        # 1. cases : including all xmls, cmd list, provision.ini
        # 2. ue log : mtc , mme log, tcpdump log, profiles dir
        # 3. sipp log:  -trace_err will generate *_errors.log, -trace_calldebug will generate *_calldebug.log
        casedir = outputdir + '/' + "cases"
        uelogdir = outputdir + '/' + "uelog"
        sipplogdir = outputdir + '/' + "sipplog"
        self.utils.mkdirp(casedir)
        self.utils.mkdirp(uelogdir)
        self.utils.mkdirp(sipplogdir)

        #TODO: add sipp/nc runtime logs
        cmdlist = casedir + '/cmdlist'
        nccmds = self.cmdenv.getnccmds()
        sippcmds = self.cmdenv.getsippcmds()
        with open(cmdlist, 'w+') as cfile:
            for index, cmd in enumerate(sippcmds):
                nccmd = nccmds[index]
                sippcmd = sippcmds[index]
                cfile.write("Step " + str(index + 1) + '\n')
                cfile.write("sipp cmd : " + sippcmd['cmd'] + '\n')
                if (nccmd):
                    cfile.write("nc cmd: " + nccmd['cmd'] + '\n')

        self.utils.mv(outputdir + "/provision.ini", casedir)
        self.utils.mv(outputdir + "/*.xml", casedir)

        self.utils.mv(outputdir + "/mtc*.log", uelogdir)
        self.utils.mv(outputdir + "/mme*.log", uelogdir)
        self.utils.mv(outputdir + "/profiles", uelogdir)
        self.utils.mv(outputdir + "/*.cap", uelogdir)
        self.utils.mv(outputdir + "/main*.log", uelogdir)
        self.utils.mv(outputdir + "/*.msg", sipplogdir)
        self.utils.mv(outputdir + "/*_errors.log", sipplogdir)
        self.utils.mv(outputdir + "/*_calldebug.log", sipplogdir)

    def killprocess(self, pname):
        #stop tmtclient
        killp = "killall " + pname
        try:
            stoptask = eadbshell(cmd=killp)
            stoptask.run()
        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            estr = str(etype) + ' ' + str(evalue)
            self.logger.logger.info("Unexpected error: " + estr)


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
        curtimeout = self.ueconfig['startuptime']
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

    def sippthread(self, sharedreport, sipprunning):
        """

        :param sharedreport:
        :param sipprunning:
        :return:
        """
        sippcmds = self.cmdenv.getsippcmds()

        #multiprocess , ue need time to start
        time.sleep(self.ueconfig['startuptime'])

        #run the cmd
        for index, sippcmd in enumerate(sippcmds):
            cmd = sippcmd['cmd']
            timeout = sippcmd['timeout']
            desc = sippcmd['desc']
            substart = datetime.now()
            try:
                self.logger.logger.info('NOTE: start to run sippcmd '+ cmd + ' with timeout ' + str(timeout))
                sipptask = eadbshell(cmd=cmd, timeout=timeout)
                sipprunning[index] = True
                sipptask.run()
                #NOTE: if reach here, case PASS.
                # CAUTION: https://stackoverflow.com/questions/38703907/modify-a-list-in-multiprocessing-pools-manager-dict
                # seems manager list becomes immutable
                # will only append once and NEVER changed.

                subend = datetime.now()
                runtime = (subend - substart).total_seconds()
                onereport = subreport()

                onereport.setresult(True)
                onereport.setcmd(cmd)
                onereport.settimeout(timeout)
                onereport.setdesc(desc)
                onereport.setruntime(runtime)
                sharedreport.append(onereport)
                self.logger.logger.info('case ' + repr(index + 1) + ' result is ' + repr(onereport.getresult()))
            except:
                etype = sys.exc_info()[0]
                evalue = sys.exc_info()[1]
                estr = str(etype) + ' ' + str(evalue)
                self.logger.logger.info("Unexpected error: " + estr)
                #if exception comes here
                subend = datetime.now()
                runtime = (subend - substart).total_seconds()
                if index <= len(sippcmd):
                    onereport = subreport()
                    onereport.setresult(False)
                    onereport.setcmd(cmd)
                    onereport.settimeout(timeout)
                    onereport.setdesc(desc)
                    onereport.setruntime(runtime)
                    sharedreport.append(onereport)

                self.checkResult()
                raise utException('case ' + str(index+1) + ' failed\n error is ' + estr)

        #CAUTION: multiprocessing variable is not shared
        #so do the check in sipp process
        # add case result check
        #self.checkResult()
        #self.termtmtc()

    def ncthread(self, sipprunning):
        """
        netcat thread
        :return:
        """
        #FIXME: need to add sync with sippthread!

        nccmds = self.cmdenv.getnccmds()
        sippcmds = self.cmdenv.getsippcmds()
        time.sleep(self.ueconfig['startuptime'])
        for index, nccmd in enumerate(nccmds):
            #there may be none in nccmds
            cmd = nccmd['cmd']
            timeout = nccmd['timeout']
            wtime = 0
            while not sipprunning[index]:
                wtime += 0.2
                time.sleep(0.2)
                self.logger.logger.info("wait 0.2s for " + sippcmds[index]['cmd'] + " to start")
                if wtime > sippcmds[index-1]["timeout"]:
                    self.logger.logger.error("wait for " + sippcmds[index-1]["timeout"]  + " s"  + sippcmds[index]['cmd'])
                    break

            if cmd != DUMMY_CMD:
                try:
                    self.logger.logger.info('NOTE: start to run nccmd '+ cmd + ' with timeout ' + str(timeout))
                    nctask = eadbshell(cmd=cmd, timeout=timeout)
                    nctask.run()
                except:
                    etype = sys.exc_info()[0]
                    evalue = sys.exc_info()[1]
                    estr = str(etype) + ' ' + str(evalue)
                    self.logger.logger.info("Unexpected error: " + estr)

    # start a thread to collect main log
    # main log can be used to collect media cmd,
    def tcpdumpthread(self):
        timeouts = self.cmdenv.gettimeouts()
        #logcat timeout is the sum of all timeout plus
        #curtimeout = self.ueconfig['startuptime']
        curtimeout = 0
        for index, timeout in enumerate(timeouts):
            curtimeout = curtimeout + timeout

        capname = re.sub(r'[\s+]', '_', self.cmdenv.getCasename())
        tcpdumpcmd = 'adb shell tcpdump -i any -w ' + self.execdir + '/' + capname + '.cap'

        try:
            self.logger.logger.info('NOTE: start to run tcpcmd '+ tcpdumpcmd + ' with timeout ' + str(curtimeout))
            tmtctask = etask(cmd=tcpdumpcmd, timeout=curtimeout, retry=1)
            tmtctask.run()
        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            estr = str(etype) + ' ' + str(evalue)
            self.logger.logger.info("Unexpected error: " + estr)

    def mainlogthread(self):
        timeouts = self.cmdenv.gettimeouts()
        #logcat timeout is the sum of all timeout plus
        #curtimeout = self.ueconfig['startuptime']
        curtimeout = 0
        for index, timeout in enumerate(timeouts):
            curtimeout = curtimeout + timeout

        mainname = re.sub(r'[\s+]', '_', self.cmdenv.getCasename())
        logcatcmd = 'adb shell logcat -s TMTC CPVoiceAgent > ' + self.execdir + '/' + 'main' + mainname + '.log'

        try:
            self.logger.logger.info('NOTE: start to run logcatcmd'+ logcatcmd + ' with timeout ' + str(curtimeout))
            tmtctask = etask(cmd=logcatcmd, timeout=curtimeout, retry=1)
            tmtctask.run()
        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            estr = str(etype) + ' ' + str(evalue)
            self.logger.logger.info("Unexpected error: " + estr)

    def checkResult(self):
        #just compare the case number.
        casenum = len(self.cmdenv.getsippcmds())
        subreports = self.casereport.getsubreports()
        #CAUTION: listProxy is not return list values when using repr
        #self.logger.logger.info('report is ' + repr(subreports))
        #sub case pass count

        passnum = 0

        for index, subreport in enumerate(subreports):
            #self.logger.logger.info('result is ' + repr(subreport.getresult()))
            phrase = " Failed"
            if subreport.getresult():
                passnum += 1
                phrase = " Pass"
            self.logger.logger.info('Case '+ str(index + 1) + ": " + subreport.getdesc() + phrase
                                    + ', takes ' + repr(subreport.getruntime()) + ' s')

        if casenum == passnum:
            self.logger.logger.info('All the ' + str(casenum) + " Cases Passed.")
            self.casereport.setresult(True)
        else:
            self.logger.logger.error("Totally " + str(casenum) + ', Passed: ' + str(passnum))
            self.casereport.setresult(False)

        self.endtime = datetime.now()
        elapsedsec = (self.endtime - self.starttime).total_seconds()
        self.casereport.setruntime(elapsedsec)
        self.logger.logger.info('elapsed time is ' + repr(self.casereport.getruntime()))
        desc = self.cmdenv.getCasename()
        self.casereport.setdesc(desc)
        self.casereport.setcategroy(self.cmdenv.getCategory())
        self.casereport.setstarttime(self.starttime.strftime('%Y.%m.%d %H:%M:%S'))

    def getreport(self):
        return self.casereport

    def run(self):
        """
        1. run tmtclient process
        2. run SIPp xmls
        3. collect the report after each sce
        4. run nc
        :return:
        """

        #sipptread is used to check sipp case pass rate
        manager = Manager()
        #sharedreport is used to shared between processes
        #main process and sip thread
        sharedreport = manager.list()
        self.casereport.setsubreports(sharedreport)

        #sip thread and nc thread should be synced
        sipprunning = manager.list()
        for _ in range(len(self.cmdenv.getsippcmds())):
            sipprunning.append(False)


        logcatprocess = Process(target=self.mainlogthread)
        logcatprocess.daemon = True
        logcatprocess.start()

        #NOTE: etask will block so should use multiprocessing instead!
        #run tcpdump thread
        # AT thread will not be stopped, so AT cmd is not correct anyway.

        tcpdumpprocess = Process(target=self.tcpdumpthread)
        tcpdumpprocess.daemon = True
        tcpdumpprocess.start()

        # run tmtclient
        tmtcprocess = Process(target=self.tmtclientthread)
        tmtcprocess.daemon = True
        tmtcprocess.start()

        # run SIPp xml series
        sippprocess = Process(target=self.sippthread, args=(sharedreport, sipprunning))
        sippprocess.daemon = True
        sippprocess.start()

        # run nc
        ncprocess = Process(target=self.ncthread, args=(sipprunning,))
        ncprocess.daemon = True
        ncprocess.start()

        ncprocess.join()

        sippprocess.join()

        #kill tmtclient
        self.killprocess(pname=self.ueconfig['binary'])
        tmtcprocess.join()

        self.killprocess(pname="tcpdump")
        tcpdumpprocess.join()

        self.killprocess(pname="logcat")
        logcatprocess.join()
        #get log
        self.getLog()

        self.checkResult()

        #analyze logs

if __name__ == '__main__':
    #tmtc = TmtcUt(confdir="cases/mo_status_confirm/", brickdir="cases/bricks/",bindir="bin")
    #tmtc = TmtcUt(confdir="staging_cases/notifyprobation_855991/", brickdir="cases/bricks/",bindir="bin")
    #tmtc = TmtcUt(confdir="cases/reg404_862531/", brickdir="cases/bricks/",bindir="bin")
    tmtc = TmtcUt(confdir="cases/tmtc_demo/", brickdir="cases/bricks/",bindir="bin")
    tmtc.envsetup()
    tmtc.run()
    rjson = tmtc.getreport().todict()
    print json.dumps(rjson, indent=4)
    reports = list()
    reports.append(rjson)
    print reports
    summary = convert(reports)
    temphtml = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "lib/templates",
        "tmtc_report_sample.html"
    )

    print summary
    jinja2 = JinjaGenerator(templatehtml=temphtml, data=summary)
    html = jinja2.render()

    with open("./jinja1.html", "w+") as file:
        file.write(html)

    #TODO: report collect and html?
    #TODO: log collect: cap log is not needed, all log config file in one dir
    #TODO: add some cases check about failed scenarioes