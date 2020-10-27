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
        urls = urls[:config["c_data"]["limit"]]
        in_files = in_files[:config["c_data"]["limit"]]
        out_files = out_files[:config["c_data"]["limit"]]

    ins = list(zip(urls, in_files, out_files))

    with multiprocessing.Pool(config["cpu_count"]) as pool:
        for _ in tqdm(pool.istarmap(preprocess_datafile, ins), total=len(ins)):
            pass

    ins_2 = list(zip([config["c_data"]["database"]]*len(out_files),
                     out_files, [config["c_data"]["num_entities_per_article"]]*len(out_files),
                     [config["c_data"]["salience_threshold"]]*len(out_files)))

    with multiprocessing.Pool(config["cpu_count"]) as pool:
        for _ in tqdm(pool.istarmap(generate_graph_data, ins_2), total=len(ins_2)):
            pass


def preprocess_datafile(url, in_file, out_file):

    if not os.path.isfile(in_file):
        temp_file = os.path.basename(in_file)
        os.system(f"curl -s -LOJ {url}")
        os.system(f"gunzip {temp_file}.gz")
        os.system(f"mv {temp_file} {in_file}")

    if not os.path.isfile(out_file):
        os.system(f"./src/preprocess.sh {in_file} {out_file}")


def generate_graph_data(db_name, processed_file, num_entities_per_article, salience_threshold):

    data = json.load(open(processed_file, "r"))

    pairs = []

    time_index = []

    for article in data:
        entities = []
        for entity in article["entities"][:num_entities_per_article]:
            if entity["avgSalience"] > salience_threshold:
                entities.append(entity["name"])

        article_pairs = list(itertools.combinations(entities, 2))

        article_date = datetime.datetime.strptime(article["date"], "%Y-%m-%dT%H:%M:%SZ")
        time_index.extend([int(article_date.timestamp())] * len(article_pairs))

        pairs.extend(article_pairs)

    df = pd.DataFrame(pairs, index=time_index, columns=['entity_1', 'entity_2'])

    try:
        conn = sqlite3.connect(db_name)
        df.to_sql("data", conn, if_exists="append")
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
