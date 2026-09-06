#!/bin/bash
#SBATCH --job-name=mass_booklets
#SBATCH --output=experiments/slurm_logs/out/mass_%A_%a.out
#SBATCH --error=experiments/slurm_logs/err/mass_%A_%a.err
#SBATCH --array=0-2
#SBATCH --partition=short
#SBATCH --time=0:05:00
#SBATCH --mem-per-cpu=1G
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=simondn@uw.edu

source /mnt/beegfs/homes/simondn/MassHandout/.venv/bin/activate
export PYTHONPATH=.

DATES=(093026 100126 100226)
TARGET_DATE=${DATES[$SLURM_ARRAY_TASK_ID]}

python -c "
import asyncio
from config.experiment_config import EXPERIMENT_CONFIG as CONFIG
from src.scrapers import scrape_usccb_async, get_thanhlinh_url_dynamically, scrape_thanhlinh
from src.parsers import prepare_template_data
from src.builder import create_booklet_docx
import os

async def main():
    date_str = '$TARGET_DATE'
    os.makedirs(CONFIG['output_dir'], exist_ok=True)
    user_inputs = CONFIG['default_inputs'].copy()
    user_inputs['date'] = date_str

    scraped_eng = await scrape_usccb_async(date_str)
    thanhlinh_url = get_thanhlinh_url_dynamically(date_str)
    scraped_viet = scrape_thanhlinh(thanhlinh_url)

    final_data = prepare_template_data(user_inputs, scraped_eng, scraped_viet)
    filename = os.path.join(CONFIG['output_dir'], f'Mass_Booklet_{date_str}.docx')
    create_booklet_docx(user_inputs, final_data, filename=filename)

asyncio.run(main())
"
