import plotly.express as px
import streamlit as st
import pandas as pd


def write_sunburst(db, st: st):
    st.subheader("Source Volume")
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
                f"SELECT sentiment,source_id,news_priority FROM doc WHERE source_id='{portal}' ORDER BY news_date DESC LIMIT 1000"
            )
            for row in resp.fetchall():
                docs.append(
                    dict(
                        sentiment=row["sentiment"] if row["sentiment"] else "Negative",
                        source=row["source_id"],
                        priority=row["news_priority"]
                        if row["news_priority"]
                        else "Not Important",
                    )
                )
        except Exception as e:
            print(e)
        finally:
            db.dispose()

    df = pd.DataFrame(docs)
    df["value"] = 1
    df = df.groupby(["priority", "sentiment", "source"], as_index=False).sum()
    fig = px.sunburst(df, path=["priority", "sentiment", "source"], values="value")
    st.write(fig)
