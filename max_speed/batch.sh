#!/bin/bash
#SBATCH --job-name=py_diagnostics
#SBATCH --ntasks=5
#SBATCH --nodes=4
#SBATCH --mem-per-cpu=9000M
#SBATCH --time=10:00:00
#SBATCH --mail-user=avbernat@uchicago.edu
#SBATCH --mail-type=ALL
#SBATCH --partition=broadwl
#SBATCH --reservation=cenzer-lab

echo "Running on hostname `hostname`"
echo "Working directory is `pwd`"
echo "Starting Python at `date`."

module load python
python3 /home/avbernat/Desktop/undergrad-collabs/max_speed/diagnostics.py

echo "Finished Python at `date`."