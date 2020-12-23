from torch.utils.data import DataLoader
import torch
import tqdm
from src.data_loader import NewsEntityDataset
from src.tgn.model import TGN
from src.tgn.utils.utils import get_neighbor_finder


def run_training(config):

    c_tgn = config["c_tgn"]

    data = NewsEntityDataset(config["c_data"]["database"], config["c_model"]["predict_horizon"])
    dataset_loader = DataLoader(data, batch_size=20, shuffle=False, num_workers=6)

    torch.multiprocessing.set_sharing_strategy("file_system")

    train_ngh_finder = get_neighbor_finder(
        train_data, uniform=c_tgn["uniform"], max_node_idx=max_idx
    )

    tgn = TGN(
        neighbor_finder=train_ngh_finder,
        node_features=node_features,
        edge_features=edge_features,
        device=0,
        n_layers=c_tgn["n_layer"],
        n_heads=c_tgn["n_heads"],
        dropout=c_tgn["drop_out"],
        use_memory=c_tgn["use_memory"],
        message_dimension=c_tgn["message_dim"],
        memory_dimension=c_tgn["memory_dim"],
        memory_update_at_start=not c_tgn["memory_update_at_end"],
        embedding_module_type=c_tgn["embedding_module_type"],
        message_function=c_tgn["message_function"],
        aggregator_type=c_tgn["aggregator"],
        n_neighbors=c_tgn["n_neg"],
        mean_time_shift_src=mean_time_shift_src,
        std_time_shift_src=std_time_shift_src,
        mean_time_shift_dst=mean_time_shift_dst,
        std_time_shift_dst=std_time_shift_dst,
        use_destination_embedding_in_message=c_tgn["use_destination_embedding_in_message"],
        use_source_embedding_in_message=c_tgn["use_source_embedding_in_message"],
    )

    tgn = tgn.to(device)

    num_instance = len(train_data.sources)
    num_batch = math.ceil(num_instance / BATCH_SIZE)

    logger.debug("Num of training instances: {}".format(num_instance))
    logger.debug("Num of batches per epoch: {}".format(num_batch))

    logger.info("Loading saved TGN model")
    model_path = f"./saved_models/{args.prefix}-{DATA}.pth"
    tgn.load_state_dict(torch.load(model_path))
    tgn.eval()
    logger.info("TGN models loaded")
    logger.info("Start training node classification task")

    decoder = MLP(node_features.shape[1], drop=DROP_OUT)
    decoder_optimizer = torch.optim.Adam(decoder.parameters(), lr=args.lr)
    decoder = decoder.to(device)
    decoder_loss_criterion = torch.nn.BCELoss()

    val_aucs = []
    train_losses = []

    early_stopper = EarlyStopMonitor(max_round=args.patience)
    for epoch in range(args.n_epoch):
        start_epoch = time.time()

    # Initialize memory of the model at each epoch
    if USE_MEMORY:
        tgn.memory.__init_memory__()

    tgn = tgn.eval()
    decoder = decoder.train()
    loss = 0

    for k in range(num_batch):
        s_idx = k * BATCH_SIZE
        e_idx = min(num_instance, s_idx + BATCH_SIZE)

        sources_batch = train_data.sources[s_idx:e_idx]
        destinations_batch = train_data.destinations[s_idx:e_idx]
        timestamps_batch = train_data.timestamps[s_idx:e_idx]
        edge_idxs_batch = full_data.edge_idxs[s_idx:e_idx]
        labels_batch = train_data.labels[s_idx:e_idx]

        size = len(sources_batch)

        decoder_optimizer.zero_grad()
        with torch.no_grad():
            source_embedding, destination_embedding, _ = tgn.compute_temporal_embeddings(
                sources_batch,
                destinations_batch,
                destinations_batch,
                timestamps_batch,
                edge_idxs_batch,
                NUM_NEIGHBORS,
            )

        labels_batch_torch = torch.from_numpy(labels_batch).float().to(device)
        pred = decoder(source_embedding).sigmoid()
        decoder_loss = decoder_loss_criterion(pred, labels_batch_torch)
        decoder_loss.backward()
        decoder_optimizer.step()
        loss += decoder_loss.item()
    train_losses.append(loss / num_batch)

    val_auc = eval_node_classification(
        tgn, decoder, val_data, full_data.edge_idxs, BATCH_SIZE, n_neighbors=NUM_NEIGHBORS
    )
    val_aucs.append(val_auc)

    pickle.dump(
        {
            "val_aps": val_aucs,
            "train_losses": train_losses,
            "epoch_times": [0.0],
            "new_nodes_val_aps": [],
        },
        open(results_path, "wb"),
    )

    logger.info(
        f"Epoch {epoch}: train loss: {loss / num_batch}, val auc: {val_auc}, time: {time.time() - start_epoch}"
    )

    if args.use_validation:
        if early_stopper.early_stop_check(val_auc):
            logger.info(
                "No improvement over {} epochs, stop training".format(early_stopper.max_round)
            )
        break
    else:
        torch.save(decoder.state_dict(), get_checkpoint_path(epoch))

    if args.use_validation:
        logger.info(f"Loading the best model at epoch {early_stopper.best_epoch}")
        best_model_path = get_checkpoint_path(early_stopper.best_epoch)
        decoder.load_state_dict(torch.load(best_model_path))
        logger.info(f"Loaded the best model at epoch {early_stopper.best_epoch} for inference")
        decoder.eval()
        test_auc = eval_node_classification(
            tgn, decoder, test_data, full_data.edge_idxs, BATCH_SIZE, n_neighbors=NUM_NEIGHBORS
        )
    else:
        # If we are not using a validation set, the test performance is just the performance computed
        # in the last epoch
        test_auc = val_aucs[-1]

    pickle.dump(
        {
            "val_aps": val_aucs,
            "test_ap": test_auc,
            "train_losses": train_losses,
            "epoch_times": [0.0],
            "new_nodes_val_aps": [],
            "new_node_test_ap": 0,
        },
        open(results_path, "wb"),
    )

    logger.info(f"test auc: {test_auc}")
