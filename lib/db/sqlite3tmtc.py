# -*- coding=utf-8 -*-
#author: zhihua.ye@spreadtrum.com

#simple function to insert data.

import sqlite3
import sqlitehelper
import json
import sys
import os





def json_to_db(report):
    pass

class sqlite3Tmtc(object):
    def __init__(self, dbname):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()
        #use curtab to track table in use.
        self.curtab = None

    def add_table(self, tfile):
        """
        sqlstr = 'CREATE TABLE IF NOT EXISTS RESULTS (id integer PRIMARY KEY AUTOINCREMENT ,total integer, pass integer, ' \
                 'failed integer, skipped integer, starttime TEXT , duration real, procedure TEXT);'
        """
        self.curtab = os.path.basename(tfile).split('.')[0]
        sqlstr = sqlitehelper.create_table_str_fromfile(tfile)
        self.cursor.execute(sqlstr)
        self.conn.commit()

    def insert_record(self, data):
        """
        get column name , only work for mysql
        SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'my_database' AND TABLE_NAME = 'my_table';
        :param tname:
        :param data:
        :return:
        """
        #sqlstr = sqlhelper.insert_table_str(tname, data)
        #self.cursor.execute(sqlstr)
        qstr = sqlitehelper.gen_colnamestr(self.curtab)
        self.cursor.execute(qstr)
        r = self.cursor.fetchall()
        colnames = [ col[1] for col in r]
        istr = sqlitehelper.gen_insertstr(self.curtab, colnames, data)
        self.cursor.execute(istr)
        self.conn.commit()

    def close(self):
        self.conn.close()

if __name__ == '__main__':
    st = sqlite3Tmtc(dbname="tmtcsprd.db")
    st.add_table('./results.json')
    data = [1, 12, 8, 4, 0, "2018-06-14 12:12:12", "12.123", "{}"]
    st.insert_record(data)
    st.close()
