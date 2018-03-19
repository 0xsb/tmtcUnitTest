#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com
#common log module

import logging
import os
import sys
from time import gmtime, strftime

import logging.config
import logutils

#http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class logConf(object):
    __metaclass__ = Singleton
    def __init__(self, loggername='logparser', logpath="./test.log", debuglevel='DEBUG'):
        self.timestamp = strftime("%Y_%m_%d_%H_%M_%S", gmtime())
        self.utils = logutils.logutils()
        self.logpath = './' + str(self.timestamp) + '.log'
        logFormatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(filename)s - <%(funcName)s> - %(lineno)d - %(message)s')
        rootLogger = logging.getLogger(loggername)
        debuglevel = logging.getLevelName(debuglevel)
        rootLogger.setLevel(debuglevel)
        #truncate before new writing
        fileHandler = logging.FileHandler(self.logpath,mode='w')
        fileHandler.setFormatter(logFormatter)

        rootLogger.addHandler(fileHandler)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        rootLogger.addHandler(consoleHandler)
        self.logger = rootLogger

if __name__ == '__main__':

    lc = logConf(loggername='logparser', logpath='./test.log', debuglevel='DEBUG')
    lc.logger.debug('debug')
    lc.logger.info('info')
    lc.logger.warn('warn')
    lc.logger.error('error')
