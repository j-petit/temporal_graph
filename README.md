# Activity Prediction Using Dynamic Graph Embeddings

Graph embeddings for temporal clustering

## Research Idea

Take a look at the presentation in `reports/temp_graph_praesi/slides.pdf`.

Short summary: Predict the activity of an entity in a temporal graph stream using dynamic embeddings computed by the [TGN architecture](https://github.com/twitter-research/tgn). TGN is adapted to use an RNN as a decoder which outputs the `# Occurances` of each entity in the datastream. The graph stream dataset is extracted from the [GDELT Global Entity Graph](https://blog.gdeltproject.org/announcing-the-global-entity-graph-geg-and-a-new-11-billion-entity-dataset/).

## Repository Architecture

I am using `conda` to manage the python environment. Install the environment with the provided `environment.yml`. Furthermore, I use [sacred](https://sacred.readthedocs.io/en/stable/) to manage the experiment and write results in a MongoDB.

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
