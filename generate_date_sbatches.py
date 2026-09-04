import os
from datetime import datetime, timedelta

def generate_sbatch_files(start_date_str, end_date_str, output_dir="job_scripts"):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("ClusterMessages/out", exist_ok=True)
    os.makedirs("ClusterMessages/error", exist_ok=True)

    start_date = datetime.strptime(start_date_str, "%m%d%y")
    end_date = datetime.strptime(end_date_str, "%m%d%y")
    
    current_date = start_date
    generated_files = []

    while current_date <= end_date:
        date_str = current_date.strftime("%m%d%y")
        filename = os.path.join(output_dir, f"run_scrape_{date_str}.sbatch")
        
        sbatch_content = f"""#!/bin/bash
#SBATCH --job-name Scrape_{date_str}
#SBATCH --partition medium
#SBATCH --ntasks 1
#SBATCH --time 1-00:00:00
#SBATCH --mem-per-cpu=4000
#SBATCH -o ClusterMessages/out/scrape_{date_str}_%j.out
#SBATCH -e ClusterMessages/error/scrape_{date_str}_%j.err
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=simondn@uw.edu

cd ~/Stats572
python3 Code/RunScraper.py --date {date_str}
"""
        with open(filename, "w") as f:
            f.write(sbatch_content)
            
        generated_files.append(filename)
        current_date += timedelta(days=1)

    # Generate a master run-all script
    master_script = "run_all_scrapes.sh"
    with open(master_script, "w") as f:
        f.write("#!/bin/bash\n")
        for file in generated_files:
            f.write(f"sbatch {file}\n")
    
    os.chmod(master_script, 0o755)
    print(f"Generated {len(generated_files)} sbatch files and master script '{master_script}'.")

if __name__ == "__main__":
    generate_sbatch_files("100126", "100726")