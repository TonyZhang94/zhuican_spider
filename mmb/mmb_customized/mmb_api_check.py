# -*- coding:utf-8 -*-
from string import lower

import psycopg2


class mmb_api_check():
    ip = 'postgres-lkr70ecv.gz.cdb.myqcloud.com'
    db_mmb = psycopg2.connect(host=ip, port=62, user='zczx_admin', password='zczx112211',
                              database='crawl_mmb_category')
    print "DB Connect Success--crawl_mmb_category"

    schema = "mmb_api_{0}"
    table = "{0}.{1}_cid{2}"
    key_type = ""

    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p",
                "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
                "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                "/", "-", "+", "*", "(", ")", "[", "]", "{", "}", "'", '"', "\\",
                "?", "~", ":", ";", ",", ".", "%", "&"]

    def get_cids(self, version, search_keys="", is_all="all"):
        schema = self.schema.format(self.key_type)
        table = self.table.format(schema, self.key_type, "check").replace("cid", "")
        if "all" == is_all:
            cur = self.db_mmb.cursor()
            pgSQL = "SELECT * FROM {0} where version = '{1}';" \
                .format(table, version)
            cur.execute(pgSQL)
            datum = cur.fetchall()
            cids = list()
            for data in datum:
                cids.append(data)
            return cids
        else:
            cur = self.db_mmb.cursor()
            cids = list()
            for search_key in search_keys:
                pgSQL = "SELECT * FROM {0} where search_key = '{1}' and version = '{2}';"\
                    .format(table, search_key, version)
                cur.execute(pgSQL)
                datum = cur.fetchall()
                if 0 == len(datum):
                    print "search_key={0}, 不存在".format(search_key)
                else:
                    cids.append(datum[0])
            return cids

    def get_data_count(self, cid, search_key, version):
        schema = self.schema.format(self.key_type)
        table = self.table.format(schema, self.key_type, cid)
        cur = self.db_mmb.cursor()
        pgSQL = "SELECT COUNT(*) FROM {0} where search_key = '{1}' and version = '{2}';" \
            .format(table, search_key, version)
        cur.execute(pgSQL)
        datum = cur.fetchall()
        return datum[0][0]

    def alignment(self, text, x):
        text = text.decode("utf-8")
        slen = len(text)
        if isinstance(text, str):
            blank = ' '
        else:
            blank = u'　'
        while slen < x:
            text = blank + text
            slen += 1

        temp = lower(text)
        for letter in self.alphabet:
            temp = temp.replace(letter, "")
        supple = x - len(temp)
        while supple:
            text = " " + text
            supple -= 1

        return text

    def get_info(self, cid, version):
        record = dict()
        cidname = cid[1].strip()
        search_key = cid[2].strip()
        record["cid"] = cid[0]
        record["cidname"] = self.alignment(cidname, 10)
        record["search_key"] = self.alignment(search_key, 10)
        record["complete_match_count"] = cid[3]
        record["semi_match_count"] = cid[4]
        record["updatetime"] = cid[5]
        record["data_count"] = self.get_data_count(record["cid"], search_key, version)
        return record

    def print_title(self, num):
        print "共有{0}条search_key".format(str(num))
        print "%5s%10s%20s%20s%15s%15s%15s%15s%15s" % \
              ("Inx", "Cid", "CidName", "SearchKey", "UpdateTime", "GivenCount", "DataCount", "Difference", "Percent")
        print "====================================================================================================" \
              "================================="

    def cal_info(self, info):
        difference = info["data_count"] - info["semi_match_count"]
        if 0 == info["semi_match_count"]:
            percent = "--"
        else:
            percent = (round(float(info["data_count"]) / info["semi_match_count"], 4) - 1) * 100
        return difference, percent

    def print_info(self, inx, info, difference, percent):
        try:
            print "%-5s%10s%5s%5s%15s%15s%15s%15s%15s" % \
                  (str(inx + 1) + ".", info["cid"], info["cidname"], info["search_key"], str(info["updatetime"]),
                   info["semi_match_count"], str(info["data_count"]), str(difference), str(percent) + "%")
        except:
            print "%-5s%10s" % \
                  (str(inx + 1) + ".", info["cid"]),
            print info["cidname"] + info["search_key"],
            print "%14s%15s%15s%15s%15s" % \
                    (str(info["updatetime"]), info["semi_match_count"], str(info["data_count"]),
                     str(difference), str(percent) + "%")

    def process_all_search_keys(self, version):
        cids = self.get_cids(version, is_all="all")
        self.print_title(len(cids))
        for inx in range(len(cids)):
            cid = cids[inx]
            info = self.get_info(cid, version)
            difference, percent = self.cal_info(info)
            self.print_info(inx, info, difference, percent)

    def find_problem_search_keys(self, version):
        cids = self.get_cids(version, is_all="all")
        self.print_title(len(cids))
        num = 0
        for cid in cids:
            info = self.get_info(cid, version)
            difference, percent = self.cal_info(info)
            if difference > 100 and percent > 10:
                num += 1
                self.print_info(inx, info, difference, percent)
        print "共有{0}条search_key数据量出入超过范围".format(str(num))

    def process_designed_search_keys(self, version, search_keys):
        cids = self.get_cids(version, search_keys=search_keys, is_all="part")
        self.print_title(len(cids))
        for inx in range(len(cids)):
            cid = cids[inx]
            info = self.get_info(cid, version)
            difference, percent = self.cal_info(info)
            self.print_info(inx, info, difference, percent)

    def introduction(self):
        while True:
            print "请选择模式:"
            print "1. 查看所有search_key"
            print "2. 查看所有数据量出入超过范围的search_key"
            print "3. 查看指定search_key"
            print "0. 重新选择version"
            choice = str(raw_input())
            if choice not in ["1", "2", "3", "0"]:
                print "输入错误，请重新输入"
                continue
            else:
                break
        return choice

    def get_versions(self, version):
        schema = self.schema.format(self.key_type)
        table = self.table.format(schema, self.key_type, "check").replace("cid", "")
        cur = self.db_mmb.cursor()
        if "%" in version:
            pgSQL = "SELECT DISTINCT version FROM {0} where version like '{1}';".format(table, version)
        else:
            pgSQL = "SELECT DISTINCT version FROM {0} where version = '{1}';".format(table, version)
        cur.execute(pgSQL)
        datum = cur.fetchall()
        return datum

    def select_version(self):
        while True:
            print "请选择version:"
            print "1. words: 直接输入version"
            print "2. words: 根据日期查看有哪些version"
            print "3. models: 直接输入version"
            print "4. models: 根据日期查看有哪些version"

            choice = str(raw_input())
            if choice not in ["1", "2", "3", "4"]:
                print "输入错误，请重新输入"
                continue
            elif choice in ["1", "2"]:
                self.key_type = "words"
            elif choice in ["3", "4"]:
                self.key_type = "models"

            if choice in ["1", "3"]:
                print "请输入version:"
                version = str(raw_input())
                versions = self.get_versions(version)
                if 0 == len(versions):
                    print "version {0} 不存在，请重新输入"
                    continue
                else:
                    break
            elif choice in ["2", "4"]:
                print "请输入version年月日或年月（e.g. 20170824 / 201708）:"
                version = str(raw_input())
                versions = self.get_versions(version + "%")
                if 0 == len(versions):
                    print "version {0} 没有找到相关版本，请重新输入"
                else:
                    print "version {0} 找到如下结果：".format(version)
                    for version in versions:
                        print version[0]
                continue

        return version

    def process(self, version):
        while True:
            choice = self.introduction()
            if "1" == choice:
                self.process_all_search_keys(version)
            elif "2" == choice:
                self.find_problem_search_keys(version)
            elif "3" == choice:
                print "请输入search_key,以#结束:"
                search_keys = list()
                while True:
                    search_key = str(raw_input())
                    if "#" == search_key:
                        break
                    else:
                        search_keys.append(search_key)
                if 0 == len(search_keys):
                    print "至少指定一个search_key"
                    continue
                self.process_designed_search_keys(version, search_keys)
            elif "0" == choice:
                return

    def start(self):
        while True:
            version = self.select_version()
            print "version: {0}".format(version)
            self.process(version)

if __name__ == '__main__':
    obj = mmb_api_check()
    obj.start()
