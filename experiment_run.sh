#!/bin/bash
PYTHONPATH=. python src/run_experiment.py
sbatch experiments/job_scripts/run_mass_array.sbatch