# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .dbpools import MysqlClient
db = MysqlClient()

class SteamspiderPipeline:
    def process_item(self, item, spider):
        return item

class SteamTagsPipeline:
    def process_item(self, item, spider):
        if spider.name != 'steamtags':
            return item
        db.insert_many(table_name='steam_tags', columns=['tag_id', 'tag_name'], data=[list(item.values())])

class SteanTagsNumPipeline:
    def process_item(self, item, spider):
        if spider.name != 'steamtagsnumspider':
            return item
        result = item['rgSolrFacetCounts']
        print(result)
        for key, value in result.items():
            sql = f"update steam_tags set nums = {value} where tag_id = {key};"
            db.raw(sql)


class SteamAppDetailsPipeling:
    def process_item(self, item, spider):
        if spider.name != 'steamappdetails':
            return item
        columns = list(item.keys())
        result = [list(item.values())]
        db.insert_many(table_name='steam_app_details', columns=columns, data=result)