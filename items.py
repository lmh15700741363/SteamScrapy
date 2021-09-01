# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SteamspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class SteamTagsItem(scrapy.Item):
    tag_id = scrapy.Field()
    tag_name = scrapy.Field()

class SteamTagsNumItem(scrapy.Item):
    rgSolrFacetCounts = scrapy.Field()

class SteamAppDetails(scrapy.Item):
    app_id = scrapy.Field()
    app_name = scrapy.Field()
    tag_name = scrapy.Field()
    tag_all = scrapy.Field()
    review_summary = scrapy.Field()
    review_counts = scrapy.Field()
    href = scrapy.Field()
    release_date = scrapy.Field()