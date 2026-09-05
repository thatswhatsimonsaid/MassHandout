### Packages ###
import asyncio
from src.scrapers import scrape_usccb_async, get_thanhlinh_url_dynamically, scrape_thanhlinh
from src.parsers import prepare_template_data
from src.builder import create_booklet_docx

### MAIN ENTRY POINT ###
async def main():
    """Orchestrates async USCCB scraping, dynamic Thanh Linh scraping, data preparation, and Word document booklet generation."""
    user_inputs = {
        "date": "092926",
        "hymns": {},
        "reading1": {"lang": "eng", "option_index": 0},
        "psalm":    {"lang": "viet", "option_index": 0},
        "reading2": {"lang": "eng", "option_index": 0},
        "alleluia": {"lang": "viet", "option_index": 0},
        "gospel":   {"lang": "eng", "option_index": 0}
    }
    date_str = user_inputs["date"]

    scraped_eng = await scrape_usccb_async(date_str)
    thanhlinh_url = get_thanhlinh_url_dynamically(date_str)
    scraped_viet = scrape_thanhlinh(thanhlinh_url)

    final_data = prepare_template_data(user_inputs, scraped_eng, scraped_viet)
    create_booklet_docx(user_inputs, final_data)


if __name__ == "__main__":
    asyncio.run(main())