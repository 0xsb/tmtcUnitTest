# -*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

#some sql table utils
import json
import os

#one sample decorator using closure
def addclosure(before, after):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return before + func(*args, **kwargs) + after
        return wrapper
    return decorator


@addclosure(' (',') ')
def addparentheis(str):
    return str

@addclosure(' ', '')
def addspace(str):
    return str

@addclosure(',', '')
def addcomma(str):
    return str

@addclosure('', ';')
def addsemi(str):
    return str


def build_col(colinfo):
    cstr = colinfo["name"] + addspace(colinfo["type"])
    #FIXME: hardcode here
    if "attr" in colinfo and colinfo["attr"] == 'primary':
        cstr += ' PRIMARY KEY AUTOINCREMENT'
    return cstr



def gen_createstr(tabname, tabinfo):
    createstr = "CREATE TABLE IF NOT EXISTS" + addspace(tabname)
    #'CREATE TABLE IF NOT EXISTS RESULTS (id integer PRIMARY KEY AUTOINCREMENT ,total integer, pass integer,
    # failed integer, skipped integer, starttime TEXT , duration real, procedure TEXT);'
    colstr = ''
    for index, colinfo in enumerate(tabinfo):
        if index == 0:
            colstr = build_col(colinfo)
        else:
            colstr += addcomma(build_col(colinfo))

    createstr += addparentheis(colstr)
    return addsemi(createstr)

def gen_insertstr(tabname, colnames, idata):
    insertstr = "INSERT INTO" + addspace(tabname)
    colstr = ''
    for index, colname in enumerate(colnames):
        if index == 0:
            colstr = colname
        else:
            colstr += addcomma(colname)

    insertstr += addparentheis(colstr) + "VALUES"
    valstr = ''
    for index, data in enumerate(idata):
        data = repr(data)
        if index == 0:
            valstr = data
        else:
            valstr += addcomma(data)
    insertstr += addparentheis(valstr)
    return addsemi(insertstr)

def gen_dropstr(tabname):
    return "DROP TABLE IF EXISTS " + tabname

def gen_selectstr(tabname):
    pass

def gen_colnamestr(tabname):
    return "PRAGMA table_info" + addparentheis(tabname)

def create_table_str_fromfile(tfile):
    """
    file name prefix is the table name
    file content is the table column details
    :param tfile:
    :return:
    """
    tname = os.path.basename(tfile).split('.')[0]
    with open(tfile) as f:
        tabinfo = json.load(f)
        return gen_createstr(tabname=tname, tabinfo=tabinfo)


def TestInFunc():
    tabinfo = list()
    col1 = { "name":"id", "type":"integer", "attr":"primary"}
    tabinfo.append(col1)
    col2 = {"name" :"total", "type":"integer"}
    tabinfo.append(col2)
    print gen_createstr(tabname="RESULTS", tabinfo=tabinfo)
    idata = [1, 1]
    colnames =  list()
    for info in tabinfo:
        colnames.append(info['name'])
    print gen_insertstr(tabname="RESULTS", colnames=colnames, idata=idata)

def TestInFile(file):
    with open(file) as tfile:
        tabinfo = json.load(tfile)
        print gen_createstr(tabname="RESULTS", tabinfo=tabinfo)
        idata = [1, 12, 8, 4, 0, "2018-06-14 12:12:12", "12.123", "none"]
        colnames =  list()
        for info in tabinfo:
            colnames.append(info['name'])
        print gen_insertstr(tabname="RESULTS", colnames=colnames, idata=idata)

if __name__ == '__main__':
    TestInFunc()
    create_table_str_fromfile('./results.json')

