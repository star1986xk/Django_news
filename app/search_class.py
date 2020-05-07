# -*- coding:utf-8 -*-
from lxml import etree
import urllib3
import time
import requests
from threading import Thread
from rest_framework.viewsets import ModelViewSet
from app import mySerializer
import random
import re
import datetime

class search_class(Thread, ModelViewSet):
    urllib3.disable_warnings()

    def __init__(self, keys_list=None, search_engines=None, page_count=None, get_time=None, flag=None):
        super(search_class, self).__init__()
        self.flag = flag
        self.keys_list = keys_list
        self.search_engines = search_engines
        self.page_count = page_count
        self.get_time = get_time
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            # 'Cookie':'Cookie: ABTEST=7|1585729036|v17; IPLOC=CN2201; SUID=CD1EF43A6D1CA00A000000005E844E0C; SUV=1585729084483710; browerV=3; osV=1; SNUID=24F71DD3E8EC4BDEB8DD42E6E9D6F645; sst0=182; sct=8; ld=kZllllllll2WP9cPlllllVfV5iZlllllnsyW8yllll9llllllklll5@@@@@@@@@@'
        }

    def sina_data(self, div, key):
        try:
            time.sleep(random.uniform(1, 3))
            title_xp = div.xpath('.//h2/a')[0]
            title = title_xp.xpath("string(.)")
            url = div.xpath('.//h2/a/@href')[0]
            author_time = div.xpath('.//h2/span/text()')[0]
            author = author_time.split(' ')[0]
            create_time = ' '.join(author_time.split(' ')[1:])
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            html = etree.HTML(response.text)
            article = html.xpath('//div[contains(@class,"article")]')[0]
            content = etree.tostring(article, encoding="utf-8", pretty_print=True, method="html").decode('utf-8')
            data = {
                'title': title,
                'content': content,
                'author': author,
                'create_time': create_time,
                'keyword': key,
                'url': url,
                'get_time': self.get_time,
                'source': '新浪'
            }
            serializer = mySerializer.NewsTableSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except Exception as e:
            print(e)

    def sina(self, key, page):
        url = 'https://search.sina.com.cn/?q={}&range=all&c=news&sort=time&page={}'
        response = requests.get(url.format(key, page), timeout=10)
        html = etree.HTML(response.text)
        div_list = html.xpath('//div[@class="result"]/div')
        self.task_list = [Thread(target=self.sina_data, args=(div, key)) for div in div_list]
        [task.start() for task in self.task_list]
        [task.join() for task in self.task_list]

    def baidu_data(self, div, key):
        try:
            time.sleep(random.uniform(1, 3))
            title = div.get('title')
            url = div.get('titleurl')
            author = div.get('subsitename')
            posttime = div.get('posttime')
            if '天' in posttime:
                day = re.search('\d*',posttime)
                d = datetime.datetime.now() - datetime.timedelta(int(day[0]))
                create_time = d.strftime('%Y-%m-%d %H:%M:%S')
            elif '小时' in posttime:
                hour = re.search('\d*',posttime)
                h = datetime.datetime.now() - datetime.timedelta(hours= int(hour[0]))
                create_time = h.strftime('%Y-%m-%d %H:%M:%S')
            else:
                create_time = re.sub('[年月日]','-',posttime)
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
            html = etree.HTML(response.text)
            article = html.xpath('//div[contains(@id,"article")]')[0]
            content = etree.tostring(article, encoding="utf-8", pretty_print=True, method="html").decode('utf-8')
            data = {
                'title': title,
                'content': content,
                'author': author,
                'create_time': create_time,
                'keyword': key,
                'url': url,
                'get_time': self.get_time,
                'source': '百度'
            }
            serializer = mySerializer.NewsTableSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except Exception as e:
            print(e)

    def baidu(self, key, page):
        page = page * 10
        url = 'https://m.baidu.com/sf/vsearch?word={}&pd=realtime&tn=vsearch&pn={}&sa=vs_tab&mod=5&p_type=1&data_type=json&atn=index'
        response = requests.get(url.format(key, page), timeout=10)
        div_list = [div for div in response.json()['data']['list']]
        self.task_list = [Thread(target=self.baidu_data, args=(div, key)) for div in div_list]
        [task.start() for task in self.task_list]
        [task.join() for task in self.task_list]

    # 执行函数
    def run(self):
        for key in set(self.keys_list):
            for engines in self.search_engines:
                if engines == '新浪':
                    fun = self.sina
                elif engines == '百度':
                    fun = self.baidu
                for n in range(int(self.page_count)):
                    if self.flag[0]:
                        time.sleep(random.uniform(1, 3))
                        fun(key, n)
        self.flag[0] = False


if __name__ == '__main__':
    keys_list = ['site:xue.com', 'site:hao123.com']
    sc = search_class(keys_list=keys_list, search_engines='sogou', page_count=1)
    # sc.run()
    sc.baidu('李小璐', '1')
