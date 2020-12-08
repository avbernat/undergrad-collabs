#!/bin/bash
#SBATCH --job-name=py_diagnostics
#SBATCH --ntasks-per-node=5
#SBATCH --nodes=8
#SBATCH --mem-per-cpu=9000M
#SBATCH --time=01-9:00
#SBATCH --mail-user=avbernat@uchicago.edu
#SBATCH --mail-type=ALL
#SBATCH --partition=broadwl

echo "Running on hostname `hostname`"
echo "Working directory is `pwd`"
echo "Starting Python at `date`."

module load python
python3 /home/avbernat/Desktop/undergrad-collabs/max_speed/diagnostics.py

echo "Finished Python at `date`."