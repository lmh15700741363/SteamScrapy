import scrapy
from steamspider.pipelines import db
from steamspider.items import SteamAppDetails
import json
from lxml import etree
from urllib.parse import urlencode
import time
import random


class SteamappdetailsSpider(scrapy.Spider):
    name = 'steamappdetails'
    allowed_domains = ['store.steampowered.com']
    start_urls = ['https://store.steampowered.com/contenthub/querypaginated/tags/TopRated/render/?query=&start=0&count=15&cc=HK&l=schinese&v=4&tag=%E5%8A%A8%E4%BD%9C&tagid=19']

    def parse(self, response):
        main_url = 'https://store.steampowered.com/contenthub/querypaginated/tags/TopRated/render/?'
        sql = "select tag_id, tag_name, nums from steam_tags where finish = 'NO' order by nums desc;"
        info = db.select(sql)
        for row in info:
            tag_id = row['tag_id']
            tag_name = row['tag_name']
            nums = row['nums']
            start = 0

            # 获取已爬取的应用id
            sql_exits = "select distinct app_id from steam_app_details;"
            app_exits = db.select(sql_exits)
            app_exits = [row['app_id'] for row in app_exits]
            while start <= nums:
                params = {
                    'query': '',
                    'start': str(start),
                    'count': '15',
                    'cc': 'HK',
                    'l': 'schinese',
                    'v': '4',
                    'tag': tag_name,
                    'tagid': tag_id
                }
                # 重定向地址，获取每页包含应用信息
                url = main_url + urlencode(params)
                print(start)
                yield scrapy.Request(url=url, callback=self.info_parse, meta={'tag_name': tag_name, 'app_exists': app_exits})
                start += 15
                # 间隔2~8秒再获取数据
                time.sleep(random.uniform(5, 15))

            # 已获取完的tag_id，更新其数据库中的状态为yes
            sql_finish = f"update steam_tags set finish = 'YES' where tag_id = {tag_id};"
            db.raw(sql_finish)


    def info_parse(self, response):
        app_exits = response.meta['app_exists']

        tag_name = response.meta['tag_name']
        result = json.loads(response.body)
        data = etree.HTML(result['results_html'], parser=etree.HTMLParser(encoding='utf-8'))
        app_array = data.xpath('//a')
        for app in app_array:
            # 获取该页所有应用的id、名称、url链接
            item = SteamAppDetails()
            href = app.xpath('@href')[0]
            app_name = app.xpath('.//div[@class="tab_item_name"]/text()')[0]
            app_id = app.xpath('@data-ds-appid')[0]
            if app_id in app_exits:
                print(app_id + "已存在")
                continue
            item['href'] = href
            item['app_name'] = app_name
            item['app_id'] = app_id
            item['tag_name'] = tag_name

            # 重定向地址，获取应用详情
            url = f'https://store.steampowered.com/apphoverpublic/{app_id}?review_score_preference=0&l=schinese&pagev6=true'
            yield scrapy.Request(url=url, meta={'item': item}, callback=self.tag_parse)
            # 间隔0~2秒再获取数据
            time.sleep(random.uniform(0, 2))


    def tag_parse(self, response):
        item = response.meta['item']
        data = etree.HTML(response.body, parser=etree.HTMLParser(encoding='utf-8'))
        # 获取发行日期
        try:
            release_date = data.xpath('//div[@class="hover_release"]/span/text()')[0]
        except:
            release_date = None

        #获取评论信息
        reviews = data.xpath('//div[@class="hover_review_summary"]')[0]
        review_counts = ''.join(reviews.xpath('text()')).strip()
        reviews_summary = reviews.xpath('./span/text()')[0]

        # 获取标签信息
        tag_array = data.xpath('//div[@class="hover_tag_row"]/div')
        tag_result = []
        for tag_div in tag_array:
            tag_result.extend(tag_div.xpath('text()'))
        tag_result = ','.join(tag_result)

        # 存入item
        item['release_date'] = release_date
        item['review_summary'] = reviews_summary
        item['review_counts'] = review_counts
        item['tag_all'] = tag_result
        print(item['app_name'])
        yield item

