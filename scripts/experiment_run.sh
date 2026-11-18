#!/bin/bash

# Usage: ./scripts/experiment_run.sh

PYTHONPATH=. python3 src/run_experiment.py
sbatch experiments/job_scripts/run_mass_array.sbatch
