#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com
"""
1. ut config can be nested configs
this design is some kind of useless and meaningless.
use json instead.
"""
from configobj import ConfigObj,ConfigObjError
import sys
from logConf import *
from configconst import *


class ConfAttr(dict):
    def __init__(self, *arg, **kw):
        #define some default values
        self['type'] = ConfigType.slave
        self['inis'] = list()
        self['xmls'] = list()
        self['timeout'] = 5
        self['tmtcport'] = 21904
        self['scenario'] = "TMTC test"
        self['tmtccmd'] = None
        super(ConfAttr, self).__init__(*arg, **kw)

    def dump(self):
        for key, value in self.iteritems():
            print 'key is %s, value is %s' % (key,value)

class utconfparser:
    def __init__(self, brickdir='', confdir='', configfile='', configspec=''):
        self.attr = ConfAttr()
        #brick xml dir
        self.brickdir = brickdir
        #case def dir
        self.confdir = confdir

        self.logger = logConf()
        #sub config may still exist.
        self.subconf = list()
        self.config = None
        try:
            conffile = os.path.realpath(confdir + '/' + configfile)
            config = ConfigObj(conffile, configspec=configspec, file_error=True)
            self.config = config
            #remove validate function, just raise exception when keyerror
        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            self.logger.logger.error("Unexpected error:"+ str(etype) +' '+str(evalue))


    def getmaster(self):
        '''

        :return:
        '''
        try:
            config = self.config
            self.attr['inis'] = convertList(config[ConfigSection.dep]['inis'])
            if checkFlistType(self.attr['inis'], 'ini'):
                #parse subconfs
                for index, ini in enumerate(self.attr['inis']):
                    inipath = os.path.realpath(self.confdir + '/' + ini)
                    inidirname = os.path.dirname(inipath)
                    subcon = utconfparser(brickdir=self.brickdir, confdir=inidirname, configfile=ini)
                    subcon.getattr()
                    self.subconf.append(subcon)
            else:
                emsg = "type is not all ini files"
                raise ConfigException(emsg)

            if keyInSection(config,  ConfigSection.desc, 'scenario'):
                self.attr['scenario'] = config[ConfigSection.desc]['scenario']

        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            self.logger.logger.error("Unexpected error:"+ str(etype) + ' ' +str(evalue))


    def getslave(self):
        config = self.config
        try:
            self.attr['xmls'] = convertList(config[ConfigSection.dep]['xmls'])

            if not checkFlistType(self.attr['xmls'], 'xml'):
                emsg = "type is not all xml files"
                raise ConfigException(emsg)

            #########critical data is collected here.
            #collect port
            if keyInSection(config,  ConfigSection.param, 'timeout'):
                self.attr['timeout'] = config[ConfigSection.param]['timeout']
            #collect timeout
            if keyInSection(config,  ConfigSection.param, 'tmtcport'):
                self.attr['tmtcport'] = config[ConfigSection.param]['tmtcport']

            if keyInSection(config,  ConfigSection.param, 'tmtccmd'):
                self.attr['tmtccmd'] = config[ConfigSection.param]['tmtccmd']

            if keyInSection(config,  ConfigSection.desc, 'scenario'):
                self.attr['scenario'] = config[ConfigSection.desc]['scenario']


        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            self.logger.logger.error("Unexpected error:" + str(etype) + ' ' +str(evalue))


    def getattr(self):
        """
        master, slave need different attr
        master need: inis
        slave need:  xmls
        :return:
        """
        config = self.config

        try:
            if keyInSection(config, section=ConfigSection.desc, key='type'):
                self.attr['type'] = config[ConfigSection.desc]['type']
            if isMasterConf(self.attr['type']):
                self.getmaster()
            elif isSlaveConf(self.attr['type']):
                self.getslave()
            else:
                emsg = "Not valid Type"
                self.logger.logger.error(emsg)
                raise ConfigException(emsg)
            self.attr.dump()
        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            self.logger.logger.error("Unexpected error:"+ str(etype) +' '+str(evalue))


    def collectsubconf(self):
        pass

if __name__ == "__main__":
    up = utconfparser(brickdir="../cases/bricks/", confdir='../cases/mt/', configfile="config.ini")
    up.getattr()