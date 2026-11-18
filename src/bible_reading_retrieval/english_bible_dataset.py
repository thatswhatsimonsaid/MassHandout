from typing import Optional, List

import requests
import sys


def get_english_bible_section(lit_word_section: str, bible_passage_reference: Optional[str] = None):
    # parts = ["2", "Timothy", "1:1-8"]
    combined_book_name = "John"
    res = requests.get(
        f"https://raw.githubusercontent.com/nirmalben/bible-nabre-json-dataset/refs/heads/master/generated_data/books/{combined_book_name}.json"
    )
    book_data = res.json()

    target_chapter = 1
    start_verse = 1
    end_verse = 18

    chapter_data = next((ch for ch in book_data.get("chapters", []) if dict(ch).get("chapter") == target_chapter), None)
    if chapter_data is None:
        print(f"Chapter {target_chapter} not found.")
        return None

    selected_texts = [
        v["text"] for v in dict(chapter_data).get("verses", []) if start_verse <= dict(v).get("verse", 0) <= end_verse
    ]

    # Join the verses into a single reading block
    concatenated_reading = " ".join(selected_texts)

    print(f"--- {lit_word_section.upper()} ({bible_passage_reference}) ---")
    print(concatenated_reading)

    return concatenated_reading


def main(args: List[str]):
    get_english_bible_section("first-readings", "2 Timothy 1:1-8")


if __name__ == "__main__":
    main(sys.argv)
