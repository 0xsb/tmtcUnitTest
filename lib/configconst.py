#-*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com
"""
conf parser constants
"""


class ConfigSection:
    desc="description"
    dep="dependency"
    param="paramters"


class ConfigType:
    master="master"
    slave="slave"

class ConfigException(Exception):
    def __init__(self, message):
        super(ConfigException, self).__init__(message)
        self.message = message


def configHasSection(config, sectionname):
    if sectionname in config:
        return True
    else:
        return False


def isFile(fname, ftype):
    if fname:
        fields = fname.split('.')
        postfix = fields[1]

        if postfix == ftype:
            return True
        else:
            return False


def checkFlistType(flist, ftype):
    for index, onefile in enumerate(flist):
        if isFile(onefile, ftype) is False:
            return False
    return True

def convertList(value):
    if not isinstance(value, list):
        ret = list()
        ret.append(value)
        return ret
    else:
        return value

def isMasterConf(ftype):
    if ftype == ConfigType.master:
        return True
    else:
        return False


def isSlaveConf(ftype):
    if ftype == ConfigType.slave:
        return True
    else:
        return False

