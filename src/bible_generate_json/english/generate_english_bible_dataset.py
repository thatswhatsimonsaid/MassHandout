# Note: This Python script was originally inspired by https://github.com/nirmalben/bible-nabre-json-dataset/blob/master/generate_nabre.py,
# but it has been modified for our use-cases.

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

import requests
from attr import dataclass
from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement
from pydantic import BaseModel

from src.bible_reading_retrieval.english.english_catholic_bible_books import CatholicEnglishBibleBook


@dataclass
class CONSTANTS:
    HEADING_TAGS = ["h2", "h3", "h4", "h5", "h6"]

    VERSE_CLASS_PATTERN = re.compile(r"^[A-Za-z0-9]+-(\d+)-(\d+[a-z]*)$")
    INLINE_HEADING_CLASS_PATTERN = re.compile(r"^inline-h\d+$")
    ROMAN_NUMERAL_PATTERN = re.compile(r"^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")

    CHAPTERS_FILE = Path(
        f"{os.getcwd()}/src/bible_generate_json/english/prerequisite_data/bible-english-nabre-book-chapters.json"
    )
    OUTPUT_DIR = Path(f"{os.getcwd()}/src/bible_reading_retrieval/english/generated_data/books")
    OUTPUT_FILE = Path(f"{os.getcwd()}/src/bible_reading_retrieval/english/generated_data/nabre.json")


class CatholicBibleVerseContent(BaseModel):
    verse: int
    header: Optional[str] = ""
    text: str


class CatholicBibleChapterContent(BaseModel):
    chapter: int
    verses: List[CatholicBibleVerseContent]


class CatholicBibleBookContent(BaseModel):
    book: CatholicEnglishBibleBook
    chapters: List[CatholicBibleChapterContent]


class EmbeddedVerse(NamedTuple):
    book: CatholicEnglishBibleBook
    from_chapter: int
    from_verse: int
    to_chapter: int
    to_verse: int
    text: str


# Verses that Bible Gateway embeds at the end of the previous chapter's last verse.
# (book, from_chapter, from_verse, to_chapter, to_verse, text)
EMBEDDED_VERSES: List[EmbeddedVerse] = [
    ("Wisdom", 11, 26, 12, 1, "for your imperishable spirit is in all things!"),
    ("Daniel", 10, 21, 11, 1, "and in the first year of Darius the Mede I stood to strengthen him and be his refuge."),
]


def _clean_text(text: str) -> str:
    return " ".join(text.split())


def _get_verse_num(tag: Tag) -> Optional[int]:
    """Return the int verse number from a tag's 'Book-ch-v' class, or None."""
    for tag_class in tag.get("class", []):
        verse_class_pattern_patch = CONSTANTS.VERSE_CLASS_PATTERN.match(tag_class)
        if verse_class_pattern_patch is not None:
            # "1a", "1b" etc. are folded into verse 1
            return int(re.match(r"\d+", verse_class_pattern_patch.group(2)).group())
    return None


def _is_inline_heading(node: PageElement) -> bool:
    return isinstance(node, Tag) and any(
        CONSTANTS.INLINE_HEADING_CLASS_PATTERN.match(node_class) for node_class in node.get("class", [])
    )


def _fetch_chapter(book: str, ch: int) -> List[Dict[str, Any]]:
    res = requests.get(
        "https://www.biblegateway.com/passage/",
        params={"search": f"{book} {ch}", "version": "NABRE"},
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        timeout=30,
    )
    res.raise_for_status()
    passage = BeautifulSoup(res.text, "html.parser").select_one(".passage-text")
    if passage is None:
        raise RuntimeError(f"No passage-text for {book} {ch}")

    # Keep section headings; strip notes, verse/chapter numbers, outline divisions, and "Chapter N" labels.
    for html_elem_selector in passage.select(
        "sup.footnote, sup.crossreference, .footnotes, .crossrefs, "
        "h1, h2.outline, h3.chapter, h4.chapter, .versenum, .chapternum"
    ):
        html_elem_selector.decompose()

    for br_selector in passage.find_all("br"):
        br_selector.replace_with(" ")

    verses: Dict[int, List[str]] = {}  # int verse number -> list of text parts
    headers: Dict[int, List[str]] = {}  # int verse number -> list of heading strings
    pending_headers: List[str] = []  # headings seen but not yet attached to a verse

    def add_header(text: str):
        title = _clean_text(text).removesuffix(".")
        if len(title) > 0 and (CONSTANTS.ROMAN_NUMERAL_PATTERN.fullmatch(title) is None):
            pending_headers.append(title)

    def attach_text(num: int, text: str):
        if len(text) == 0:
            return
        if len(pending_headers) > 0:
            headers.setdefault(num, []).extend(pending_headers)
            pending_headers.clear()
        verses.setdefault(num, []).append(text)

    # Walk headings and verse spans in document order
    for html_elem_selector in passage.find_all(CONSTANTS.HEADING_TAGS + ["span"]):
        if html_elem_selector.name in CONSTANTS.HEADING_TAGS:
            add_header(html_elem_selector.get_text())
            continue

        # Only verse-text spans, and skip spans that live inside a heading
        if "text" not in html_elem_selector.get("class", []) or html_elem_selector.find_parent(CONSTANTS.HEADING_TAGS):
            continue
        num = _get_verse_num(html_elem_selector)
        if num is None:
            continue

        buffer: List[str] = []

        def flush() -> None:
            attach_text(num, _clean_text("".join(buffer)))
            buffer.clear()

        def walk_span(node: Tag) -> None:
            for child in node.children:
                if _is_inline_heading(child):
                    flush()
                    add_header(child.get_text())
                elif isinstance(child, Tag) and child.find(_is_inline_heading):
                    walk_span(child)
                elif isinstance(child, Tag):
                    buffer.append(child.get_text())
                else:
                    buffer.append(str(child))

        walk_span(html_elem_selector)
        flush()

    result: List[Dict[str, Any]] = []
    for verse, parts in sorted(verses.items()):
        item: Dict[str, Any] = {"verse": verse}
        if verse in headers:
            # Several headings in a row (e.g. section + subsection) are joined
            item["header"] = " — ".join(headers[verse])
        item["text"] = " ".join(parts)
        result.append(item)
    return result


def apply_embedded_fixes(book: str, chapters: List[CatholicBibleChapterContent]):
    """Split verses that the site glued onto the end of the previous verse."""
    by_num = {c["chapter"]: c for c in chapters}
    for b, from_ch, from_v, to_ch, to_v, tail in EMBEDDED_VERSES:
        if b != book:
            continue
        src, dst = by_num.get(from_ch), by_num.get(to_ch)
        if not src or not dst:
            continue

        if any(v["verse"] == to_v for v in dst["verses"]):
            continue  # already present, nothing to do

        src_verse = next((v for v in src["verses"] if v["verse"] == from_v), None)
        if src_verse and str(src_verse["text"]).rstrip().endswith(tail):
            src_verse["text"] = str(src_verse["text"]).rstrip()[: -len(tail)].rstrip()
            print(f"  [FIX] moved {book} {to_ch}:{to_v} out of {from_ch}:{from_v}")
        else:
            print(
                f"  [FIX] {book} {to_ch}:{to_v} not found at end of {from_ch}:{from_v}; "
                f"inserting anyway, check {from_ch}:{from_v} manually"
            )

        dst["verses"].insert(0, {"verse": to_v, "text": tail})
        dst["verses"].sort(key=lambda v: v["verse"])


def _save_bible(bible: List[Dict[str, Any]]):
    """Write the combined file atomically so it is always valid JSON."""
    tmp = CONSTANTS.OUTPUT_FILE.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(
            bible,
            ensure_ascii=False,
            indent=2,
            default=lambda obj: obj.model_dump(mode="json") if isinstance(obj, BaseModel) else str(obj),
        ),
        encoding="utf-8",
    )
    os.replace(tmp, CONSTANTS.OUTPUT_FILE)


def _parse_catholic_book(name: str) -> CatholicEnglishBibleBook:
    cleaned = name.replace(" ", "")
    for b in CatholicEnglishBibleBook:
        if b.value.replace(" ", "") == cleaned:
            return b
    raise ValueError(f"Unknown book name: {name}")


def main():
    chapter_metadata = json.load(open(CONSTANTS.CHAPTERS_FILE))
    bible: List[CatholicBibleBookContent] = []

    for entry in chapter_metadata:
        book = _parse_catholic_book(entry["Book"])
        num_chapters = int(entry["Chapters"])
        book_file = CONSTANTS.OUTPUT_DIR / f"{book.json_filename}"

        # Resume: reuse books that were already scraped
        if book_file.exists():
            print(f"Skipping {book} (already saved)")
            bible.append(json.loads(book_file.read_text(encoding="utf-8")))
            _save_bible(bible)
            continue

        print(f"Processing Book: {book}")
        chapters: List[CatholicBibleChapterContent] = []

        for ch in range(1, num_chapters + 1):
            print(f"  Chapter {ch}", end="", flush=True)
            try:
                verses = _fetch_chapter(book, ch)
            except Exception as e:
                print(f"  [ERROR] {e}")
                verses = []
            else:
                n_hdr = sum(1 for v in verses if "header" in v)
                print(f"  ({len(verses)} verses, {n_hdr} headers)" + ("  [WARN] empty" if not verses else ""))
            chapters.append({"chapter": ch, "verses": verses})
            time.sleep(0.3)

        apply_embedded_fixes(book, chapters)

        book_obj = CatholicBibleBookContent(book=book, chapters=chapters)
        bible.append(book_obj)

        # Save this book, then update the main bible file before moving on
        book_file.write_text(book_obj.model_dump_json(indent=2), encoding="utf-8")
        _save_bible(bible)
        print(f"  -> saved {book} ({len(bible)} books in {CONSTANTS.OUTPUT_FILE})")

    print(f"Done. Wrote {CONSTANTS.OUTPUT_FILE}")


if __name__ == "__main__":
    CONSTANTS.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    main()
