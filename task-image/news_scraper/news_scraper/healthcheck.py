from scrapy import spiderloader
from scrapy.utils import project


def scrapy_health_check():
    settings = project.get_project_settings()
    spider_loader = spiderloader.SpiderLoader.from_settings(settings)
    spiders = spider_loader.list()
    classes = [spider_loader.load(name).name for name in spiders]
    if classes:
        print("Scrapy: healthy")
        print(classes)
        return classes
    else:
        print("scrapy has no spider")
        raise ValueError("scrapy has no spider")


if __name__ == "__main__":
    scrapy_health_check()
