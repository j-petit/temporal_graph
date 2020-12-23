# Activity Prediction Using Dynamic Graph Embeddings

Graph embeddings for temporal clustering

## Research Idea

Take a look at [the presentation](reports/temp_graph_praesi/slides.pdf).

Short summary: Predict the activity of an entity in a temporal graph stream using dynamic embeddings computed by the [TGN architecture](https://github.com/twitter-research/tgn). TGN is adapted to use an RNN as a decoder which outputs the `# Occurances` of each entity in the datastream. The graph stream dataset is extracted from the [GDELT Global Entity Graph](https://blog.gdeltproject.org/announcing-the-global-entity-graph-geg-and-a-new-11-billion-entity-dataset/).

## How To Get Started

I am using `conda` to manage the python environment. Install the environment with the provided `environment.yml`. Furthermore, I use [sacred](https://sacred.readthedocs.io/en/stable/) to manage the experiment and write results in a MongoDB.

TGN, the dynamic graph encoding architecture used in this project, is added as a git submodule.

The `run.py` file is the single entry point to the repo. Almost all configuration is done via the `config/config.yaml`, there are no parameters set in the source code. Execute `python run.py print_config` to see the current parameters status. 

The project has multiple stages which can be (de)activated via the config file.

The data preprocessing can be executed on a cluster which uses the internal cluster memory to speed up things. After processing, the resulting database is copied back to the shared NFS.

## Current Status

This is not a finished project but WIP due to me leaving ScaDS.AI at the end of January 2021.

- Data preprocessing pipeline finished:
    - dataset can be loaded in a specific time interval and is saved in an intermediate SQLite database
    - all entity pair counts are computed and in the count per entity is calculated and stored in an extra table
- TGN is added as a submodule, however the integration with the GDELT dataset is not finished:
    - add RNN decoder
    - prepare input in such a form that TGN understands it
- Evaluation is still missing

## Contact

You can contact me at jenspetit@posteo.net for further questions.
