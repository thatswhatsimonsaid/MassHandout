
### Packages ###

import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from parsers import SECTION_KEYWORDS


### CITATION FORMAT VALIDATOR ###
def _looks_like_citation(text):
    """Validates whether a given text string matches a standard scripture citation pattern."""
    clean = text.strip()
    return bool(
        re.match(r'^(cf\.\s*)?[1-3]?\s*[A-Z][a-zA-Z]+\.?\s+\d+(:\d+)?([-,]\s*\d+)*[a-z]?$', clean) or
        re.match(r'^[1-3]?\s*[A-Z][a-zA-Z]+\.?\s+[0-9a-zA-Z\s,–-]+$', clean) and len(clean) < 50
    )


### USCCB HTML PARSER ###
def _parse_usccb_html(html_content):
    """Parses raw USCCB HTML content to extract feast day titles and structured scripture sections."""
    eng_dict = {
        "feast_day": "Daily Readings",
        "reading1": [], "psalm": [], "reading2": [], "alleluia": [], "gospel": []
    }
    soup = BeautifulSoup(html_content, 'html.parser')

    if soup.title:
        title_text = soup.title.get_text(strip=True)
        clean_title = title_text.split('|')[0].split('-')[0].strip()
        if clean_title and "daily readings" not in clean_title.lower():
            eng_dict["feast_day"] = clean_title

    if eng_dict["feast_day"] == "Daily Readings":
        main_title = soup.select_one('.block-page-title h1, .content-header h1, h1.page-title')
        if main_title:
            t = main_title.get_text(strip=True)
            if t and not t.lower().startswith("reading"):
                eng_dict["feast_day"] = t

    current_section = None
    current_text = []

    def save_current_option():
        if not current_section or not current_text:
            return
        full_text = "\n".join(current_text).strip()
        if full_text and full_text not in eng_dict[current_section]:
            eng_dict[current_section].append(full_text)

    for block in soup.select('.b-verse, .content-header, .row'):
        heading = block.find(['h3', 'h4', 'h5'])
        address = block.find(class_='address')
        body = block.find(class_='content-body')

        if heading:
            h_text = heading.get_text(strip=True).lower()
            matched = None
            for keys, section in SECTION_KEYWORDS:
                if any(k in h_text for k in keys):
                    matched = section
                    break
            if matched:
                save_current_option()
                current_section = matched
                current_text = []
                
                if address:
                    addr_text = address.get_text(strip=True)
                    if addr_text:
                        current_text.append(addr_text)

        if current_section and body:
            b_text = body.get_text(separator=' ', strip=True)
            if b_text and b_text not in current_text:
                current_text.append(b_text)

    if not any(eng_dict[s] for s in ["reading1", "psalm", "reading2", "gospel", "alleluia"]):
        current_section = None
        current_text = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'a', 'span', 'strong', 'b']):
            text = tag.get_text(separator=' ', strip=True)
            if not text:
                continue
            lower_text = text.lower().strip()

            if any(footer_trigger in lower_text for footer_trigger in [
                "email terms & privacy", "united states conference of catholic bishops", 
                "listen podcast", "en español", "view calendar", "get daily readings",
                "lectionary for mass", "privacy policy", "usccb", "subscribe"
            ]):
                if current_section == "gospel":
                    save_current_option()
                    current_section = None
                continue

            is_heading_tag = tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
            if is_heading_tag and lower_text == "or":
                save_current_option()
                current_text = []
                continue

            if is_heading_tag or len(text) < 40 or 'address' in tag.get('class', []):
                matched = None
                for keys, section in SECTION_KEYWORDS:
                    if any(k in lower_text for k in keys):
                        matched = section
                        break
                if matched:
                    save_current_option()
                    current_section = matched
                    current_text = []
                    continue

            if current_section:
                if tag.name in ['p', 'div', 'strong', 'b'] and not tag.find(['div', 'p']):
                    if text not in current_text:
                        current_text.append(text)

    save_current_option()
    return eng_dict


### ASYNCHRONOUS USCCB SCRAPER ###
async def async_scrape_usccb(date_str):
    """Asynchronously fetches and loads daily scripture readings from the USCCB website for a given date."""
    url = f"https://bible.usccb.org/bible/readings/{date_str}.cfm"
    empty = {"feast_day": "Daily Readings", "reading1": [], "psalm": [], "reading2": [], "alleluia": [], "gospel": []}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print(f"  -> Navigating to USCCB for {date_str}...")
            await page.goto(url, wait_until="networkidle", timeout=25000)
            await page.wait_for_timeout(3000)
            
            title = await page.title()
            if "checking connection" in title.lower() or "cloudflare" in title.lower():
                print("  -> Encountered connection check, waiting longer...")
                await page.wait_for_timeout(5000)
                
            html_content = await page.content()
        except Exception as e:
            print(f"  -> Error loading USCCB page: {e}")
            return empty
        finally:
            await browser.close()

    return _parse_usccb_html(html_content)


### THANHLINH VIETNAMESE SCRAPER ###
def scrape_thanhlinh(url):
    """Scrapes Vietnamese scripture readings from a specified ThanhLinh URL endpoint."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    viet_dict = {"reading1": [], "psalm": [], "reading2": [], "alleluia": [], "gospel": []}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8' 
    except requests.exceptions.RequestException:
        return viet_dict
        
    soup = BeautifulSoup(response.content, 'html.parser')
    content_container = soup.find('div', class_=re.compile(r'node__content|field--name-body|content-article', re.I)) or soup.find('article') or soup
    
    current_section = None
    current_text = []

    def save_current_section():
        if current_section and current_text:
            cleaned_text = "\n".join(current_text).strip()
            if cleaned_text and cleaned_text not in viet_dict[current_section]:
                viet_dict[current_section].append(cleaned_text)

    for tag in content_container.find_all(['p', 'h3', 'h4', 'div', 'span', 'strong']):
        text = tag.get_text(separator=' ', strip=True)
        if not text:
            continue
        lower_text = text.lower()
        if any(w in lower_text for w in ["mục đặc biệt", "xem tất cả", "phim ảnh", "thánh ca phụng vụ", "tủ sách"]):
            if current_section:
                save_current_section()
                current_section = None
            continue

        matched_section = None
        if text.startswith("Bài Ðọc I:") or text.startswith("Bài Đọc I:") or text.startswith("Bài đọc I:"):
            matched_section = "reading1"
        elif text.startswith("Ðáp Ca:") or text.startswith("Đáp Ca:") or text.startswith("Đáp ca:") or "thánh vịnh" in lower_text:
            matched_section = "psalm"
        elif text.startswith("Bài Ðọc II:") or text.startswith("Bài Đọc II:") or text.startswith("Bài đọc II:"):
            matched_section = "reading2"
        elif text.startswith("Alleluia:") or text.startswith("Tung Hô"):
            matched_section = "alleluia"
        elif text.startswith("Phúc Âm:") or text.startswith("Tin Mừng:") or text.startswith("Tin mừng:") or text.startswith("Preaching:"):
            matched_section = "gospel"

        if matched_section:
            save_current_section()
            current_section = matched_section
            current_text = []
            continue

        if current_section:
            if not any(noise in lower_text for noise in ["bấm vào đây", "đó là lời chúa", "thứ sáu"]):
                if text not in current_text:
                    current_text.append(text)

    save_current_section()
    return viet_dict


### DYNAMIC URL GENERATOR ###
def get_thanhlinh_url_dynamically(date_str):
    """Computes and generates the corresponding ThanhLinh URL offset dynamically based on an anchor date."""
    try:
        target_date = datetime.strptime(date_str, "%m%d%y")
        anchor_date = datetime(2026, 8, 8)
        anchor_id = 587
        delta_days = (target_date - anchor_date).days
        computed_id = anchor_id + delta_days
        return f"https://thanhlinh.net/loi-chua-{computed_id}"
    except Exception as e:
        print(f"  -> Offset calculation warning: {e}")
        return "https://thanhlinh.net/loi-chua-587"


async def scrape_usccb_async(date_str):
    """Asynchronously scrapes USCCB readings for a given MMDDYY date string."""
    url = f"https://bible.usccb.org/bible/readings/{date_str}.cfm"
    empty = {"feast_day": "Daily Readings", "reading1": [], "psalm": [], "reading2": [], "alleluia": [], "gospel": []}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print(f"  -> Navigating to USCCB for {date_str}...")
            await page.goto(url, wait_until="networkidle", timeout=25000)
            await page.wait_for_timeout(3000)
            
            title = await page.title()
            if "checking connection" in title.lower() or "cloudflare" in title.lower():
                print("  -> Encountered connection check, waiting longer...")
                await page.wait_for_timeout(5000)
                
            html_content = await page.content()
        except Exception as e:
            print(f"  -> Error loading USCCB page: {e}")
            return empty
        finally:
            await browser.close()

    return _parse_usccb_html(html_content)
