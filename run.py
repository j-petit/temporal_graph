import logging
import pdb
import logging.config
import yaml
import sacred
import pprint
import os
import datetime
import dotenv
import multiprocessing
import pandas as pd

from sacred import Experiment
from sacred.observers import MongoObserver

from src.get_data import get_dataset
from src.data_loader import occurances_entity
from src.run_training import run_training
from src.utils import plot_occurances


ex = sacred.Experiment("temp_graph")
ex.add_config(yaml.load("config/config.yaml", yaml.SafeLoader))


dotenv.load_dotenv(".env")
URI = "mongodb://{}:{}@139.18.13.64/?authSource=hids&authMechanism=SCRAM-SHA-1".format(
    os.environ["SACRED_MONGODB_USER"], os.environ["SACRED_MONGODB_PWD"]
)
ex.observers.append(MongoObserver(url=URI, db_name="hids"))


@ex.command(unobserved=True)
def print_config(_config):
    """ Replaces print_config which is not working with python 3.8 and current packages sacred"""
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(_config)


@ex.config
def config(c_data, c_results, c_model):

    c_data["raw"] = os.path.join(c_data["prefix"], "raw")
    c_data["processed"] = os.path.join(c_data["prefix"], "processed")
    c_data["interim"] = os.path.join(c_data["prefix"], "interim")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    cpu_count = multiprocessing.cpu_count()

    c_results["output_path"] = os.path.join(c_results["prefix"], timestamp)

    c_data["start_date"] = datetime.datetime.strptime(c_data["start_date"], "%Y_%m_%d")
    c_data["end_date"] = datetime.datetime.strptime(c_data["end_date"], "%Y_%m_%d")
    c_data["database"] = os.path.join(c_data["interim"], c_data["database"])


@ex.config_hook
def hook(config, command_name, logger):

    if config["c_data"]["cluster"]:
        os.system(f"rm -rf {config['c_data']['prefix']}")

    config.update({"hook": True})

    pd.set_option("display.max_columns", 500)
    pd.set_option("display.max_rows", None)
    pd.options.display.width = 0

    os.makedirs(config["c_results"]["output_path"], exist_ok=True)
    os.makedirs(config["c_data"]["processed"], exist_ok=True)
    os.makedirs(config["c_data"]["interim"], exist_ok=True)
    os.makedirs(config["c_data"]["raw"], exist_ok=True)

    # logging.config.fileConfig("config/logging_local.conf")
    log_config = yaml.load(open("config/logging.yaml", "r"), yaml.SafeLoader)

    for handler in log_config["handlers"].values():
        if "filename" in handler.keys():
            handler["filename"] = os.path.join(
                config["c_results"]["output_path"], handler["filename"]
            )

    logging.config.dictConfig(log_config)

    return config


@ex.post_run_hook
def clean_up(c_data, _log):

    if c_data["cluster"]:
        _log.info("Copying database back...")
        os.system(f"cp {c_data['database']} ./data/interim/")
        _log.info("Removing temp files...")
        os.system(f"rm -rf {c_data['prefix']}")


@ex.automain
def run(hook, _config, c_stages, c_results, _run):

    logger = logging.getLogger("temp_graph." + os.path.basename(os.path.splitext(__file__)[0]))
    logger.info(_config["timestamp"])

    if c_stages["get_data"]:
        get_dataset(_config)
    if c_stages["train"]:
        run_training(_config)

    ex.add_artifact(os.path.join(c_results["output_path"], "general.log"))
