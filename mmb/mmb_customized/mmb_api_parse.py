# -*- coding:utf-8 -*-
import time

import mmb_request
import mmb_db_operation
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class mmb_api_parse():
    key_type = ""
    version = ""

    page_size = 80
    price_min = 0
    price_max = 0
    step = 10000
    max_info = 8000
   
    complete_match_count = 0
    semi_match_count = 0

    mmb_request = mmb_request.mmb_request()
    mmb_db_operation = mmb_db_operation.mmb_db_operation()

    def get_basic(self, search_key, mmb_classid, run_log):
        run_log.run_log("dynamic price_duan")
        first_request = True
        step = self.step
        while True:
            if first_request:
                if self.price_min == self.price_max and self.price_max !=0:
                    self.price_min = self.price_max+1
                else:
                    self.price_min = self.price_max
                self.price_max = 0
                first_request = False

                # self.price_min = self.price_max
                # self.price_max = 0
                # first_request = False

            response = self.mmb_request.request(search_key=search_key, classid=mmb_classid, price_min=self.price_min,
                                             price_max=self.price_max)

            complete_match_count = response.get("SearchCount", 0)
            semi_match_count = response.get("SearchItemsCount", 0)

            if complete_match_count > self.max_info or semi_match_count > self.max_info:
                print "too many info between {0} - {1}".format(str(self.price_min), str(self.price_max))
                if 0 == self.price_max:
                    self.price_max = self.price_min + step
                    step /= 2
                else:
                    if 0 == step:
                        step = 1
                    self.price_max -= step
                    step /= 2

                if 0 != self.price_max - self.price_min:
                    continue
                else:
                    if self.max_info < complete_match_count:
                        complete_match_count = self.max_info
                    if self.max_info < semi_match_count:
                        semi_match_count = self.max_info
					# self.price_max +=1

            page_size = self.page_size
            max_page = semi_match_count / page_size
            if max_page * page_size < semi_match_count:
                max_page += 1
            print "search_key=%s max_page=%s page_size=%s price_min=%s price_max=%s" % (search_key, max_page, page_size, str(self.price_min), str(self.price_max))

            self.complete_match_count += complete_match_count
            self.semi_match_count += semi_match_count
            return max_page, page_size

    def get_json(self, search_key, mmb_classid, page_num, page_size):  # 得到json数据
        response = self.mmb_request.request(search_key=search_key, classid=mmb_classid, price_min=self.price_min,
                                            price_max=self.price_max, page_num=page_num, page_size=page_size)
        return response.get("SearchResultList", [])

    def dict_to_list(self, record):
        return [record["cid"], record["cidname"],
                record["title"], record["brandName"], record["className"], record["classid"],
                record["commentCount"], record["commentUrl"], record["id"], record["siteName"],
                record["siteid"], record["spbh"], record["spname"], record["sppic"],
                record["spprice"], record["spurl"], record["taobaoid"], record["ziying"],
                record["search_key"], record["updatetime"], record["version"]]

    def analysis(self, datum, search_key, cid, cidname):
        records = list()
        for data in datum:
            record = dict()

            record["cid"] = cid
            record["cidname"] = cidname

            title = data.get("TitleHighLighter", "")
            record["title"] = title.replace('<font color="red">', '').replace('</font>', '')
            record["brandName"] = data.get("brandName", "")
            record["className"] = data.get("className", "")
            record["classid"] = data.get("classid", "")
            record["commentCount"] = data.get("commentCount", 0)
            record["commentUrl"] = data.get("commentUrl", "")
            record["id"] = data.get("id", "")
            record["siteName"] = data.get("siteName", "")
            record["siteid"] = data.get("siteid", "")
            record["spbh"] = data.get("spbh", "")
            record["spname"] = data.get("spname", "")
            record["sppic"] = data.get("sppic", "")
            record["spprice"] = data.get("spprice", "")
            record["spurl"] = data.get("spurl", "")
            record["taobaoid"] = data.get("taobaoid", "")
            record["ziying"] = data.get("ziying", "")

            record["search_key"] = search_key
            record["updatetime"] = time.strftime('%Y%m%d', time.localtime(time.time()))
            record["version"] = self.version

            record = self.dict_to_list(record)
            records.append(record)

        return records

    def parse_search_key(self, search_key, mmb_classid, cid, cidname, run_log):
        first_request = True
        while first_request or 0 != self.price_max:
            first_request = False
            max_page, page_size = self.get_basic(search_key, mmb_classid, run_log)
            for page_num in range(1, max_page+1):
                datum = self.get_json(search_key, mmb_classid, page_num, page_size)
                records = self.analysis(datum, search_key, cid, cidname)
                # self.mmb_db_operation.insert(records, cid, self.key_type)
                run_log.run_log("version %s: search_key=%s page_num=%s insert success" % (self.version, search_key, str(page_num)))
        # self.mmb_db_operation.insert_check(cid, cidname, search_key, self.complete_match_count, self.semi_match_count,
        #                                    self.version, self.key_type)

    def process(self, search_key, run_log):
        self.price_min = 0
        self.price_max = 0
        self.complete_match_count = 0
        self.semi_match_count = 0

        cid = search_key[0]
        cidname = search_key[1]
        search_key = search_key[2]
        search_key, mmb_classid = search_key.split("|||")
        
        self.mmb_db_operation.table_init(cid, self.key_type, run_log)
        
        run_log.run_log(search_key+'mmb_db_operation.table_init')

        run_log.run_log("version {0}: search_key={1} is processing".format(self.version, search_key))
        self.parse_search_key(search_key, mmb_classid, cid, cidname, run_log)
        run_log.run_log(search_key+'parse_search_key complete')

        run_log.run_log("version {0}: search_key={1} is completed".format(self.version, search_key))
            
    def start(self, search_key, key_type, version, run_log):
        
        self.mmb_db_operation.table_check_init(key_type, run_log)
        run_log.run_log(search_key[2]+'mmb_db_operation.table_check_init')
        self.key_type = key_type
        self.version = version
        self.process(search_key, run_log)
        run_log.run_log("version {0}: search_key={1} is completed".format(self.version, search_key[2]))
        return "search_key={} completed".format(search_key[2].split('|||')[0])


if __name__ == '__main__':
    obj = mmb_api_parse()
    obj.start([], "words", "19991231235959")
