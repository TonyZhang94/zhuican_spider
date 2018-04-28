# -*- coding:utf-8 -*-
import csv

import time
import mmb_db_operation
import mmb_api_parse


class manager():
    mmb_db_operation = mmb_db_operation.mmb_db_operation()
    mmb_api_parse = mmb_api_parse.mmb_api_parse()

    def read_file(self, key_type):
        file_name = "mmb_search_key_{0}.csv".format(key_type)
        while True:
            print "请确认search_keys已经以正确格式写入{0}".format(file_name)
            print "输入0确认"
            confirm = str(raw_input())
            if "0" == confirm:
                break

        datum = list()
        with open(file_name, "r") as file_obj:
            lines = csv.reader(file_obj)
            for line in lines:
                datum.append(line[0].split(";"))
        file_obj.close()
        return datum

    @staticmethod
    def generate_version():
        return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

    def round_words(self):
        key_type = "words"
        while True:
            version = self.generate_version()
            print "version: {0}".format(version)
            search_keys = self.mmb_db_operation.get_search_keys(key_type)
            self.mmb_api_parse.start(search_keys, key_type, version)

    def round_models(self):
        key_type = "models"
        while True:
            version = self.generate_version()
            print "version: {0}".format(version)
            search_keys = self.mmb_db_operation.get_search_keys(key_type)
            self.mmb_api_parse.start(search_keys, key_type, version)

    def round_words_and_models(self):
        while True:
            version = self.generate_version()
            print "version: {0}".format(version)
            # read database
            search_keys = self.mmb_db_operation.get_search_keys("words")
            self.mmb_api_parse.start(search_keys, key_type="words", version=version)
            search_keys = self.mmb_db_operation.get_search_keys("models")
            self.mmb_api_parse.start(search_keys, key_type="models", version=version)

    def designed_words(self):
        key_type = "words"
        version = self.generate_version()
        print "version: {0}".format(version)
        search_keys = self.read_file(key_type)
        self.mmb_api_parse.start(search_keys, key_type, version)

    def designed_models(self):
        key_type = "models"
        version = self.generate_version()
        print "version: {0}".format(version)
        search_keys = self.read_file(key_type)
        self.mmb_api_parse.start(search_keys, key_type, version)
        
# 以下代码与django无关 'l'
    def introduction(self):
        while True:
            print "请选择模式:"
            print "1. 循环爬取所有words"
            print "2. 循环爬取指定models"
            print "3. 循环爬取所有words和指定models"
            print "4. 单次爬取指定words"
            print "5. 单次爬取指定models"
            choice = str(raw_input())
            if choice not in ["1", "2", "3", "4", "5"]:
                print "输入错误，请重新输入"
                continue
            else:
                break
        return choice

    def process(self):
        choice = self.introduction()
        if "1" == choice:
            self.round_words()
        elif "2" == choice:
            self.round_models()
        elif "3" == choice:
            self.round_words_and_models()
        elif "4" == choice:
            self.designed_words()
        elif "5" == choice:
            self.designed_models()

    def start(self):
        self.process()


if __name__ == '__main__':
    obj = manager()
    obj.start()
