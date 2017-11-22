#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com
"""
1. ut config can be nested configs
2.
"""
from configobj import ConfigObj,ConfigObjError
import sys
from logConf import *
from configconst import *


class ConfAttr(dict):
    def __init__(self, *arg, **kw):
        #define some default values
        self['type'] = ConfigType.slave
        super(ConfAttr, self).__init__(*arg, **kw)


class utconfparser:
    def __init__(self, configfile='', configspec=''):
        self.attr = ConfAttr()
        self.logger = logConf()
        #ut config default should be slave

        try:
            config = ConfigObj(configfile, configspec=configspec, file_error=True)
            #actually ConfigObj has its own validator
            #But seems need to reinvent the wheel
            if self.validator(config):
                if 'type' in config[ConfigSection.desc]:
                    self.attr['type'] = config[ConfigSection.desc]['type']

            else:
                self.logger.logger.error("Invalid Config file.")

        except:
            etype = sys.exc_info()[0]
            evalue = sys.exc_info()[1]
            self.logger.logger.error("Unexpected error:"+ etype +' '+evalue)

    def validator(self, config):
        #quite Simple and Stupid
        if config:
            if ConfigSection.desc in config:
                if ConfigSection.dep in config:
                    if 'inis' in config[ConfigSection.dep] or 'xmls' in config[ConfigSection.dep]:
                        return True
                else:
                    self.logger.logger.error("no 'dependency' in config file")
        return False

    def dumpAttr(self):
        pass

if __name__ == "__main__":
    up = utconfparser(configfile="../cases/mt/config.ini")