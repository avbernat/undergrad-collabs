#!/bin/bash
#SBATCH --job-name=diagnostics
#SBATCH --output=diagnostics.out
#SBATCH --error=diagnostics.err
#SBATCH --time=08:00:00
#SBATCH --partition=broadwl
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --mem-per-cpu=2000