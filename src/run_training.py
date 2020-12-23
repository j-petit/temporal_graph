import sys
from torch.utils.data import DataLoader
import torch
import tqdm
from src.data_loader import NewsEntityDataset

# to be able to improt tgn content
sys.path.append("./src/tgn")
from model.tgn import TGN


def run_training(config):

    c_tgn = config["c_tgn"]

    data = NewsEntityDataset(config["c_data"]["database"], config["c_model"]["predict_horizon"])
    dataset_loader = DataLoader(data, batch_size=20, shuffle=False, num_workers=6)

    torch.multiprocessing.set_sharing_strategy("file_system")

    # See https://github.com/twitter-research/tgn/blob/master/train_supervised.py how to continue from here
