import scrapy
from datetime import datetime, timedelta, date
import re
import os
from scrapy.exceptions import CloseSpider
from utils import load_to_elastic


class JawaPosSpider(scrapy.Spider):
    name = "jawapos"
    allowed_domain = [
        "jawapos.com",
    ]
    # start_urls = [
    #     "https://index.sindonews.com/",
    # ]
    base_url = "https://www.jawapos.com/berita-hari-ini/"

    def __init__(self, start_date=None, end_date=None, hourly=True, *args, **kwargs):
        super(JawaPosSpider, self).__init__(*args, **kwargs)

        self.start_date = None  # "2020-08-06" #None hari ini doang
        self.end_date = None  # "2020-08-14" #None hari ini doang

        self.hourly = True  # False #True per jam

        if self.start_date != None and self.end_date != None:
            self.start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            self.end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
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
                    "{}/{}".format(
                        self.base_url,
                        f"{date.year}/{date.month}/{date.day}",
                    )
                )

        for url in _ranged:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        for article_url in response.css(
            ".main-section div > div > div > div > div.col > div > h3 > a::attr(href)"
        ).extract():
            yield scrapy.Request(
                response.urljoin("{}?page=all%single=1   ".format(article_url)),
                callback=self.parse_article_page,
            )

        # next_link = response.css('.pagination > ul > li').css('a')
        # next_page = next_link.css("::attr(href)").extract()
        # if (next_page):
        #     yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_article_page(self, response):
        item = {
            "source": "jawapos",
            "type": "article",
            "slug": response.request.url,
        }

        # Get category
        breadcrumb = response.css(".breadcrumb > ul > li").css("a::text").extract()
        if breadcrumb:
            item["category"] = breadcrumb
        else:
            breadcrumb = response.css("a.tdb-entry-category::text").extract()
            item["category"] = breadcrumb

        # Get title
        title = response.css("h1.single-title::text").extract_first()
        item["title"] = None
        if title:
            item["title"] = title.replace("\t", "").replace("\r", "").replace("\n", "")
        else:
            title = response.css("h1.tdb-title-text::text").extract_first()
            item["title"] = title.replace("\t", "").replace("\r", "").replace("\n", "")

        # Get author
        author = response.css(".content-reporter > p::text").extract_first()
        author = author.split(": ")[1]
        item["author"] = author

        # Get date (String)
        monthChanger = {
            "Januari": "January",
            "January": "January",
            "Jan": "January",
            "Februari": "February",
            "February": "February",
            "Feb": "February",
            "Maret": "March",
            "March": "March",
            "Mar": "March",
            "April": "April",
            "Apr": "April",
            "Mei": "May",
            "May": "May",
            "May": "May",
            "Juni": "June",
            "Jun": "June",
            "June": "June",
            "Juli": "July",
            "July": "July",
            "Jul": "July",
            "Agustus": "August",
            "August": "August",
            "Aug": "August",
            "September": "September",
            "Sep": "September",
            "Oktober": "October",
            "October": "October",
            "Oct": "October",
            "November": "November",
            "Nov": "November",
            "Desember": "December",
            "December": "December",
            "Des": "December",
        }

        date = response.css(".time::text").extract_first()
        date = date.replace(",", "").replace("WIB", "")[:-4]
        date = date.replace(
            re.search("[A-Za-z]+", date).group(0),
            monthChanger[re.search("[A-Za-z]+", date).group(0)],
        )
        date = date.strip()
        item["news_date"] = datetime.strptime(date, "%d %B %Y %H:%M")

        # Get media url
        item["media"] = response.css(".single-featured > img::attr(data-src)").extract()

        # Get tags
        item["tags"] = (
            response.css(".content-tag > div ul > li").css("a::text").extract()
        )

        # Get raw content
        content = response.css('div[itemprop="articleBody"] > p::text')
        list_content = content.extract()
        string = " ".join(list_content)
        string = re.sub("\n|\t|\r|\xa0|\u201d|\u201c", "", string)
        string = re.sub(" +", " ", string)
        string.strip()
        item["contentRaw"] = string

        item["createdAt"] = datetime.now()

        # stop berita diatas 1 jam dari sekarang
        if datetime.now().hour - item["news_date"].hour > 1:
            raise CloseSpider("get only and hour from now")

        load_to_elastic(item)
        yield item
