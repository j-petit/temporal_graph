import os
import glob
import logging
import sys
import yaml
import pandas as pd
import multiprocessing
import datetime
import itertools
import json
import sqlite3
import datetime
from tqdm import tqdm

import src.istarmap


def get_dataset(config):
    """Downloads the corresponding data and preprocesses it"""

    masterfile = os.path.join(config["c_data"]["raw"], "MASTERFILELIST.TXT")

    if not os.path.isfile(masterfile):
        os.system("curl -LOJ http://data.gdeltproject.org/gdeltv3/geg_gcnlapi/MASTERFILELIST.TXT")
        os.system(f'mv MASTERFILELIST.TXT {config["c_data"]["raw"]}')

    masterfile = pd.read_csv(masterfile, names=["url"])

    masterfile["file"] = masterfile.applymap(lambda url: os.path.splitext(os.path.basename(url))[0])
    masterfile["time"] = masterfile["file"].apply(
        lambda filename: datetime.datetime.strptime(filename[: filename.find(".")], "%Y%m%d%H%M%S")
    )
    masterfile["in_file"] = masterfile["file"].apply(
        lambda filename: os.path.join(config["c_data"]["raw"], filename)
    )
    masterfile["out_file"] = masterfile["file"].apply(
        lambda filename: os.path.join(config["c_data"]["processed"], filename + "_processed")
    )

    mask = (masterfile["time"] > config["c_data"]["start_date"]) & (
        masterfile["time"] <= config["c_data"]["end_date"]
    )

    selection = masterfile[mask]

    urls = selection["url"].tolist()
    in_files = selection["in_file"].tolist()
    out_files = selection["out_file"].tolist()

    if config["c_data"]["limit"]:
        urls = urls[: config["c_data"]["limit"]]
        in_files = in_files[: config["c_data"]["limit"]]
        out_files = out_files[: config["c_data"]["limit"]]

    ins = list(zip(urls, in_files, out_files))

    with multiprocessing.Pool(config["cpu_count"]) as pool:
        for _ in tqdm(pool.istarmap(preprocess_datafile, ins), total=len(ins)):
            pass

    ins_2 = list(
        zip(
            [config["c_data"]["database"]] * len(out_files),
            out_files,
            [config["c_data"]["num_entities_per_article"]] * len(out_files),
            [config["c_data"]["salience_threshold"]] * len(out_files),
        )
    )

    try:
        conn = sqlite3.connect(config["c_data"]["database"])
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS "data" ("unix_time" INTEGER, "entity_1" TEXT, "entity_2" TEXT)"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS "entities" ("mid" TEXT UNIQUE, "name" TEXT, "type" TEXT, PRIMARY KEY("mid") ON CONFLICT IGNORE)"""
        )
    except sqlite3.Error as error:
        print(error)
    finally:
        if conn:
            conn.close()

    with multiprocessing.Pool(config["cpu_count"]) as pool:
        for _ in tqdm(pool.istarmap(generate_graph_data, ins_2), total=len(ins_2)):
            pass

    try:
        conn = sqlite3.connect(config["c_data"]["database"])
        cursor = conn.cursor()
        cursor.execute("""CREATE INDEX IF NOT EXISTS "unix_time" ON "data" ("unix_time" ASC);""")
        conn.commit()
    except sqlite3.Error as error:
        print(error)
    finally:
        if conn:
            conn.close()

    log = logging.getLogger("preprocess")
    log.info("Now creating entity counts...")
    create_entity_counts(config["c_data"]["database"])
    log.info("Finished generating entity counts...")


def preprocess_datafile(url, in_file, out_file):

    if not os.path.isfile(in_file):
        os.system(f"curl -sLJ {url} | gunzip > {in_file}")

    if not os.path.isfile(out_file):
        os.system(f"./src/preprocess.sh {in_file} {out_file}")


def generate_graph_data(db_name, processed_file, num_entities_per_article, salience_threshold):

    data = json.load(open(processed_file, "r"))

    pairs = []

    time_index = []

    entity_ids = pd.DataFrame(columns=["mid", "name", "type"])

    for article in data:
        entity_names = []
        entities = []
        entity_type = []
        for entity in article["entities"][:num_entities_per_article]:
            if entity["avgSalience"] > salience_threshold:
                entities.append(entity["mid"])
                entity_names.append(entity["name"])
                entity_type.append(entity["type"])

        article_pairs = list(itertools.combinations(entities, 2))

        article_date = datetime.datetime.strptime(article["date"], "%Y-%m-%dT%H:%M:%SZ")
        article_pairs = [
            (int(article_date.timestamp()), *article_pair) for article_pair in article_pairs
        ]
        pairs.extend(article_pairs)
        entity_ids = entity_ids.append(pd.DataFrame(list(zip(entities, entity_names, entity_type)), columns=["mid", "name", "type"]))

    df = pd.DataFrame(pairs, columns=["unix_time", "entity_1", "entity_2"])

    try:
        conn = sqlite3.connect(db_name)
        df.to_sql("data", conn, index=False, if_exists="append", method='multi')
        entity_ids.to_sql("entities", conn, index=False, if_exists="append", method='multi')
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def create_entity_counts(db_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE entity_counts AS
            SELECT entity_1, my_date, COUNT(*) as occCount FROM
            (
                SELECT entity_1, date(unix_time, "unixepoch") as my_date FROM data
                UNION ALL
                SELECT entity_2, date(unix_time, "unixepoch") as my_date FROM data
            )
            GROUP BY entity_1, my_date
            ORDER BY my_date ASC, occCount DESC"""
        )
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
