import scrapy
from steamspider.items import SteamTagsItem

# 获取steam中tag_id及对应的tag_name

class SteamtagsSpider(scrapy.Spider):
    name = 'steamtags'
    allowed_domains = ['store.steampowered.com']
    start_urls = ['https://store.steampowered.com/tag/browse/']

    def parse(self, response):
        item = SteamTagsItem()
        tag_array = response.xpath('//div[@id="tag_browse_global"]/div')
        for tag_info in tag_array:
            item['tag_id'] = tag_info.xpath('@data-tagid').get()
            item['tag_name'] = tag_info.xpath('text()').get()
            yield item