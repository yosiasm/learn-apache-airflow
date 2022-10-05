import scrapy
from datetime import datetime, timedelta
import re
import os
from scrapy.exceptions import CloseSpider
from utils import load_to_elastic


class AntaraNewsSpider(scrapy.Spider):
    name = "antaranews"
    allowed_domain = [
        "antaranews.com",
    ]
    # start_urls = [
    #     "https://news.detik.com/indeks",
    # ]
    base_url = "https://www.antaranews.com/indeks"

    def __init__(self, start_date=None, end_date=None, hourly=True, *args, **kwargs):
        super(AntaraNewsSpider, self).__init__(*args, **kwargs)
        print("updpdpdp")
        self.start_date = None  # "2020-08-06" #None hari ini doang
        self.end_date = None  # "2020-08-14" #None hari ini doang
        self.hourly = True  # False #True ambil cuma perjam

        if self.start_date != None and self.end_date != None:
            self.start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            self.end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
            print(self.start_date, self.end_date)
            if self.start_date >= self.end_date:
                print("start date must lowre")
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
                # print(_ranged,"ranged yo")
                _ranged.append(
                    "{}/{:02d}-{:02d}-{}".format(
                        self.base_url, date.day, date.month, date.year
                    )
                )
        for url in _ranged:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for article_url in response.css(".simple-thumb > a::attr(href)").extract():
            yield scrapy.Request(
                response.urljoin("{}?single=1   ".format(article_url)),
                callback=self.parse_article_page,
            )

        next_link = response.css("ul.pagination > li").css("a")
        next_page = next_link.css("::attr(href)").extract()[-1]
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_article_page(self, response):
        item = {
            "source": "antaranews",
            "type": "article",
            "slug": response.request.url,
        }

        # Get category
        # breadcrumb_link = response.css(
        #     "a.read-page--breadcrumb--item__title > span")
        # item["category"] = breadcrumb_link.css("::text").extract()[-1]

        # Get title
        title = response.css("h1.post-title::text").extract_first()
        item["title"] = None
        if title:
            item["title"] = (
                title.replace("\n         ", "").replace("    ", "").replace("\n", "")
            )

        # Get author
        author = response.css(".text-muted::text").extract_first()
        item["author"] = None
        if author:
            item["author"] = author

        # Get date (Datetime)
        monthChanger = {
            "Januari": "January",
            "January": "January",
            "Februari": "February",
            "February": "February",
            "Maret": "March",
            "March": "March",
            "April": "April",
            "Mei": "May",
            "May": "May",
            "Juni": "June",
            "June": "June",
            "Juli": "July",
            "July": "July",
            "Agustus": "August",
            "August": "August",
            "September": "September",
            "Oktober": "October",
            "October": "October",
            "November": "November",
            "Desember": "December",
            "December": "December",
        }

        date = response.css("span.article-date::text").extract_first()
        date = date.split(",")[1].replace("WIB", "")
        date = date.replace(
            re.search("[A-Za-z]+", date).group(0),
            monthChanger[re.search("[A-Za-z]+", date).group(0)],
        )
        date = date.strip()
        item["news_date"] = datetime.strptime(date, "%d %B %Y %H:%M")

        # Get media url
        item["media"] = (
            response.css("figure.image-overlay > picture")
            .css("img::attr(data-src)")
            .extract_first()
        )

        # Get tags
        item["tags"] = response.css("ul.tags-widget > li").css("a::text").extract()

        # Get raw content
        content = response.css(".post-content::text")
        list_content = content.extract()
        string = " ".join(list_content)
        string = re.sub("\n|\t|\r|\xa0|\u201d|\u201c", "", string)
        string = re.sub(" +", " ", string)
        string = string.strip()
        item["contentRaw"] = string

        item["createdAt"] = datetime.now()

        # stop berita diatas 1 jam dari sekarang
        if datetime.now().hour - item["news_date"].hour > 1 and self.hourly:
            raise CloseSpider("get only and hour from now")

        load_to_elastic(item)
        yield item
