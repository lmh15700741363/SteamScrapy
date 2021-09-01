import scrapy
from steamspider.pipelines import db
from steamspider.items import SteamTagsNumItem
import json

class SteamtagsnumspiderSpider(scrapy.Spider):
    name = 'steamtagsnumspider'
    allowed_domains = ['store.steampowered.com']
    start_urls = ['https://store.steampowered.com/contenthub/querypaginated/tags/TopRated/render/?query=&start=0&count=15&cc=HK&l=schinese&v=4&tag=%E5%8A%A8%E4%BD%9C&tagid=19']

    def parse(self, response):
        item = SteamTagsNumItem()
        result = json.loads(response.body)
        item['rgSolrFacetCounts'] = result['rgSolrFacetCounts']
        yield item
