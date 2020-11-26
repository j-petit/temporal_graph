from torch.utils.data import DataLoader
import torch
import tqdm
from src.data_loader import NewsEntityDataset


def run_training(config):

    torch.multiprocessing.set_sharing_strategy('file_system')

    data = NewsEntityDataset(config["c_data"]["database"], config["c_model"]["predict_horizon"])
    dataset_loader = DataLoader(data, batch_size=20, shuffle=False, num_workers=4)

    for x in tqdm.tqdm(dataset_loader):
        a = 1
