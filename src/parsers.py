### Packages ###
import re
from datetime import datetime

### SECTION KEYWORDS MAPPING ###
SECTION_KEYWORDS = [
    (("reading 1", "first reading", "reading i"), "reading1"),
    (("responsorial psalm", "psalm"), "psalm"),
    (("reading 2", "second reading", "reading ii"), "reading2"),
    (("alleluia", "gospel acclamation", "verse before the gospel"), "alleluia"),
    (("gospel",), "gospel"),
]

### SCRIPTURE CITATION REGEX PATTERN ###
SCRIPTURE_CITATION_RE = re.compile(
    r'(?:cf\.\s*)?(?:[1-3]\s?)?[A-Z][a-zA-Z]{0,6}\.?\s*\d{1,3}'
    r'(?:\s*[:,]\s*\d+[a-z]{0,3}(?:\s*[-–]\s*\d+[a-z]{0,3})?)?'
)


def _looks_like_citation(text):
    """Validates whether a given text string matches a standard scripture citation pattern."""
    clean = text.strip()
    return bool(
        re.match(r'^(cf\.\s*)?[1-3]?\s*[A-Z][a-zA-Z]+\.?\s+\d+(:\d+)?([-,]\s*\d+)*[a-z]?$', clean) or
        re.match(r'^[1-3]?\s*[A-Z][a-zA-Z]+\.?\s+[0-9a-zA-Z\s,–-]+$', clean) and len(clean) < 50
    )


### READING TO DICT PARSER ###
def parse_reading_to_dict(raw_text):
    """Separates a reading string into citation and clean body text, removing leading quotes, announcements, and closings."""
    if not raw_text:
        return {"citation": "", "text": ""}
        
    cleaned = raw_text.strip()
    lines = cleaned.split("\n")
    citation_val = ""
    body_text = ""
    
    # 1. Extract citation if it sits on its own line
    if len(lines) > 1 and _looks_like_citation(lines[0]):
        citation_val = lines[0].strip()
        body_text = " ".join(lines[1:]).strip()
    else:
        # Fallback extraction if the citation is squashed into the same line as the text
        match = re.match(r'^([1-3]?\s*[A-Z][a-zA-Z]+\.?\s+\d+[:\d,\-\sa-zA-Z]+?)(?=[A-Z“"T])', cleaned)
        if match:
            citation_candidate = match.group(1).strip()
            if _looks_like_citation(citation_candidate) or len(citation_candidate) < 30:
                citation_val = citation_candidate
                body_text = cleaned[len(match.group(1)):].strip()
                
    if not body_text:
        body_text = cleaned
        
    # 2. Clean leading quotes and trailing punctuation (e.g. removes `"Quote". `)
    body_text = re.sub(r'^\s*["“][^"”]+["”][\s\.,;]*', '', body_text)
    
    # 3. Clean standard liturgical intro sentences up to their ending period/colon (e.g. `Trích thư... Rôma. `)
    intro_prefixes = r'(?:Bài trích|Bài đọc|Tin Mừng|Trích sách|Trích thư|Thư của|Phúc Âm|Bài Ðọc|Bài Đọc|Khởi đầu)'
    intro_pattern = rf'^{intro_prefixes}[^\.:]+[\.:]\s*'
    body_text = re.sub(intro_pattern, '', body_text, flags=re.IGNORECASE)
    
    # 4. Clean standard liturgical closings at the very end of the text
    body_text = re.sub(r'\s*Ðó là lời Chúa\.?\s*$', '', body_text, flags=re.IGNORECASE)
    body_text = re.sub(r'\s*Đó là lời Chúa\.?\s*$', '', body_text, flags=re.IGNORECASE)
    body_text = re.sub(r'\s*The word of the Lord\.?\s*$', '', body_text, flags=re.IGNORECASE)

    return {
        "citation": citation_val,
        "text": body_text.strip()
    }


### ALLELUIA VERSE PARSER ###
def parse_alleluia_text(raw_text):
    """Strips out redundant opening/closing Alleluia framing and any inline scripture citation, returning the clean verse text plus citation."""
    if not raw_text:
        return {"citation": "", "text": "Alleluia, alleluia!"}

    cleaned = raw_text.strip()
    citation_text = ""

    # 1. If the citation sits on its own line (e.g. USCCB's separate address element),
    #    pull it off first.
    lines = [l.strip() for l in cleaned.split("\n") if l.strip()]
    if len(lines) > 1 and (_looks_like_citation(lines[0]) or SCRIPTURE_CITATION_RE.fullmatch(lines[0])):
        citation_text = lines[0].strip()
        cleaned = "\n".join(lines[1:]).strip()

    cleaned_flat = " ".join(cleaned.split())

    # 2. Find & strip ANY inline scripture citation, wherever it sits, whatever the book.
    #    (Handles no-dash, dash-prefixed, and trailing-citation formats alike.)
    def _grab(m):
        nonlocal citation_text
        if not citation_text:
            citation_text = m.group(0).strip(" -–—")
        return " "
    cleaned_flat = SCRIPTURE_CITATION_RE.sub(_grab, cleaned_flat)

    # 3. Tidy up leftover dashes/double-spaces left behind where the citation used to sit.
    cleaned_flat = re.sub(r'\s*[-–—]\s*[-–—]\s*', ' - ', cleaned_flat)
    cleaned_flat = re.sub(r'\s{2,}', ' ', cleaned_flat).strip()

    # 4. Strip opening/closing Alleluia framing (English & Vietnamese).
    verse_core = re.sub(r'^(?:R\.\s*)?Alleluia,?\s*alleluia[!.]?\s*(?:-\s*)?', '', cleaned_flat, flags=re.IGNORECASE).strip()
    verse_core = re.sub(r'\s*(?:-\s*)?(?:R\.\s*)?Alleluia[!.]?\s*$', '', verse_core, flags=re.IGNORECASE).strip()
    verse_core = re.sub(r'\s*(?:-\s*)?(?:R\.\s*)?Alleluia,?\s*alleluia[!.]?\s*$', '', verse_core, flags=re.IGNORECASE).strip()
    verse_core = re.sub(r'\s*R\.\s*Alleluia,?\s*$', '', verse_core, flags=re.IGNORECASE).strip()
    verse_core = re.sub(r'\s*R\.\s*$', '', verse_core, flags=re.IGNORECASE).strip()
    verse_core = re.sub(r'^[-–—,\.\s]+', '', verse_core).strip()

    return {
        "citation": citation_text,
        "text": verse_core if verse_core else cleaned_flat
    }


### USCCB ENGLISH PSALM PARSER ###
def parse_usccb_psalm_to_dict(raw_text):
    """Specifically parses USCCB English psalm strings into citation, response, and clean stanzas without repeating the response."""
    if not raw_text:
        return {"citation": "", "response": "", "verses": {}}
        
    cleaned = raw_text.strip()
    citation_text = ""
    response_text = ""
    verses_list = []
    
    lines = [l.strip() for l in cleaned.split("\n") if l.strip()]
    if lines and (re.search(r'(?:Psalm|Ps\.?)\s*\d+', lines[0], re.IGNORECASE) or len(lines[0]) < 40):
        citation_text = lines[0].strip()
        cleaned = "\n".join(lines[1:]).strip()

    cleaned_flat = " ".join(cleaned.split())

    if "R." in cleaned_flat:
        parts = cleaned_flat.split("R.")
        if len(parts) > 1:
            refrain_segment = parts[1].strip()
            match_end = re.search(r'(\(?[0-9a-zA-Z\.\s]+\)?\.\s*["\u201d]?|[\.?!]\s*["\u201d]?)', refrain_segment)
            if match_end and match_end.start() > 5:
                end_idx = match_end.end()
                response_text = "R. " + refrain_segment[:end_idx].strip()
            else:
                response_text = "R. " + refrain_segment.split('.')[0] + "."

    body_text = cleaned_flat
    if response_text in body_text:
        body_text = body_text.replace(response_text, "", 1)

    core_resp_phrase = re.sub(r'^R\.\s*(\([^\)]+\))?\s*', '', response_text).strip()

    raw_chunks = body_text.split("R.")
    for chunk in raw_chunks:
        chunk_clean = chunk.strip()
        
        if core_resp_phrase:
            chunk_clean = chunk_clean.replace(core_resp_phrase, "").strip()
            
        chunk_clean = re.sub(r'^[\.,;\s]+', '', chunk_clean).strip()
        chunk_clean = re.sub(r'R\.\s*$', '', chunk_clean).strip()
        
        if chunk_clean and len(chunk_clean) > 5:
            verses_list.append(chunk_clean)

    verses_dict = {}
    for i, verse_text in enumerate(verses_list, start=1):
        clean_v = verse_text.strip()
        if not re.match(r'^\d+\.', clean_v):
            verses_dict[f"verse{i}"] = f"{i}. {clean_v}"
        else:
            verses_dict[f"verse{i}"] = clean_v

    return {
        "citation": citation_text,
        "response": response_text,
        "verses": verses_dict
    }


### THANHLINH VIETNAMESE PSALM PARSER ###
def parse_thanhlinh_psalm_to_dict(raw_text):
    """Specifically parses ThanhLinh Vietnamese psalm strings into citation, response, and numbered verses."""
    if not raw_text:
        return {"citation": "", "response": "", "verses": {}}
        
    cleaned = raw_text.strip()
    citation_text = ""
    response_text = ""
    verses_list = []
    
    match_broader = re.search(r'^((?:Tv|Ps|Thánh\s*Vịnh)[\d\s:,\-a-zà-ỹÀ-Ỹ]+)', cleaned, re.IGNORECASE)
    if match_broader and len(match_broader.group(1)) < 30:
        citation_text = match_broader.group(1).strip()
        cleaned = cleaned[len(citation_text):].strip()

    cleaned_flat = " ".join(cleaned.split())

    marker = None
    if "Ðáp:" in cleaned_flat:
        marker = "Ðáp:"
    elif "Đáp:" in cleaned_flat:
        marker = "Đáp:"
    elif "R." in cleaned_flat:
        marker = "R."
        
    if marker:
        parts = cleaned_flat.split(marker)
        if len(parts) > 1:
            refrain_segment = parts[1].strip()
            match_end = re.search(r'(\(?[0-9a-zA-ZÀ-Ỹa-zà-ỹ\.\s]+\)?\.\s*["\u201d]?|[\.?!]\s*["\u201d]?)', refrain_segment)
            if match_end and match_end.start() > 5:
                end_idx = match_end.end()
                response_text = marker + " " + refrain_segment[:end_idx].strip()
            else:
                response_text = marker + " " + refrain_segment.split('.')[0] + "."

    body_text = cleaned_flat
    if response_text in body_text:
        body_text = body_text.replace(response_text, "", 1)

    split_stanzas = re.split(r'(?=\s+\d+\.\s+)', body_text)
    for stz in split_stanzas:
        stz_clean = stz.strip()
        if re.match(r'^\d+\.\s+', stz_clean):
            for r_marker in ["R.", "Ðáp:", "Đáp:"]:
                if r_marker in stz_clean:
                    stz_clean = stz_clean.split(r_marker)[0].strip()
            content_only = re.sub(r'^\d+\.\s*', '', stz_clean).strip()
            if content_only:
                verses_list.append(stz_clean)

    verses_dict = {}
    for i, verse_text in enumerate(verses_list, start=1):
        clean_v = verse_text.strip()
        if not re.match(r'^\d+\.', clean_v):
            verses_dict[f"verse{i}"] = f"{i}. {clean_v}"
        else:
            verses_dict[f"verse{i}"] = clean_v

    return {
        "citation": citation_text,
        "response": response_text,
        "verses": verses_dict
    }


### TEMPLATE DATA PREPARATION & VALIDATION ###
def prepare_template_data(user_inputs, scraped_eng, scraped_viet):
    """Populates the master dictionary using tailored parsers for English and Vietnamese with validation warnings."""
    final_data = {
        "feast_day": scraped_eng.get("feast_day"),
        "citations": {},
        "eng": {}, 
        "viet": {},
        "hymns": user_inputs.get("hymns", {}),
        "warnings": []
    }
    
    required_keys = ["feast_day", "reading1", "psalm", "alleluia", "gospel"]
    
    sections = ["reading1", "psalm", "reading2", "alleluia", "gospel"]
    
    for section in sections:
        idx = user_inputs.get(section, {}).get("option_index", 0)
        
        # 1. Parse English
        eng_parsed = None
        if section in scraped_eng and len(scraped_eng[section]) > idx:
            val_eng = scraped_eng[section][idx]
            if section == "psalm" and val_eng:
                eng_parsed = parse_usccb_psalm_to_dict(val_eng)
            elif section == "alleluia" and val_eng:
                eng_parsed = parse_alleluia_text(val_eng)
            elif val_eng:
                eng_parsed = parse_reading_to_dict(val_eng)
                
        # 2. Parse Vietnamese
        viet_parsed = None
        if section in scraped_viet and len(scraped_viet[section]) > idx:
            val_viet = scraped_viet[section][idx]
            if section == "psalm" and val_viet:
                viet_parsed = parse_thanhlinh_psalm_to_dict(val_viet)
            elif section == "alleluia" and val_viet:
                viet_parsed = parse_alleluia_text(val_viet)
            elif val_viet:
                viet_parsed = parse_reading_to_dict(val_viet)

        # 3. Store top-level shared citation
        citation_val = ""
        if eng_parsed and eng_parsed.get("citation"):
            citation_val = eng_parsed.get("citation")
        elif viet_parsed and viet_parsed.get("citation"):
            citation_val = viet_parsed.get("citation")
            
        final_data["citations"][section] = citation_val

        # 4. Assign text bodies
        if eng_parsed:
            if section == "psalm":
                final_data["eng"]["psalm"] = {
                    "response": eng_parsed.get("response"),
                    "verses": eng_parsed.get("verses")
                }
            elif section == "alleluia":
                final_data["eng"]["alleluia"] = eng_parsed.get("text")
            else:
                final_data["eng"][section] = eng_parsed.get("text")
        else:
            final_data["eng"][section] = None

        if viet_parsed:
            if section == "psalm":
                final_data["viet"]["psalm"] = {
                    "response": viet_parsed.get("response"),
                    "verses": viet_parsed.get("verses")
                }
            elif section == "alleluia":
                final_data["viet"]["alleluia"] = viet_parsed.get("text")
            else:
                final_data["viet"][section] = viet_parsed.get("text")
        else:
            final_data["viet"][section] = None

    
    # 1. Check for missing or empty mandatory keys across eng/viet/top-level
    for key in required_keys:
        if key == "feast_day":
            if not final_data.get("feast_day") or final_data.get("feast_day") == "Daily Readings":
                final_data["warnings"].append("Warning: 'feast_day' was not properly identified.")
        else:
            eng_val = final_data["eng"].get(key)
            viet_val = final_data["viet"].get(key)
            if not eng_val and not viet_val:
                final_data["warnings"].append(f"Warning: Required section '{key}' is missing text in both English and Vietnamese.")

    # 2. Check for missing citations for any section that has text
    all_sections = ["reading1", "psalm", "reading2", "alleluia", "gospel"]
    for key in all_sections:
        has_text = final_data["eng"].get(key) or final_data["viet"].get(key)
        # For psalm, text is a dict with responses/verses, so check accordingly or check presence
        if key == "psalm":
            has_text = final_data["eng"].get("psalm") or final_data["viet"].get("psalm")
            
        if has_text and not final_data["citations"].get(key):
            final_data["warnings"].append(f"Warning: Citation for section '{key}' is missing.")

    # 3. Check if it's a Sunday and any reading is completely missing text
    date_str = user_inputs.get("date")
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%m%d%y")
            is_sunday = (dt.weekday() == 6)
            if is_sunday:
                for key in all_sections:
                    if not final_data["eng"].get(key) and not final_data["viet"].get(key):
                        final_data["warnings"].append(f"Sunday Warning: No text found for '{key}' on a Sunday service.")
        except Exception:
            pass
        
    return final_data
