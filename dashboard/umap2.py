import streamlit as st
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from cluestar import plot_text


def draw_umap(db, st: st):
    docs = []
    for portal in [
        "antaranews",
        "detiknews",
        "jawapos",
        "kompas",
        "liputan6",
        "tempo",
    ]:
        try:
            db.connect()
            resp = db.execute(
                f"SELECT title,sentiment,source_id,news_priority FROM doc WHERE source_id='{portal}' ORDER BY news_date DESC LIMIT 1000"
            )
            for row in resp.fetchall():
                docs.append(
                    dict(
                        title=row["title"],
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

    cluster = st.selectbox("Cluster Of", ["sentiment", "priority", "source", "tfidf"])
    if cluster == "tfidf":
        texts = [t["title"] for t in docs]
        clean_texts = [t.replace(" di ", "") for t in texts]
        tfidf_vectorizer = TfidfVectorizer(ngram_range=[1, 1])
        tfidf_separate = tfidf_vectorizer.fit_transform(clean_texts)

        word_lst = tfidf_vectorizer.get_feature_names()
        count_lst = tfidf_separate.toarray().sum(axis=0)

        vocabs = {w: c for w, c in zip(word_lst, count_lst)}
        vocabs = dict(sorted(vocabs.items(), key=lambda item: item[1], reverse=True))

        color = list(vocabs.keys())[:10]
    else:
        texts = ["{}-{}".format(t[cluster], t["title"]) for t in docs]
        color = list(set([doc[cluster].lower() for doc in docs if doc[cluster]]))

    pipe = make_pipeline(
        TfidfVectorizer(ngram_range=[1, 3]), TruncatedSVD(n_components=2)
    )
    X = pipe.fit_transform(texts)
    # set layout

    container = st.container()

    st.markdown(
        f"""
    <style>
        .appview-container .main .block-container{{
            padding-left: 2rem;
            padding-right: 2rem;
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )

    container.header("Similarity Text Cluster")
    st.write(plot_text(X, texts, color_words=color))
