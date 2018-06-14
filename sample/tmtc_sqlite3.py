# -*- coding=utf-8 -*-
# author: zhihua.ye@spreadrum.com

#TODO:
# 1. case table, result table
# 2. singleton to create db
# 3. parse old report json to store to db.


import os
import sys
import glob
import traceback
import sqlite3
import json


def benchmark(func):
    import time
    def wrapper(*args, **kwargs):
        starttime = time.clock()
        res = func(*args, **kwargs)
        print("{0}, {1}s".format(func.__name__, time.clock() - starttime))
        return res
    return wrapper

@benchmark
def oswalk(dir):
    """
    just to simple test decorator
    :param dir:
    :return:
    """
    for root, dirs, files in os.walk(dir):
        for name in files:
            print(os.path.join(root, name))
        for name in dirs:
            print(os.path.join(root, name))

def connect(sqlitedb):
    conn = sqlite3.connect(sqlitedb)
    return conn

def close(conn):
    conn.close()


def findJson(outputdir, cursor):
    """
    find report.json under dir
    :param dir:
    :return:
    """
    #whole running is start like 2018_05_...
    globpattern = outputdir + "/[2-9][0-9][0-9][0-9]_*/"
    for dname in glob.glob(globpattern):
        fname = dname + 'report.json'
        if os.path.isfile(fname):
            with open(fname) as jsonf:
                reports = json.load(jsonf)
                record = convertDb(reports)

                """
                THIS IS ALWAYS WRONG
                insertsql = "INSERT INTO RESULTS(starttime, procedure) VALUES ({starttime}, {procedure})".format(**record)
                print insertsql
                cursor.execute(insertsql)
                """
                cursor.execute('INSERT INTO RESULTS(total, pass, failed, skipped, starttime, duration, procedure) '
                               'VALUES (?,?,?,?,?,?,?)', (record["total"],record['pass'],record['failed'], record['skipped'],record["starttime"], record['duration'],record["procedure"]))

def convertDb(reports):
    #report is a list
    record = {
        "total": len(reports),
        "failed": 0,
        "pass": 0,
        "skipped": 0,
        "starttime": "",
        "duration": 0,
        "procedure": json.dumps(reports)
    }
    for index, report in enumerate(reports):
        if index == 0:
            record["starttime"] = report["starttime"]

        if report["result"]:
            record["pass"] += 1
        else:
            record["failed"] += 1
        record["duration"] += report["runtime"]
    return record

def sampleSQl(dbname):
    try:
        conn = connect(dbname)
        cursor = conn.cursor()
        cursor.execute(('DROP TABLE IF EXISTS RESULTS ;'))
        #create case table
        # CREATE TABLE IF NOT EXIST
        cursor.execute('CREATE TABLE IF NOT EXISTS RESULTS (id integer PRIMARY KEY AUTOINCREMENT ,total integer, pass integer, failed integer, skipped integer, '
                       'starttime TEXT , duration real, procedure TEXT);')
        cursor.execute('INSERT INTO RESULTS(total, pass, failed, skipped, starttime, duration) VALUES (14, 13, 1, 0, "2018.06.08 18:02:18", 271.54147)')
        cursor.execute('INSERT INTO RESULTS(total, pass, failed, skipped, starttime, duration) VALUES (14, 12, 1, 1, "2018.06.18 18:02:18", 200.123)')

        findJson('../output', cursor)
        conn.commit()
        #dummpy code to get some json column
        cursor.execute('SELECT id, total, pass, starttime, duration,procedure FROM RESULTS')
        rows = cursor.fetchmany(size=3)
        onep = json.loads(rows[2][5])
        print onep[0]

        conn.close()

    except:
        etype,estr,tb = sys.exc_info()
        print 'type is {0}, estr is {1}'.format(etype, estr)
        traceback.print_exc()


if __name__ == '__main__':
    #oswalk('.')
    dbname = "tmtc.db"
    sampleSQl(dbname)
    #findJson('../output')
