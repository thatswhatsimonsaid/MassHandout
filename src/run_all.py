### Packages ###
import os
import asyncio
from config.experiment_config import CONFIG
from src.scrapers import scrape_usccb_async, get_thanhlinh_url_dynamically, scrape_thanhlinh
from src.parsers import prepare_template_data
from src.builder import create_booklet_docx

### Run all ###
async def run_all_local():
    output_dir = CONFIG["output_dir"]
    os.makedirs(output_dir, exist_ok=True)

    for date_str in CONFIG["dates"]:
        print(f"Generating booklet for date: {date_str}...")
        user_inputs = CONFIG["default_inputs"].copy()
        user_inputs["date"] = date_str

        scraped_eng = await scrape_usccb_async(date_str)
        thanhlinh_url = get_thanhlinh_url_dynamically(date_str)
        scraped_viet = scrape_thanhlinh(thanhlinh_url)

        final_data = prepare_template_data(user_inputs, scraped_eng, scraped_viet)
        
        filename = os.path.join(output_dir, f"Mass_Booklet_{date_str}.docx")
        create_booklet_docx(user_inputs, final_data, filename=filename)
        print(f"Saved: {filename}")

if __name__ == "__main__":
    asyncio.run(run_all_local())