import scrapy
from datetime import datetime, timedelta
import re
import os
from scrapy.exceptions import CloseSpider
from utils import load_to_elastic


class DetikNewsSpider(scrapy.Spider):
    name = "detiknews"
    allowed_domain = [
        "news.detik.com",
    ]
    # start_urls = [
    #     "https://news.detik.com/indeks",
    # ]
    base_url = "https://news.detik.com/indeks"

    def __init__(self, start_date=None, end_date=None, hourly=True, *args, **kwargs):
        super(DetikNewsSpider, self).__init__(*args, **kwargs)

        self.start_date = None  # "2020-08-06" #None hari ini doang
        self.end_date = None  # "2020-08-14" #None hari ini doang

        self.hourly = True  # False #True per jam

        if self.start_date != None and self.end_date != None:
            self.start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            self.end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
            print(self.start_date, self.end_date, "yosss")
            if self.start_date >= self.end_date:
                raise scrapy.exceptions.CloseSpider(
                    reason="Start date must be lower than end date"
                )

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def start_requests(self):
        _ranged = [
            self.base_url,
        ]

        if self.start_date != None and self.end_date != None:
            _ranged = []

            for date in self.daterange(
                self.start_date, self.end_date + timedelta(days=1)
            ):
                _ranged.append(
                    "{}?date={:02d}%2F{:02d}%2F{}".format(
                        self.base_url, date.month, date.day, date.year
                    )
                )

        for url in _ranged:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for article_url in response.css(".media__title  > a::attr(href)").extract():
            yield scrapy.Request(
                response.urljoin("{}?single=1".format(article_url)),
                callback=self.parse_article_page,
            )

        next_link = response.css(".pagination > a")[-1]
        next_page = next_link.css("::attr(href)").extract_first()

        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_article_page(self, response):
        item = {
            "source": "detiknews",
            "type": "article",
            "slug": response.request.url,
        }

        # Get category
        breadcrumb_link = response.css(".page__breadcrumb > a")[-1]
        item["category"] = breadcrumb_link.css("::text").extract_first()

        data = response.css("article.detail")
        header = data.css(".detail__header")
        media = data.css(".detail__media")
        content = data.css(".detail__body")
        tags = data.css(".detail__body-tag")

        # Get title
        title = header.css("h1.detail__title::text").extract_first()
        item["title"] = None
        if title:
            item["title"] = (
                title.replace("\n         ", "").replace("    ", "").replace("\n", "")
            )

        # Get author
        author = header.css(".detail__author::text").extract_first()
        item["author"] = None
        if author:
            item["author"] = author.replace(" - detikNews", "")

        # Get date (String)
        monthChanger2 = {
            "Jan": "01",
            "Feb": "02",
            "Mar": "03",
            "Apr": "04",
            "May": "05",
            "Mei": "05",
            "Jun": "06",
            "Jul": "07",
            "Aug": "08",
            "Agu": "08",
            "Sep": "09",
            "Oct": "10",
            "Okt": "10",
            "Nov": "11",
            "Dec": "12",
            "Des": "12",
        }

        date = header.css(".detail__date::text").extract_first()
        date = date.split(",")[1].replace("WIB", "")
        date = date.replace(
            re.search("[A-Za-z]+", date).group(0),
            monthChanger2[re.search("[A-Za-z]+", date).group(0)],
        )
        date = date.strip()
        item["news_date"] = datetime.strptime(date, "%d %m %Y %H:%M")

        # Get media url
        item["media"] = media.css(
            "figure.detail__media-image > img::attr(src)"
        ).extract()

        # Get tags
        item["tags"] = tags.css(".nav > a::text").extract()

        # Get raw content
        contentRaw = content.css(".detail__body-text > p::text")
        list_content = contentRaw.extract()
        string = " ".join(list_content)
        string = re.sub("\n|\t|\r|\xa0|\u201d|\u201c", "", string)
        string = re.sub(" +", " ", string)
        string = string.strip()
        item["contentRaw"] = string

        item["createdAt"] = datetime.now()

        # stop berita diatas 1 jam dari sekarang
        if datetime.now().hour - item["news_date"].hour > 1:
            raise CloseSpider("get only and hour from now")

        load_to_elastic(item)
        yield item
