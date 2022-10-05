-- doc meta

CREATE TABLE
    IF NOT EXISTS doc_author (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

CREATE TABLE
    IF NOT EXISTS doc_source (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

CREATE TABLE
    IF NOT EXISTS doc_category (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

CREATE TABLE
    IF NOT EXISTS doc_tags (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

-- entity

CREATE TABLE
    IF NOT EXISTS entity_ethnic (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

CREATE TABLE
    IF NOT EXISTS entity_event (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

CREATE TABLE
    IF NOT EXISTS entity_gpe (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

CREATE TABLE
    IF NOT EXISTS entity_job_title (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

CREATE TABLE
    IF NOT EXISTS entity_law (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

CREATE TABLE
    IF NOT EXISTS entity_loc (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

CREATE TABLE
    IF NOT EXISTS entity_org (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

CREATE TABLE
    IF NOT EXISTS entity_person (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

CREATE TABLE
    IF NOT EXISTS entity_product (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

CREATE TABLE
    IF NOT EXISTS entity_work_of_art (
        id TEXT PRIMARY KEY,
        alias TEXT,
        is_visible BOOLEAN
    );

-- doc

ALTER TABLE
    work_of_art_in_doc DROP CONSTRAINT IF EXISTS work_of_art_in_doc_doc_id_fkey;

ALTER TABLE
    product_in_doc DROP CONSTRAINT IF EXISTS product_in_doc_doc_id_fkey;

ALTER TABLE
    person_in_doc DROP CONSTRAINT IF EXISTS person_in_doc_doc_id_fkey;

ALTER TABLE
    org_in_doc DROP CONSTRAINT IF EXISTS org_in_doc_doc_id_fkey;

ALTER TABLE
    loc_in_doc DROP CONSTRAINT IF EXISTS loc_in_doc_doc_id_fkey;

ALTER TABLE
    law_in_doc DROP CONSTRAINT IF EXISTS law_in_doc_doc_id_fkey;

ALTER TABLE
    job_title_in_doc DROP CONSTRAINT IF EXISTS job_title_in_doc_doc_id_fkey;

ALTER TABLE
    gpe_in_doc DROP CONSTRAINT IF EXISTS gpe_in_doc_doc_id_fkey;

ALTER TABLE
    event_in_doc DROP CONSTRAINT IF EXISTS event_in_doc_doc_id_fkey;

ALTER TABLE
    ethnic_in_doc DROP CONSTRAINT IF EXISTS ethnic_in_doc_doc_id_fkey;

ALTER TABLE
    tag_in_doc DROP CONSTRAINT IF EXISTS tag_in_doc_doc_id_fkey;

DROP TABLE IF EXISTS doc;

CREATE TABLE
    IF NOT EXISTS doc (
        id TEXT PRIMARY KEY,
        author_id TEXT REFERENCES doc_author (id),
        source_id TEXT REFERENCES doc_source (id),
        category_id TEXT REFERENCES doc_category (id),
        clean_text TEXT,
        news_date TIMESTAMP,
        created_at TIMESTAMP,
        sentiment TEXT,
        news_priority TEXT,
        media TEXT,
        slug TEXT,
        title TEXT
    );

-- association TABLE

DROP TABLE IF EXISTS tag_in_doc;

CREATE TABLE
    IF NOT EXISTS tag_in_doc (
        id SERIAL PRIMARY KEY,
        entity_id TEXT REFERENCES doc_tags (id),
        doc_id TEXT REFERENCES doc (id)
    );

DROP TABLE IF EXISTS work_of_art_in_doc;

CREATE TABLE
    IF NOT EXISTS work_of_art_in_doc (
        id SERIAL PRIMARY KEY,
        entity_id TEXT REFERENCES entity_work_of_art (id),
        doc_id TEXT REFERENCES doc (id)
    );

DROP TABLE IF EXISTS product_in_doc;

CREATE TABLE
    IF NOT EXISTS product_in_doc (
        id SERIAL PRIMARY KEY,
        entity_id TEXT REFERENCES entity_product (id),
        doc_id TEXT REFERENCES doc (id)
    );

DROP TABLE IF EXISTS person_in_doc;

CREATE TABLE
    IF NOT EXISTS person_in_doc (
        id SERIAL PRIMARY KEY,
        entity_id TEXT REFERENCES entity_person (id),
        doc_id TEXT REFERENCES doc (id)
    );

DROP TABLE IF EXISTS org_in_doc;

CREATE TABLE
    IF NOT EXISTS org_in_doc (
        id SERIAL PRIMARY KEY,
        entity_id TEXT REFERENCES entity_org (id),
        doc_id TEXT REFERENCES doc (id)
    );

DROP TABLE IF EXISTS loc_in_doc;

CREATE TABLE
    IF NOT EXISTS loc_in_doc (
        id SERIAL PRIMARY KEY,
        entity_id TEXT REFERENCES entity_loc (id),
        doc_id TEXT REFERENCES doc (id)
    );

DROP TABLE IF EXISTS law_in_doc;

CREATE TABLE
    IF NOT EXISTS law_in_doc (
        id SERIAL PRIMARY KEY,
        entity_id TEXT REFERENCES entity_law (id),
        doc_id TEXT REFERENCES doc (id)
    );

DROP TABLE IF EXISTS job_title_in_doc;

CREATE TABLE
    IF NOT EXISTS job_title_in_doc (
        id SERIAL PRIMARY KEY,
        entity_id TEXT REFERENCES entity_job_title (id),
        doc_id TEXT REFERENCES doc (id)
    );

DROP TABLE IF EXISTS gpe_in_doc;

CREATE TABLE
    IF NOT EXISTS gpe_in_doc (
        id SERIAL PRIMARY KEY,
        entity_id TEXT REFERENCES entity_gpe (id),
        doc_id TEXT REFERENCES doc (id)
    );

DROP TABLE IF EXISTS event_in_doc;

CREATE TABLE
    IF NOT EXISTS event_in_doc (
        id SERIAL PRIMARY KEY,
        entity_id TEXT REFERENCES entity_event (id),
        doc_id TEXT REFERENCES doc (id)
    );

DROP TABLE IF EXISTS ethnic_in_doc;

CREATE TABLE
    IF NOT EXISTS ethnic_in_doc (
        id SERIAL PRIMARY KEY,
        entity_id TEXT REFERENCES entity_ethnic (id),
        doc_id TEXT REFERENCES doc (id)
    );