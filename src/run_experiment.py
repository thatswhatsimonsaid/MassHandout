import os
from config.experiment_config import EXPERIMENT_CONFIG as CONFIG

def generate_sbatch():
    job_dir = "experiments/job_scripts"
    log_out_dir = "experiments/slurm_logs/out"
    log_err_dir = "experiments/slurm_logs/err"
    
    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(log_out_dir, exist_ok=True)
    os.makedirs(log_err_dir, exist_ok=True)
    
    dates_str = " ".join(CONFIG["dates"])
    scfg = CONFIG["slurm"]
    
    sbatch_content = f"""#!/bin/bash
#SBATCH --job-name=mass_booklets
#SBATCH --output={log_out_dir}/mass_%A_%a.out
#SBATCH --error={log_err_dir}/mass_%A_%a.err
#SBATCH --array=0-{len(CONFIG["dates"])-1}
#SBATCH --partition={scfg['partition']}
#SBATCH --time={scfg['time']}
#SBATCH --mem-per-cpu={scfg['mem_per_cpu']}
#SBATCH --mail-type={scfg['mail_type']}
#SBATCH --mail-user={scfg['mail_user']}

source /mnt/beegfs/homes/simondn/MassHandout/.venv/bin/activate
export PYTHONPATH=.

DATES=({dates_str})
TARGET_DATE=${{DATES[$SLURM_ARRAY_TASK_ID]}}

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
    filename = os.path.join(CONFIG['output_dir'], f'Mass_Booklet_{{date_str}}.docx')
    create_booklet_docx(user_inputs, final_data, filename=filename)

asyncio.run(main())
"
"""
    sbatch_path = os.path.join(job_dir, "run_mass_array.sbatch")
    with open(sbatch_path, "w") as f:
        f.write(sbatch_content)
    print(f"Generated {sbatch_path} successfully!")

if __name__ == "__main__":
    generate_sbatch()