import streamlit as st

from sqlalchemy import create_engine
from config import (
    POSTGRES_PORT,
    POSTGRES_HOST,
    POSTGRES_DB,
    POSTGRES_PASSWORD,
    POSTGRES_USERNAME,
)
from trending import draw_trend
from sunburst import write_sunburst
from timeseries import draw_timeseries
from umap2 import draw_umap
from entity import draw_entity

st.set_page_config(layout="wide")


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


db = get_connection()
st.title("News Monitoring Dashboard")
# whats happening
# important
# neutral
# not important
draw_trend(db, st)

col1, col2 = st.columns(2)
# priority goodnews bad news
write_sunburst(db, col1)
# timeseries
draw_timeseries(db, col2)
# goodnews
draw_umap(db, st)


# person
# org
# work of art
# product
# loc
# law
# job title
# gpe
# event
# ethnic
draw_entity(db, st)
