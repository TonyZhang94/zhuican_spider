# -*- coding:utf-8 -*-
import json
import random
import time
import urllib
from tools.write_log import ErrorLog
import codecs
import requests
from bs4 import BeautifulSoup


class mmb_request():
    Appkey = 'c2MyspriI6GGT9VD'
    url_model = "http://sapi.manmanbuy.com/Search.aspx?AppKey={0}&Key={1}&Class={2}&Brand={3}&Site=0&PriceMin={4}" \
                "&PriceMax={5}&PageNum={6}&PageSize={7}&OrderBy=score&ZiYing=false&ExtraParameter=0"

    def generate_url(self, search_key, classid=0, brand=0, price_min=0, price_max=0, page_num=1, page_size=80):
        search_key = urllib.quote(search_key.decode('utf-8').encode('gbk'))
        url = self.url_model.format(self.Appkey, search_key, str(classid), str(brand), str(price_min), str(price_max),
                                    str(page_num), str(page_size))
        return url

    def get_content(self, url):
        try:
            content = requests.get(url, timeout=10).content
            content = content.decode("GB18030")
            response = json.loads(content)
            return response
        except requests.Timeout:
            print 'timeout...sleep 60s, url:{}'.format(url)
            time.sleep(60)
            return None
        except:
            content = '{"State":1000,"SearchItemsCount":0,"SearchCount":0,"ClassList":"","BrandList":"",' \
                      '"SiteList":"","SearchResultList":[]}'
            response = json.loads(content)
            return response

    def request(self, search_key, classid=0, brand=0, price_min=0, price_max=0, page_num=1, page_size=80,
                early_start=1, later_start=3):
        url = self.generate_url(search_key=search_key, classid=classid, brand=brand, price_min=price_min,
                                price_max=price_max, page_num=page_num, page_size=page_size)
      
        print 'url', url
        while True:
            gap = random.random() * later_start + early_start
            time.sleep(gap)
            while True:
                response = self.get_content(url)
                if response:
                    break
            if 1000 == response.get("State"):
                # print "Request Success: search_key={0} page_num={1}".format(search_key, str(page_num))
                return response
            elif 1001 == response.get("State"):
                error_log = ErrorLog(search_key.decode('utf-8').encode('gbk'))
                error_log.error_log(url+'\n')
                error_log.error_log("Error Parameter: search_key={0} page_num={1}".format(search_key, str(page_num)))
                exit()
            elif 1002 == response.get("State"):
                error_log = ErrorLog(search_key.decode('utf-8').encode('gbk'))
                error_log.error_log(url+'\n')
                error_log.error_log("Error AppKey: search_key={0} page_num={1}".format(search_key, str(page_num)))
                exit()
            elif 1003 == response.get("State"):
                error_log = ErrorLog(search_key.decode('utf-8').encode('gbk'))
                error_log.error_log(url + '\n')
                error_log.error_log("AppKey Used Too Frequently: search_key={0} page_num={1}".format(search_key, str(page_num)))
                gap = random.random() * 20 + 10
                time.sleep(gap)

    def process(self):
        pass

    def start(self):
        self.process()


if __name__ == '__main__':
    obj = mmb_request()
    obj.start()
