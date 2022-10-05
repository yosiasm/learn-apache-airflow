from news_scraper.engines import spiders
from scrapyscript import Job, Processor
import scrapy
import sys


spidercls = dir(getattr(spiders, sys.argv[1]))
spidercls = [d for d in spidercls if d != "CloseSpider" and "__" not in d]
spidercls = spidercls[0]
spidercls = getattr(getattr(spiders, sys.argv[1]), spidercls)


settings = scrapy.settings.Settings(values={"LOG_LEVEL": "WARNING"})

job = Job(spidercls)
processor = Processor(settings=settings)

data = processor.run(job)
