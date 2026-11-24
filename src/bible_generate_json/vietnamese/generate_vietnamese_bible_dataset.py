# Note: Inspired by https://github.com/v-bible/bible-scraper/blob/main/src/ktcgkpv.org/main.ts
# and mirrored after src/bible_generate_json/english/generate_english_bible_dataset.py.
# Calls ktcgkpv.org's JSON POST API directly via requests + BeautifulSoup (no Playwright or Prisma).

import argparse
import json
import os
import re
import time
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Sequence, Tuple

import requests
from attr import dataclass
from bs4 import BeautifulSoup, Comment, NavigableString, Tag
from pydantic import BaseModel

from src.bible_reading_retrieval.vietnamese.vietnamese_catholic_bible_books import (
    KTCG_BOOK_ID_TO_VIETNAMESE_BOOK,
    CatholicVietnameseBibleBook,
)


class KTCGKPV_Version(IntEnum):
    KT2011 = 1  # KPA : ấn bản KT 2011 (all 73 Catholic books)
    KT2021 = 2  # KPB : ấn bản KT 2021 (currently 8 Old Testament books on ktcgkpv.org)
    LCCMN = 3  # KPA : ấn bản LCCMN (all 73 Catholic books, same text as KT 2011)


PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class CONSTANTS:
    BASE_URL = "https://ktcgkpv.org"
    BIBLE_PAGE_URL = f"{BASE_URL}/bible"
    CONTENT_VIEW_URL = f"{BASE_URL}/bible/content-view"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

    REQUEST_TIMEOUT_SECONDS = 30
    REQUEST_DELAY_SECONDS = 0.3
    MAX_RETRIES = 4

    HEADING_TAGS = ("h2", "h3", "h4", "h5", "h6")
    BLOCK_TAGS = ("p", "div", "li", "blockquote")
    NOISE_SELECTOR = "sup.note, sup.reference, p.chapter-num, p.ref-para, h1"

    CHAPTER_VERSES_JS_PATTERN = re.compile(
        r"""a\[data-chapter=['"](?P<chapter>[^'"]+)['"]\]["']\)"""
        r"""\.data\(['"]verses['"],\s*\$\.parseJSON\('(?P<json>[^']+)'\)\)"""
    )
    VERSE_LABEL_PATTERN = re.compile(r"^(?P<start>\d+)(?:-(?P<end>\d+))?")
    ROMAN_NUMERAL_PATTERN = re.compile(r"^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")

    # Daniel 3 Greek addition (24*..90*) has 67 verses; trailing Aramaic 24..33 map to NABRE 91..100.
    DANIEL_CH3_ARAMAIC_OFFSET = 67

    GENERATED_DATA_DIR = PROJECT_ROOT / "src/bible_reading_retrieval/vietnamese/generated_data"
    OUTPUT_DIR = GENERATED_DATA_DIR / "books"


class CatholicBibleVerseContent(BaseModel):
    verse: int
    verse_end: Optional[int] = None
    label: str = ""
    header: Optional[str] = ""
    text: str


class CatholicBibleChapterContent(BaseModel):
    chapter: int
    verses: List[CatholicBibleVerseContent]


class CatholicBibleBookContent(BaseModel):
    book: CatholicVietnameseBibleBook
    chapters: List[CatholicBibleChapterContent]


class KtcgBookCatalogEntry(NamedTuple):
    book_id: str
    book_abbr: str
    book: CatholicVietnameseBibleBook
    # Ordered list of (chapter_number, first_verse_label, last_verse_label)
    chapters: List[Tuple[int, str, str]]


def _clean_text(text: str) -> str:
    cleaned = " ".join(text.split())
    # Remove stray whitespace left before punctuation after decomposing inline note/ref <sup> tags
    cleaned = re.sub(r"\s+([,.;:!?])", r"\1", cleaned)
    cleaned = re.sub(r"“\s+", "“", cleaned)
    cleaned = re.sub(r"\s+”", "”", cleaned)
    return cleaned


def _parse_verse_label(raw_label: str) -> Optional[Tuple[int, Optional[int], str]]:
    """Parse a verse marker into (start_verse, end_verse, clean_label).

    Examples: '1' -> (1, None, '1'), '4a' -> (4, None, '4a'), '24*' -> (24, None, '24*'),
    '37-38' -> (37, 38, '37-38').
    """
    clean_label = raw_label.strip()
    match = CONSTANTS.VERSE_LABEL_PATTERN.match(clean_label)
    if match is None:
        return None
    start = int(match.group("start"))
    end = int(match.group("end")) if match.group("end") is not None else None
    return start, end, clean_label


def _request_with_retry(
    session: requests.Session,
    method: str,
    url: str,
    **kwargs: Any,
) -> requests.Response:
    last_exc: Optional[Exception] = None
    for attempt in range(1, CONSTANTS.MAX_RETRIES + 1):
        try:
            res = session.request(method, url, timeout=CONSTANTS.REQUEST_TIMEOUT_SECONDS, **kwargs)
            res.raise_for_status()
            return res
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < CONSTANTS.MAX_RETRIES:
                time.sleep(float(2 ** (attempt - 1)))
    raise RuntimeError(f"Request failed after {CONSTANTS.MAX_RETRIES} attempts ({url}): {last_exc}")


def _fetch_catalog(
    session: requests.Session,
    version: KTCGKPV_Version,
    include_prologue: bool = False,
) -> List[KtcgBookCatalogEntry]:
    """Fetch book list and exact (chapter, first_verse, last_verse) ranges from ktcgkpv.org."""
    res = _request_with_retry(session, "GET", CONSTANTS.BIBLE_PAGE_URL, params={"version": int(version)})
    html = res.text
    soup = BeautifulSoup(html, "html.parser")

    # Parse embedded jQuery verse maps: book_id -> {chapter_num -> (first_verse, last_verse)}
    book_chapters: Dict[str, Dict[int, Tuple[str, str]]] = {}
    for match in CONSTANTS.CHAPTER_VERSES_JS_PATTERN.finditer(html):
        raw_chapter = match.group("chapter").strip()
        if not raw_chapter.isdigit():
            continue
        chapter_num = int(raw_chapter)
        if chapter_num == 0 and not include_prologue:
            continue

        verses_by_book: Dict[str, str] = json.loads(match.group("json"))
        for book_id, verse_csv in verses_by_book.items():
            verse_labels = [v.strip() for v in verse_csv.split(",") if v.strip()]
            if not verse_labels:
                continue
            book_chapters.setdefault(book_id, {})[chapter_num] = (verse_labels[0], verse_labels[-1])

    catalog: List[KtcgBookCatalogEntry] = []
    for btn in soup.select("#bookSelectDialog button[data-book-id]"):
        if btn.get("data-book-isintro") == "1":
            continue
        book_id = (btn.get("data-book-id") or "").strip()
        book_abbr = (btn.get("data-book-abbr") or "").strip()
        book = KTCG_BOOK_ID_TO_VIETNAMESE_BOOK.get(book_id)
        if book is None:
            continue

        chapters_map = book_chapters.get(book_id, {})
        if not chapters_map:
            continue

        ordered_chapters = [(ch, bounds[0], bounds[1]) for ch, bounds in sorted(chapters_map.items())]
        catalog.append(
            KtcgBookCatalogEntry(
                book_id=book_id,
                book_abbr=book_abbr,
                book=book,
                chapters=ordered_chapters,
            )
        )

    return catalog


def _normalize_daniel_chapter_3(verses: List[CatholicBibleVerseContent]) -> List[CatholicBibleVerseContent]:
    """Normalize Daniel 3 trailing Aramaic verses (24..33 after 24*..90*) to NABRE/USCCB 91..100.

    Preserves the original ktcgkpv.org verse label (e.g. label='24', verse=91) while preventing
    collisions with 24*..33* and matching USCCB Lectionary citations (e.g. Daniel 3:91-95).
    """
    seen_starred = False
    normalized: List[CatholicBibleVerseContent] = []
    for verse in verses:
        if verse.label.endswith("*"):
            seen_starred = True
            normalized.append(verse)
        elif seen_starred:
            shifted_end = verse.verse_end + CONSTANTS.DANIEL_CH3_ARAMAIC_OFFSET if verse.verse_end is not None else None
            normalized.append(
                verse.model_copy(
                    update={
                        "verse": verse.verse + CONSTANTS.DANIEL_CH3_ARAMAIC_OFFSET,
                        "verse_end": shifted_end,
                    }
                )
            )
        else:
            normalized.append(verse)
    return normalized


def _parse_chapter_html(content_html: str) -> List[CatholicBibleVerseContent]:
    """Parse ktcgkpv.org chapter HTML into ordered verses with exact labels, spans, and headers."""
    soup = BeautifulSoup(content_html, "html.parser")

    # Strip footnotes, cross-references, chapter number badges, reference paragraphs, and book titles
    for elem in soup.select(CONSTANTS.NOISE_SELECTOR):
        elem.decompose()

    for br in soup.find_all("br"):
        br.replace_with(" ")

    drafts: List[Dict[str, Any]] = []
    current_draft: Optional[Dict[str, Any]] = None
    pending_headers: List[str] = []
    buffer: List[str] = []

    def add_header(text: str) -> None:
        title = _clean_text(text).removesuffix(".")
        if len(title) > 0 and (CONSTANTS.ROMAN_NUMERAL_PATTERN.fullmatch(title) is None):
            pending_headers.append(title)

    def flush() -> None:
        if not buffer:
            return
        text = _clean_text("".join(buffer))
        buffer.clear()
        if not text or current_draft is None:
            return
        if pending_headers:
            current_draft["headers"].extend(pending_headers)
            pending_headers.clear()
        current_draft["parts"].append(text)

    def walk(node: Tag) -> None:
        nonlocal current_draft
        for child in node.children:
            if isinstance(child, Comment):
                continue
            if isinstance(child, NavigableString):
                buffer.append(str(child))
                continue
            if not isinstance(child, Tag):
                continue

            if child.name in CONSTANTS.HEADING_TAGS:
                flush()
                add_header(child.get_text())
            elif child.name == "sup" and "verse-num" in child.get("class", []):
                flush()
                parsed = _parse_verse_label(child.get_text())
                if parsed is not None:
                    start, end, clean_label = parsed
                    if current_draft is None or current_draft["label"] != clean_label:
                        current_draft = {
                            "verse": start,
                            "verse_end": end,
                            "label": clean_label,
                            "headers": [],
                            "parts": [],
                        }
                        drafts.append(current_draft)
            elif child.name in CONSTANTS.BLOCK_TAGS:
                flush()
                walk(child)
                flush()
            else:
                # Inline tags (span, a.proper-name, i, b, empty poetry spacer <sup>)
                walk(child)

    walk(soup)
    flush()

    result: List[CatholicBibleVerseContent] = []
    for draft in drafts:
        if not draft["parts"]:
            continue
        header_str = " — ".join(draft["headers"]) if draft["headers"] else ""
        result.append(
            CatholicBibleVerseContent(
                verse=draft["verse"],
                verse_end=draft["verse_end"],
                label=draft["label"],
                header=header_str,
                text=_clean_text(" ".join(draft["parts"])),
            )
        )
    return result


def _fetch_chapter(
    session: requests.Session,
    version: KTCGKPV_Version,
    entry: KtcgBookCatalogEntry,
    chapter_num: int,
    from_verse: str,
    to_verse: str,
) -> List[CatholicBibleVerseContent]:
    payload = {
        "version": str(int(version)),
        "book": entry.book_id,
        "book_abbr": entry.book_abbr,
        "is_intro": "",
        "from_chapter": str(chapter_num),
        "from_verse": from_verse,
        "to_chapter": str(chapter_num),
        "to_verse": to_verse,
    }
    res = _request_with_retry(session, "POST", CONSTANTS.CONTENT_VIEW_URL, data=payload)
    body = dict(res.json())
    if not body.get("success") or not (body.get("data") or {}).get("content"):
        raise RuntimeError(f"Empty response for {entry.book} {chapter_num}: {body.get('msg')}")

    verses = _parse_chapter_html(body["data"]["content"])
    if entry.book == CatholicVietnameseBibleBook.DANIEL and chapter_num == 3:
        verses = _normalize_daniel_chapter_3(verses)
    return verses


def _find_missing_verses(verses: Sequence[CatholicBibleVerseContent]) -> List[int]:
    if not verses:
        return []
    present = {n for v in verses for n in range(v.verse, (v.verse_end or v.verse) + 1)}
    max_verse = max(present)
    return [n for n in range(1, max_verse + 1) if n not in present]


def _save_bible(bible: Sequence[CatholicBibleBookContent], output_file: Path) -> None:
    """Write the combined JSON file atomically so it is always valid JSON."""
    serialized = [
        book.model_dump(mode="json", exclude_none=True) if isinstance(book, BaseModel) else book for book in bible
    ]
    tmp = output_file.with_suffix(".tmp")
    tmp.write_text(json.dumps(serialized, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, output_file)


def _parse_cli_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape Vietnamese Catholic Bible JSON dataset from ktcgkpv.org.")
    parser.add_argument(
        "--version",
        choices=[v.name for v in KTCGKPV_Version],
        default=KTCGKPV_Version.KT2011.name,
        help="ktcgkpv.org Bible version to scrape (default: KT2011).",
    )
    parser.add_argument(
        "--include-prologue",
        action="store_true",
        help="Include chapter 0 prologues (e.g. Sirach / Huấn Ca prologue).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-scrape books even if their JSON file already exists on disk.",
    )
    return parser.parse_args(argv)


def main(
    version: KTCGKPV_Version = KTCGKPV_Version.KT2011,
    include_prologue: bool = False,
    force: bool = False,
) -> None:
    CONSTANTS.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = CONSTANTS.GENERATED_DATA_DIR / f"{version.name.lower()}.json"

    session = requests.Session()
    session.headers.update({"User-Agent": CONSTANTS.USER_AGENT})

    print(f"Fetching catalog from ktcgkpv.org (version={version.name}, id={int(version)})...")
    catalog = _fetch_catalog(session, version=version, include_prologue=include_prologue)
    print(f"Found {len(catalog)} book(s) to process.")

    bible: List[CatholicBibleBookContent] = []

    for entry in catalog:
        book_file = CONSTANTS.OUTPUT_DIR / entry.book.json_filename

        # Resume: reuse books that were already scraped
        if book_file.exists() and not force:
            print(f"Skipping {entry.book} (already saved)")
            cached_book = CatholicBibleBookContent.model_validate_json(book_file.read_text(encoding="utf-8"))
            bible.append(cached_book)
            _save_bible(bible, output_file)
            continue

        print(f"Processing Book: {entry.book} ({len(entry.chapters)} chapters)")
        chapters: List[CatholicBibleChapterContent] = []

        for ch, from_verse, to_verse in entry.chapters:
            print(f"  Chapter {ch}", end="", flush=True)
            try:
                verses = _fetch_chapter(session, version, entry, ch, from_verse, to_verse)
            except Exception as exc:
                print(f"  [ERROR] {exc}")
                verses = []
            else:
                n_hdr = sum(1 for v in verses if v.header)
                missing = _find_missing_verses(verses)
                warn_msg = "  [WARN] empty" if not verses else ""
                if missing:
                    warn_msg += f"  [WARN] missing verses: {missing}"
                print(f"  ({len(verses)} verses, {n_hdr} headers){warn_msg}")

            chapters.append(CatholicBibleChapterContent(chapter=ch, verses=verses))
            time.sleep(CONSTANTS.REQUEST_DELAY_SECONDS)

        book_obj = CatholicBibleBookContent(book=entry.book, chapters=chapters)
        bible.append(book_obj)

        # Save per-book JSON, then atomically update combined Bible file
        book_file.write_text(
            json.dumps(book_obj.model_dump(mode="json", exclude_none=True), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        _save_bible(bible, output_file)
        print(f"  -> saved {entry.book} ({len(bible)} books in {output_file})")

    print(f"Done. Wrote {output_file}")


if __name__ == "__main__":
    cli_args = _parse_cli_args()
    main(
        version=KTCGKPV_Version[cli_args.version],
        include_prologue=cli_args.include_prologue,
        force=cli_args.force,
    )
