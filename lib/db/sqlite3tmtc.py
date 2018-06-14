# -*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

#simple function to insert data.

import sqlite3
import sqlitehelper
import json
import sys
import os
import glob


def find_report(outputdir):
    #whole running is start like 2018_05_...
    globpattern = outputdir + "/[2-9][0-9][0-9][0-9]_*/"
    records = list()
    for dname in glob.glob(globpattern):
        fname = dname + 'report.json'
        if os.path.isfile(fname):
            with open(fname) as jsonf:
                report = json.load(jsonf)
                record = json_to_record(report)
                #print record
                records.append(record)
    return records

def json_to_record(report):
    """
    some report.json is old file, just convert to db data
    record is just a list
    :param report:
    :return:
    """
    total = len(report)
    passed = failed = skipped = duration = 0
    starttime = ''
    for index, content in enumerate(report):
        if index == 0:
            starttime = content["starttime"]
        if content["result"]:
            passed += 1
        else:
            failed += 1
        duration += content["runtime"]
    procedure = json.dumps(report)
    return tuple([total,passed, failed, skipped, starttime, duration, procedure])

class sqlite3Tmtc(object):
    def __init__(self, dbname):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()
        #use curtab to track table in use.
        self.curtab = None
        self.colnames = list()

    def set_cols(self):
        qstr = sqlitehelper.gen_colnamestr(self.curtab)
        self.cursor.execute(qstr)
        r = self.cursor.fetchall()
        self.colnames = [col[1] for col in r]

    def add_table(self, tfile):
        """
        sqlstr = 'CREATE TABLE IF NOT EXISTS RESULTS (id integer PRIMARY KEY AUTOINCREMENT ,total integer, pass integer, ' \
                 'failed integer, skipped integer, starttime TEXT , duration real, procedure TEXT);'
        """
        self.curtab = os.path.basename(tfile).split('.')[0]
        #set colnames
        self.set_cols()
        sqlstr = sqlitehelper.create_table_str_fromfile(tfile)
        self.cursor.execute(sqlstr)
        self.conn.commit()

    def insert_onerecord(self, data):
        """
        just add one record now...
        get column name , only work for mysql
        SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'my_database' AND TABLE_NAME = 'my_table';
        :param tname:
        :param data:
        :return:
        """
        istr = sqlitehelper.gen_insertstr(self.curtab, self.colnames)
        try:
            with self.conn:
                self.conn.execute(istr, data)
        except sqlite3.IntegrityError:
            print "couldn't run " + istr

    def insert_records(self, datas):
        istr = sqlitehelper.gen_insertstr(self.curtab, self.colnames)
        try:
            with self.conn:
                self.conn.executemany(istr, datas)
        except sqlite3.IntegrityError:
            print "couldn't run " + istr


    def close(self):
        self.conn.close()

if __name__ == '__main__':
    st = sqlite3Tmtc(dbname="tmtcsprd.db")
    st.add_table('./results.json')
    data = (12, 8, 4, 0, "2018-06-14 12:12:12", "12.123", "{}")
    st.insert_onerecord(data)
    records = find_report('../../output/')

    st.insert_records(records)

    for record in records:
        print record
        st.insert_onerecord(record)

    st.close()

