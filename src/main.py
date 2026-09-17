import os
import asyncio
from config.single_config import SINGLE_CONFIG
from src.scrapers import scrape_usccb_async, get_thanhlinh_url_dynamically, scrape_thanhlinh
from src.parsers import prepare_template_data
from src.builder import create_booklet_docx

async def main(custom_date: str = None, custom_org: str = None):
    user_inputs = SINGLE_CONFIG.copy()
    if custom_date:
        user_inputs["date"] = custom_date
    if custom_org:
        user_inputs["organization"] = custom_org

    date_str = user_inputs["date"]

    scraped_eng = await scrape_usccb_async(date_str)
    thanhlinh_url = get_thanhlinh_url_dynamically(date_str)
    scraped_viet = scrape_thanhlinh(thanhlinh_url)

    final_data = prepare_template_data(user_inputs, scraped_eng, scraped_viet)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"Mass_Booklet_{date_str}.docx")

    create_booklet_docx(user_inputs, final_data, filename=filename)
    print(f"Generated: {filename}")
    return filename

if __name__ == "__main__":
    asyncio.run(main())

def generate_booklet_from_web(date_str: str, org_name: str) -> str:
    filename = asyncio.run(main(custom_date=date_str, custom_org=org_name))
    return filename