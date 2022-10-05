import plotly.express as px
import streamlit as st
from wordcloud import WordCloud
import pandas as pd


def draw_timeseries(db, st: st):
    st.subheader("Source Timeseries")
    docs = []
    for portal in [
        "antaranews",
        "beritapagi",
        "bisnisindonesia",
        "bukamatanews",
        "detiknews",
        "haluan",
        "jawapos",
        "kabarpapua",
        "kompas",
        "koransindo",
        "liputan6",
        "majalahinvestor",
        "mediaindonesia",
        "metrotvnews",
        "oposisicerdas",
        "papuainews",
        "pikiranrakyat",
        "poskota",
        "rakyatmerdeka",
        "republika",
        "rmol",
        "seputarpapua",
        "suaramerdeka",
        "tempo",
        "viva",
    ]:
        try:
            db.connect()
            resp = db.execute(
                f"SELECT source_id, news_date FROM doc WHERE source_id='{portal}' ORDER BY news_date DESC LIMIT 1000"
            )
            for row in resp.fetchall():
                docs.append(
                    dict(
                        source=row["source_id"],
                        news_date=row["news_date"],
                    )
                )
        except Exception as e:
            print(e)
        finally:
            db.dispose()
    df = pd.DataFrame(docs)
    df["news_date"] = df["news_date"].dt.floor("H")

    df["value"] = 1
    df = df.groupby(["source", "news_date"], as_index=False).sum()
    fig = px.line(df, x="news_date", y="value", color="source")
    st.write(fig)
