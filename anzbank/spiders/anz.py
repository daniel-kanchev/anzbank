import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from anzbank.items import Article


class AnzSpider(scrapy.Spider):
    name = 'anz'
    start_urls = [
        'https://www.media.anz.com/?adobe_mc=MCMID%3D61960543079305017342306234072764986940%7CMCORGID%3D67A216D751E567B20A490D4C%2540AdobeOrg%7CTS%3D1612535892']

    def parse(self, response):
        links = response.xpath('//h2//a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="component article-date"]/span/text()').get()
        if date:
            date = datetime.strptime(date.strip(), '%B %d, %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="columns"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and 'window.' not in text
                   and not text.startswith('.') and '.column' not in text and ';' not in text]

        content = "\n".join(content[4:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
