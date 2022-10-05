from datetime import datetime
import requests


def load_to_elastic(doc: dict):
    source = str(doc.get("source", None))
    type_ = str(doc.get("type", None))
    slug = doc.get("slug", None)
    slug = slug[0] if type(slug) == list else slug
    slug = str(slug)
    id_ = str(hash(slug))
    title = str(doc.get("title", None))
    author = str(doc.get("author", None))
    news_date = doc.get("news_date", None)
    news_date = (
        news_date.strftime("%Y-%m-%dT%H:%M:%S")
        if type(news_date) == datetime
        else news_date
    )
    media = doc.get("media", None)
    media = [media] if type(media) == str else media
    tags = doc.get("tags", None)
    tags = [tags] if type(tags) == str else tags
    contentRaw = doc.get("contentRaw", None)
    createdAt = doc.get("createdAt", None)
    createdAt = (
        createdAt.strftime("%Y-%m-%dT%H:%M:%S")
        if type(createdAt) == datetime
        else createdAt
    )
    doc = dict(
        source=source,
        type=type_,
        slug=slug,
        title=title,
        author=author,
        news_date=news_date,
        media=media,
        tags=tags,
        contentRaw=contentRaw,
        createdAt=createdAt,
    )
    res = requests.post(
        f"http://elasticsearch_airflow_test:9200/news_index/_create/{id_}",
        json=doc,
        timeout=5,
    )
    print(res.json())
