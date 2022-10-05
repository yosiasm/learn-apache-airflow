from config import (
    ELASTIC_URL,
    ELASTIC_INDEX,
    MODEL_URL,
    POSTGRES_PORT,
    POSTGRES_HOST,
    POSTGRES_DB,
    POSTGRES_PASSWORD,
    POSTGRES_USERNAME,
)
from sqlalchemy import create_engine
import requests
from preprocess import remove_stopwords, remove_punc, preprocess
from datetime import datetime


def get_connection():
    engine = create_engine(
        "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
            POSTGRES_USERNAME,
            POSTGRES_PASSWORD,
            POSTGRES_HOST,
            POSTGRES_PORT,
            POSTGRES_DB,
        )
    )
    return engine


def get_sentiment(text):
    if not text:
        return None
    payload = {"texts": [text]}
    resp = requests.post(MODEL_URL + "sentiment/", json=payload).json()
    return resp["response"][0]["label"]


def get_priority(text):
    if not text:
        return None
    payload = {"texts": [text]}
    resp = requests.post(MODEL_URL + "scale/", json=payload).json()
    return resp["response"][0]["label"]


def get_ner(text):
    if not text:
        return {}
    payload = {"text": text}
    resp = requests.post(MODEL_URL + "NER/new/", json=payload).json()
    resp_pars = {}
    for res in resp:
        if res == "text":
            continue
        key = res.lower()
        resp_pars[key] = resp[res]["all"]
    return resp_pars


db = get_connection()
try:
    db.connect()
    # get elastic data
    news_data = requests.get(
        f"{ELASTIC_URL}{ELASTIC_INDEX}/_search?size=2000&sort=createdAt:desc"
    ).json()
    print("elastic_data=", len(news_data["hits"]["hits"]))
    for hits in news_data["hits"]["hits"]:
        source = hits["_source"]
        id_ = hits["_id"]
        print("parsing", id_)

        # check if doc already in postgres
        existing_doc = db.execute(f"SELECT id FROM doc WHERE id='{id_}';")
        existing_doc = existing_doc.fetchone()
        if existing_doc:
            print("doc already exists, continue")
            continue

        # parsing
        author_id = source.get("author")
        author_id = remove_punc(author_id) if author_id else author_id
        source_id = source.get("source")
        source_id = remove_punc(source_id) if source_id else source_id
        category_id = source.get("category")
        category_id = remove_punc(category_id) if category_id else category_id
        clean_text = preprocess(source.get("contentRaw", ""))
        news_date = source.get("news_date")
        if news_date:
            news_date = news_date.split(".")[0]
            news_data = news_date.replace("T", " ")
            # news_date = datetime.strptime(news_date,'%Y-%m-%dT%H:%M:%S')
        created_at = source.get("createdAt")
        if created_at:
            created_at = created_at.split(".")[0]
            created_at = created_at.replace("T", " ")
            # created_at = datetime.strptime(created_at,'%Y-%m-%dT%H:%M:%S')
        sentiment = get_sentiment(
            str(source.get("contentRaw", " ")) + str(source.get("title", " "))
        )
        news_priority = get_priority(
            str(source.get("contentRaw", " ")) + str(source.get("title", " "))
        )
        media = source.get("media")
        if type(media) == list and media:
            media = media[0].replace("%", "%%")
        slug = source.get("slug")
        if slug:
            slug = slug.replace("%", "%%")
        title = source.get("title", "")
        title = remove_punc(title)
        tags = source.get("tags", [])
        if type(tags) == str:
            tags = [tags]
        tags = [remove_punc(tag) for tag in tags]
        elastic_id = str(id_)
        ner = get_ner(source.get("contentRaw", ""))
        ner = {key: [remove_punc(en) for en in ner[key]] for key in ner}

        print("insert to postgres", id_)
        # insert meta
        if author_id:
            query = f"""INSERT INTO doc_author (id, alias, is_visible)
            VALUES ('{author_id}','{author_id}', TRUE) ON CONFLICT DO NOTHING;
            """
            db.execute(query)
        if source_id:
            query = f"""INSERT INTO doc_source (id, alias, is_visible)
            VALUES ('{source_id}','{source_id}', TRUE) ON CONFLICT DO NOTHING;
            """
            db.execute(query)
        if category_id:
            query = f"""INSERT INTO doc_category (id, alias, is_visible)
            VALUES ('{category_id}','{category_id}', TRUE) ON CONFLICT DO NOTHING;
            """
            db.execute(query)

        # insert doc
        query = """INSERT INTO doc (id, author_id, source_id, category_id, clean_text, news_date, created_at, sentiment, news_priority, media, slug, title)
        VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {});
        """.format(
            f"'{elastic_id}'" if elastic_id else "NULL",
            f"'{author_id}'" if author_id else "NULL",
            f"'{source_id}'" if source_id else "NULL",
            f"'{category_id}'" if category_id else "NULL",
            f"'{clean_text}'" if clean_text else "NULL",
            f"timestamp '{news_date}'" if news_date else "NULL",
            f"timestamp '{created_at}'" if created_at else "NULL",
            f"'{sentiment}'" if sentiment else "NULL",
            f"'{news_priority}'" if news_priority else "NULL",
            f"'{media}'" if media else "NULL",
            f"'{slug}'" if slug else "NULL",
            f"'{title}'" if title else "NULL",
        )
        print(query)
        db.execute(query)

        # insert tags
        table_name = f"doc_tags"
        for tag in tags:
            query = f"""INSERT INTO {table_name} (id, alias, is_visible)
            VALUES ('{tag}', '{tag}', TRUE) ON CONFLICT DO NOTHING;
            """
            db.execute(query)

        # insert entity
        for key in ner:
            table_name = f"entity_{key}"
            for entity in ner[key]:
                query = f"""INSERT INTO {table_name} (id, alias, is_visible)
                VALUES ('{entity}', '{entity}', TRUE) ON CONFLICT DO NOTHING;
                """
                db.execute(query)

        # insert entity_in_doc
        for key in ner:
            table_name = f"{key}_in_doc"
            for entity in ner[key]:
                query = f"""INSERT INTO {table_name} (entity_id, doc_id)
                VALUES ('{entity}', '{id_}') ON CONFLICT DO NOTHING;
                """
                db.execute(query)

        # insert entity_in_doc
        table_name = f"tag_in_doc"
        for tag in tags:
            query = f"""INSERT INTO {table_name} (entity_id, doc_id)
            VALUES ('{tag}', '{id_}') ON CONFLICT DO NOTHING;
            """
            db.execute(query)
        print("inserted", id_)
except Exception as e:
    db.dispose()
    print("error", e)
    raise ValueError(e)
finally:
    db.dispose()
