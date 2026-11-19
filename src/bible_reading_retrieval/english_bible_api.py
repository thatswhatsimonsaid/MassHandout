import re
from http import HTTPStatus
from typing import Optional, Tuple

import requests
from attr import dataclass

from src.bible_reading_retrieval import books_of_the_bible_translation
from src.bible_reading_retrieval.liturgy_of_the_word_section import LiturgyOfTheWordSectionEnglish


@dataclass
class CONSTANTS:
    BIBLE_API_ENGLISH_TRANSLATION = "web"
    BIBLE_API_PSALMS_BOOK_CODE = "PSA"


def _santitize_bible_passage_reference(bible_passage_reference: str) -> str:
    bible_passage_reference = bible_passage_reference.replace("—", "-")  # Replace 'em-dash' with 'hyphen
    bible_passage_reference = bible_passage_reference.strip().rstrip(".")  # Remove (any) trailing periods

    # Example: "Hosea 11:1-4, 8e-9" -> Book: "Hosea", Verses: "11:1-4, 8e-9"
    trailing_verse_letter_match = re.match(r"^(.*?)\s+(\d+[:].*)$", bible_passage_reference)
    if trailing_verse_letter_match is not None:
        book_part, verse_part = trailing_verse_letter_match.groups()

        # Strip out unwanted lowercase/uppercase letters attached to verse numbers (e.g., '8e' -> '8')
        # This regex looks for letters immediately following numbers or verse codes and removes them,
        # while keeping digits, colons, hyphens, commas, and spaces.
        cleaned_verses = re.sub(r"(?<=\d)[a-zA-Z]+", "", verse_part)

        # Recombine and replace spaces with '+' for the URL
        bible_passage_reference = f"{book_part} {cleaned_verses}"

    bible_passage_reference = bible_passage_reference.replace(" ", "+")  # Replace spaces with '+' character
    return bible_passage_reference


def _fetch_english_psalm_locally(
    psalm_num: str, verse_spec: str, translation: str = CONSTANTS.BIBLE_API_ENGLISH_TRANSLATION
) -> str:
    """Fetches the full psalm chapter and slices verses locally to avoid 404s on fragmented single verses."""
    URL = f"https://bible-api.com/{CONSTANTS.BIBLE_API_PSALMS_BOOK_CODE}+{psalm_num}?translation={translation}"
    print("Bible-API URL:", URL)

    res = requests.get(URL)
    print("STATUS-CODE:", res.status_code)
    if res.status_code != HTTPStatus.OK:
        return ""

    full_psalm_data = dict(res.json())
    verses_dict = {verse["verse"]: verse["text"] for verse in full_psalm_data.get("verses", [])}

    # Parse verse spec like "2-3, 5, 6, 8"
    selected_texts = []
    verse_parts = verse_spec.split(",")
    for verse_part in verse_parts:
        verse_part = verse_part.strip()
        if "-" in verse_part:
            try:
                start_str, end_str = verse_part.split("-")
                start, end = int(start_str), int(end_str)
                for verse in range(start, end + 1):
                    if verse in verses_dict:
                        selected_texts.append(verses_dict[verse])
            except ValueError:
                continue
        else:
            try:
                verse = int(verse_part)
                if verse in verses_dict:
                    selected_texts.append(verses_dict[verse])
            except ValueError:
                continue

    return " ".join(selected_texts) if len(selected_texts) > 0 else ""


def get_english_bible_section(
    lit_word_section: str, bible_passage_reference: Optional[str] = None
) -> Tuple[LiturgyOfTheWordSectionEnglish, Optional[str]]:
    liturgy_of_the_word_section = LiturgyOfTheWordSectionEnglish.to_liturgy_of_the_word_section(
        lit_word_section=lit_word_section
    )
    if bible_passage_reference is None:
        return tuple([liturgy_of_the_word_section.value, None])

    bible_passage_reference_code = books_of_the_bible_translation.get_bible_api_universal_code(bible_passage_reference)
    print("Bible Passage Reference Code (English):", bible_passage_reference_code)

    # santitized_reference = _santitize_bible_passage_reference("Exodus 14:15—15:1")
    # santitized_reference = _santitize_bible_passage_reference("2 Timothy 1:1-8")
    santitized_reference = _santitize_bible_passage_reference(bible_passage_reference)
    URL = f"https://bible-api.com/{santitized_reference}?translation={CONSTANTS.BIBLE_API_ENGLISH_TRANSLATION}"
    print("Bible-API URL (Santitized):", URL)

    bible_passage_text = ""
    # Check if it's a Psalm and handle locally to prevent 404s on fragmented verses
    psalm_match = re.match(r"^(?:Psalm|Psalms)\s+(\d+):(.+)$", santitized_reference, re.IGNORECASE)
    if psalm_match is not None:
        psalm_num, verse_spec = psalm_match.groups()
        print(f"Fetching English Psalm {psalm_num} locally ({CONSTANTS.BIBLE_API_ENGLISH_TRANSLATION.upper()})...")
        bible_passage_text = _fetch_english_psalm_locally(psalm_num, verse_spec)
        print(bible_passage_text)
    else:
        res = requests.get(URL)
        print("STATUS-CODE:", res.status_code)

        bible_passage_all_data = dict(res.json())
        # print(json.dumps(bible_passage_all_data, indent=2))

        bible_passage_text = str(bible_passage_all_data.get("text"))
        # Replace embedded newlines (and any accidental double spaces) with a single space
        bible_passage_text = " ".join(bible_passage_text.split())
        # print(bible_passage_text)

    return tuple([liturgy_of_the_word_section.value, bible_passage_text])
