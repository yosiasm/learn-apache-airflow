import requests
from config import (
    ELASTIC_URL,
    MODEL_URL,
    POSTGRES_PORT,
    POSTGRES_HOST,
    POSTGRES_DB,
    POSTGRES_PASSWORD,
    POSTGRES_USERNAME,
    ELASTIC_INDEX,
)
from sqlalchemy import create_engine
from news_scraper.healthcheck import scrapy_health_check as scrapy_hc


def health_check_task():
    # elastic
    elastic_health_check()
    # model
    model_health_check()
    # postgres
    postgres_health_check()
    # scrapy
    return scrapy_health_check()


# elastic
def elastic_health_check():
    elastic_check = requests.get(ELASTIC_URL)
    elastic_check = requests.get(
        f"{ELASTIC_URL}{ELASTIC_INDEX}/_search?size=2&sort=createdAt:desc"
    )
    if elastic_check.status_code == 200:
        print("Elasticsearch: healthy")
    else:
        print("Elasticsearch: unhealthy")
        print(elastic_check.text)
        raise ValueError("Elasticsearch is not ready")


# model
def model_health_check():
    model_check = requests.get(MODEL_URL)
    if model_check.status_code == 200:
        print("Model Node: healthy")
    else:
        print("Model Node: unhealthy")
        print(model_check.text)
        raise ValueError("Model Node is not ready")


# postgres
def postgres_health_check():
    engine = create_engine(
        "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
            POSTGRES_USERNAME,
            POSTGRES_PASSWORD,
            POSTGRES_HOST,
            POSTGRES_PORT,
            POSTGRES_DB,
        )
    )
    engine.connect()
    engine.dispose()
    print("Postgres: healthy")


# scrapy
def scrapy_health_check():
    return scrapy_hc()


if __name__ == "__main__":
    health_check_task()
