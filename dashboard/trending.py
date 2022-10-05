import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def draw_trend(db, st: st):
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
                f"SELECT entity_id,sentiment,news_priority,doc_id FROM tag_in_doc INNER JOIN doc ON doc.id=tag_in_doc.doc_id WHERE doc.source_id='{portal}' ORDER BY news_date DESC LIMIT 1000"
            )
            for row in resp.fetchall():
                docs.append(
                    dict(
                        tag=row["entity_id"],
                        doc_id=row["doc_id"],
                        sentiment=row["sentiment"],
                        priority=row["news_priority"],
                    )
                )
        except Exception as e:
            print(e)
        finally:
            db.dispose()

    def create_wc(col: st, group, filters):
        col.subheader(filters)
        if group:
            text = ", ".join([doc["tag"] for doc in docs if doc[group] == filters])
        else:
            text = ", ".join([doc["tag"] for doc in docs])
        if not text:
            col.info("no data")
            return
        wc = WordCloud(
            background_color="white", width=500, height=250, max_words=100
        ).generate(text)
        # Display the generated image:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.imshow(wc)
        plt.axis("off")
        col.pyplot(fig)

    col1, col2, col3, col4 = st.columns(4)
    create_wc(col1, None, "All")
    create_wc(col2, "priority", "Important")
    create_wc(col3, "priority", "Neutral")
    create_wc(col4, "priority", "Not Important")
