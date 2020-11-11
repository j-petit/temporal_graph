#!/bin/bash

#SBATCH --time=20:00:00
#SBATCH --cpus-per-task=24
#SBATCH --mem=64gb
#SBATCH --part=clara-job
#SBATCH --ntasks=1

if [ -z "$SLURM_ARRAY_TASK_ID" ]; then
    SLURM_ARRAY_TASK_ID=1
fi

. "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate temp_graph

python run.py
