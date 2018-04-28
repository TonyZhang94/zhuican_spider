# -*- coding:utf-8 -*-
import time
import psycopg2
from tools import db_params



class mmb_db_operation():
 
    db_mmb = psycopg2.connect(host=db_params.PG_SERVER_HOST, port=db_params.PG_SERVER_PORT, user=db_params.PG_SERVER_USER, password=db_params.PG_SERVER_PASS,
                              database='crawl_mmb_category')
        
    schema = "mmb_api_{0}"
    table = "{0}.{1}_cid{2}"

    def get_pcid(self, cid):
        mj_db = psycopg2.connect(host=db_params.PG_SERVER_HOST, port=db_params.PG_SERVER_PORT, user=db_params.PG_SERVER_USER, password=db_params.PG_SERVER_PASS,
                                database='basic')
        conn = mj_db.cursor()
        # sql = "select pcid from charts.mj_cid_tree where c2id = '%s'"%(cid)
        sql = "select pcid from basics.mj_cid_tree where c3id = '%s' or c2id = '%s'" % (cid, cid)
        conn.execute(sql)
        data_tuple = conn.fetchone()
        pcid = 'no'
        if data_tuple:
            pcid = data_tuple[0]

        conn.close()
        return pcid

    def table_init(self, cid, key_type, run_log):
        # schema = self.schema.format(key_type)
        pcid = self.get_pcid(cid)
        schema = "mmb_{0}_pcid_{1}".format(key_type, pcid)
        table = self.table.format(schema, key_type, cid)
        try:
            cur = self.db_mmb.cursor()
            cur.execute("SELECT count(*) FROM " + table + ";")
        except Exception, e:
            cur = self.db_mmb.cursor()
            cur.execute("ROLLBACK;")

            sql_group = 'create schema if not exists ' + schema
            cur.execute(sql_group)

            cur.execute('''CREATE TABLE {0}
                                (cid            VARCHAR,
                                cidname         VARCHAR,
                                title           VARCHAR,
                                brandName       VARCHAR,
                                className       VARCHAR,
                                classid         VARCHAR,
                                commentCount    INTEGER,
                                commentUrl      VARCHAR,
                                id              VARCHAR,
                                siteName        VARCHAR,
                                siteid          VARCHAR,
                                spbh            VARCHAR,
                                spname          VARCHAR,
                                sppic           VARCHAR,
                                spprice         VARCHAR,
                                spurl           VARCHAR,
                                taobaoid        VARCHAR,
                                ziying          VARCHAR,
                                search_key      VARCHAR,
                                updatetime      VARCHAR,
                                version         VARCHAR
                                );'''.format(table))
            run_log.run_log("DB: Table {0} created successfully".format(table))

    def table_check_init(self, key_type, run_log):
        schema = self.schema.format(key_type)
        table = self.table.format(schema, key_type, "check").replace("cid", "")
        try:
            cur = self.db_mmb.cursor()
            cur.execute("SELECT count(*) FROM " + table + ";")
        except Exception, e:
            cur = self.db_mmb.cursor()
            cur.execute("ROLLBACK;")

            sql_group = 'create schema if not exists ' + schema
            cur.execute(sql_group)

            cur.execute('''CREATE TABLE {0}
                                        (cid            VARCHAR,
                                        cidname         VARCHAR,
                                        search_key      VARCHAR,
                                        complete_match_count    INTEGER,
                                        semi_match_count        INTEGER,
                                        updatetime      VARCHAR,
                                        version         VARCHAR
                                        );'''.format(table))
            run_log.run_log("DB: Table {0} created successfully".format(table))

    def get_search_keys(self, key_type):
        schema = "search_key"
        table = "{0}.new_search_key_{1}".format(schema, key_type)
        cur = self.db_mmb.cursor()
        # cur.execute("SELECT * FROM {0};".format(table))
        cur.execute("select key_cid, key_cidname, search_key, mmb_classid from {0};".format(table))
        datum = cur.fetchall()
        result = []
        for item in datum:
            key_cid = item[0]
            key_cidname = item[1]
            search_key = item[2]
            mmb_classid = item[3]
            new_param = search_key+'|||'+mmb_classid
            result.append([key_cid, key_cidname, new_param])
        return result

    def insert(self, datum, cid, key_type):
        while True:
            # schema = self.schema.format(key_type)
            pcid = self.get_pcid(cid)
            schema = "mmb_{0}_pcid_{1}".format(key_type, pcid)
            table = self.table.format(schema, key_type, cid)
            retime = 0
            try:
                cur = self.db_mmb.cursor()
                cur.executemany("""INSERT INTO {0}
                                (cid, cidname, title, brandName, className, classid, commentCount, commentUrl
                                , id, siteName, siteid, spbh, spname, sppic, spprice, spurl, taobaoid, ziying
                                , search_key, updatetime, version)
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                                );""".format(table), datum)

                # self.db_mmb.commit()
                return
            except Exception, e:
                print e
                retime += 1
                self.db_mmb = psycopg2.connect(host=db_params.PG_SERVER_HOST, port=db_params.PG_SERVER_PORT, user=db_params.PG_SERVER_USER, password=db_params.PG_SERVER_PASS,
                              database='crawl_mmb_category')
                print "DB Reconnect Success--crawl_mmb_category--times {0}".format(str(retime))

    def insert_check(self, cid, cidname, search_key, complete_match_count, semi_match_count, version, key_type):
        while True:
            schema = self.schema.format(key_type)
            table = self.table.format(schema, key_type, "check").replace("cid", "")
            retime = 0
            try:
                cur = self.db_mmb.cursor()
                cur.execute("""INSERT INTO {0}
                            (cid, cidname, search_key, complete_match_count, semi_match_count, updatetime, version)
                            VALUES(%s, %s, %s, %s, %s, %s, %s);""".format(table),
                            (cid,
                             cidname,
                             search_key,
                             complete_match_count,
                             semi_match_count,
                             time.strftime('%Y%m%d', time.localtime(time.time())),
                             version), )

                # self.db_mmb.commit()
                return
            except Exception, e:
                print e
                retime += 1
                self.db_mmb = psycopg2.connect(host=db_params.PG_SERVER_HOST, port=db_params.PG_SERVER_PORT, user=db_params.PG_SERVER_USER, password=db_params.PG_SERVER_PASS,
                              database='crawl_mmb_category')
                print "DB Reconnect Success--crawl_mmb_category--times {0}".format(str(retime))

    def process(self):
        models = self.get_search_keys("models")
        words = self.get_search_keys("words")

    def start(self):
        self.process()


if __name__ == '__main__':
    obj = mmb_db_operation()
    obj.start()
