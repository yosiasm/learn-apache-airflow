import streamlit as st
import plotly.express as px
import pandas as pd


def draw_entity(db, st: st):
    entity_docs = {}
    for en in [
        "ETHNIC",
        "EVENT",
        "GPE",
        "JOB_TITLE",
        "LAW",
        "LOC",
        "ORG",
        "PERSON",
        "PRODUCT",
        "WORK_OF_ART",
    ]:
        try:
            db.connect()
            res = db.execute(f"SELECT * FROM {en.lower()}_in_doc LIMIT 20000")
            result = {}
            for row in res.fetchall():
                entity_id = row["entity_id"]
                if entity_id not in result:
                    result[entity_id] = 0
                result[entity_id] += 1
        except Exception as e:
            print(e)
        finally:
            db.dispose()
        if result:
            result = [{"entity": key, "value": result[key]} for key in result]
            entity_docs[en] = pd.DataFrame(result)
        else:
            entity_docs[en] = pd.DataFrame(columns=["entity", "value"])

    col1, col2 = st.columns(2)
    col1.subheader("Person")
    fig = px.bar(
        entity_docs["PERSON"].sort_values("value", ascending=False).head(10),
        x="entity",
        y="value",
    )
    col1.write(fig)
    col2.subheader("Organization")
    fig = px.bar(
        entity_docs["ORG"].sort_values("value", ascending=False).head(10),
        x="entity",
        y="value",
    )
    col2.write(fig)

    col1, col2, col3, col4 = st.columns(4)
    col1.subheader("Ethnic")
    col1.table(entity_docs["ETHNIC"].sort_values("value", ascending=False).head(10))
    col2.subheader("Event")
    col2.table(entity_docs["EVENT"].sort_values("value", ascending=False).head(10))
    col3.subheader("Geopolitical Entity")
    col3.table(entity_docs["GPE"].sort_values("value", ascending=False).head(10))
    col4.subheader("Job Title")
    col4.table(entity_docs["JOB_TITLE"].sort_values("value", ascending=False).head(10))

    col1, col2, col3, col4 = st.columns(4)
    col1.subheader("Law")
    col1.table(entity_docs["LAW"].sort_values("value", ascending=False).head(10))
    col2.subheader("Location")
    col2.table(entity_docs["LOC"].sort_values("value", ascending=False).head(10))
    col3.subheader("Product")
    col3.table(entity_docs["PRODUCT"].sort_values("value", ascending=False).head(10))
    col4.subheader("Work Of Art")
    col4.table(
        entity_docs["WORK_OF_ART"].sort_values("value", ascending=False).head(10)
    )
