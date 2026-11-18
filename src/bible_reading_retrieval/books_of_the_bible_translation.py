import re
from typing import Dict, Literal, TypedDict, Union


class BookMetadata(TypedDict):
    vietTranslation: str  # Clean liturgical / Catholic spelling for handouts
    vietTranslationBibleAPI: str  # Exact Cadman 1934 API spelling for URL/query matching
    code: str  # 3-digit USFM code


class ReverseBookMetadata(TypedDict):
    englishTranslation: str
    code: str


BIBLICAL_BOOK_ENGLISH_ALIASES = {
    "Psalm": "Psalms",
    "Song of Songs": "Song of Solomon",
}

BIBLICAL_BOOKS_ENG_TO_VIET_MAP: Dict[str, BookMetadata] = {
    # --- Old Testament (Cựu Ước) - 46 Books ---
    "Genesis": {"vietTranslation": "Sáng Thế", "vietTranslationBibleAPI": "Sáng thế ký", "code": "GEN"},
    "Exodus": {"vietTranslation": "Xuất Hành", "vietTranslationBibleAPI": "Xuất Ê-díp-tô ký", "code": "EXO"},
    "Leviticus": {"vietTranslation": "Lê-vi", "vietTranslationBibleAPI": "Lê-vi ký", "code": "LEV"},
    "Numbers": {"vietTranslation": "Dân Số", "vietTranslationBibleAPI": "Dân số ký", "code": "NUM"},
    "Deuteronomy": {
        "vietTranslation": "Đệ Nhị Luật",
        "vietTranslationBibleAPI": "Phục truyền luật lệ ký",
        "code": "DEU",
    },
    "Joshua": {"vietTranslation": "Giô-suê", "vietTranslationBibleAPI": "Giô-suê", "code": "JOS"},
    "Judges": {"vietTranslation": "Thủ Lãnh", "vietTranslationBibleAPI": "Các quan xét", "code": "JDG"},
    "Ruth": {"vietTranslation": "Rút", "vietTranslationBibleAPI": "Ru-tơ", "code": "RUT"},
    "1 Samuel": {"vietTranslation": "1 Sa-mu-en", "vietTranslationBibleAPI": "I Sa-mu-en", "code": "1SA"},
    "2 Samuel": {"vietTranslation": "2 Sa-mu-en", "vietTranslationBibleAPI": "II Sa-mu-en", "code": "2SA"},
    "1 Kings": {"vietTranslation": "1 Các Vua", "vietTranslationBibleAPI": "I Các Vua", "code": "1KI"},
    "2 Kings": {"vietTranslation": "2 Các Vua", "vietTranslationBibleAPI": "II Các Vua", "code": "2KI"},
    "1 Chronicles": {"vietTranslation": "1 Sử Biên Niên", "vietTranslationBibleAPI": "I Sử ký", "code": "1CH"},
    "2 Chronicles": {"vietTranslation": "2 Sử Biên Niên", "vietTranslationBibleAPI": "II Sử ký", "code": "2CH"},
    "Ezra": {"vietTranslation": "Ét-ra", "vietTranslationBibleAPI": "Ê-xơ-ra", "code": "EZR"},
    "Nehemiah": {"vietTranslation": "Nơ-khe-mi-a", "vietTranslationBibleAPI": "Nê-hê-mi", "code": "NEH"},
    "Tobit": {"vietTranslation": "Tô-bi-a", "vietTranslationBibleAPI": "Tô-bi-a", "code": "TOB"},
    "Judith": {"vietTranslation": "Giu-đi-tha", "vietTranslationBibleAPI": "Giu-đi-tha", "code": "JDT"},
    "Esther": {"vietTranslation": "Ét-te", "vietTranslationBibleAPI": "Ê-xơ-tê", "code": "EST"},
    "1 Maccabees": {"vietTranslation": "1 Ma-ca-bê", "vietTranslationBibleAPI": "Ma-ca-bê 1", "code": "1MA"},
    "2 Maccabees": {"vietTranslation": "2 Ma-ca-bê", "vietTranslationBibleAPI": "Ma-ca-bê 2", "code": "2MA"},
    "Job": {"vietTranslation": "Gióp", "vietTranslationBibleAPI": "Gióp", "code": "JOB"},
    "Psalms": {"vietTranslation": "Thánh Vịnh", "vietTranslationBibleAPI": "Thi Thiên", "code": "PSA"},
    "Proverbs": {"vietTranslation": "Châm Ngôn", "vietTranslationBibleAPI": "Châm ngôn", "code": "PRO"},
    "Ecclesiastes": {"vietTranslation": "Giảng Viên", "vietTranslationBibleAPI": "Truyền đạo", "code": "ECC"},
    "Song of Solomon": {"vietTranslation": "Diễm Ca", "vietTranslationBibleAPI": "Nhã ca", "code": "SNG"},
    "Wisdom": {"vietTranslation": "Khôn Ngoan", "vietTranslationBibleAPI": "Khôn Ngoan", "code": "WIS"},
    "Sirach": {"vietTranslation": "Huấn Ca", "vietTranslationBibleAPI": "Huấn Ca", "code": "SIR"},
    "Isaiah": {"vietTranslation": "I-sai-a", "vietTranslationBibleAPI": "Ê-sai", "code": "ISA"},
    "Jeremiah": {"vietTranslation": "Giê-rê-mi-a", "vietTranslationBibleAPI": "Giê-rê-mi", "code": "JER"},
    "Lamentations": {"vietTranslation": "Ai Ca", "vietTranslationBibleAPI": "Ca thương", "code": "LAM"},
    "Baruch": {"vietTranslation": "Ba-rúc", "vietTranslationBibleAPI": "Ba-rúc", "code": "BAR"},
    "Ezekiel": {"vietTranslation": "Ê-dê-ki-en", "vietTranslationBibleAPI": "Ê-xê-chi-ên", "code": "EZK"},
    "Daniel": {"vietTranslation": "Đa-ni-en", "vietTranslationBibleAPI": "Đa-ni-ên", "code": "DAN"},
    "Hosea": {"vietTranslation": "Hô-sê", "vietTranslationBibleAPI": "Ô-sê", "code": "HOS"},
    "Joel": {"vietTranslation": "Giô-en", "vietTranslationBibleAPI": "Giô-ên", "code": "JOL"},
    "Amos": {"vietTranslation": "A-mốt", "vietTranslationBibleAPI": "A-mốt", "code": "AMO"},
    "Obadiah": {"vietTranslation": "Ô-va-đi-a", "vietTranslationBibleAPI": "Áp-đia", "code": "OBA"},
    "Jonah": {"vietTranslation": "Giô-na", "vietTranslationBibleAPI": "Giô-na", "code": "JON"},
    "Micah": {"vietTranslation": "Mi-kha", "vietTranslationBibleAPI": "Mi-chê", "code": "MIC"},
    "Nahum": {"vietTranslation": "Na-khum", "vietTranslationBibleAPI": "Na-hum", "code": "NAM"},
    "Habakkuk": {"vietTranslation": "Kha-ba-cúc", "vietTranslationBibleAPI": "Ha-ba-cúc", "code": "HAB"},
    "Zephaniah": {"vietTranslation": "Xô-phô-ni-a", "vietTranslationBibleAPI": "Sô-phô-ni", "code": "ZEP"},
    "Haggai": {"vietTranslation": "Khác-gai", "vietTranslationBibleAPI": "A-ghê", "code": "HAG"},
    "Zechariah": {"vietTranslation": "Da-ca-ri-a", "vietTranslationBibleAPI": "Xa-cha-ri", "code": "ZEC"},
    "Malachi": {"vietTranslation": "Ma-la-khi", "vietTranslationBibleAPI": "Ma-la-chi", "code": "MAL"},
    # --- New Testament (Tân Ước) - 27 Books ---
    "Matthew": {"vietTranslation": "Mát-thêu", "vietTranslationBibleAPI": "Ma-thi-ơ", "code": "MAT"},
    "Mark": {"vietTranslation": "Mác-cô", "vietTranslationBibleAPI": "Mác", "code": "MRK"},
    "Luke": {"vietTranslation": "Lu-ca", "vietTranslationBibleAPI": "Lu-ca", "code": "LUK"},
    "John": {"vietTranslation": "Gio-an", "vietTranslationBibleAPI": "Giăng", "code": "JHN"},
    "Acts": {"vietTranslation": "Công Vụ Tông Đồ", "vietTranslationBibleAPI": "Công vụ các Sứ đồ", "code": "ACT"},
    "Romans": {"vietTranslation": "Rô-ma", "vietTranslationBibleAPI": "Rô-ma", "code": "ROM"},
    "1 Corinthians": {"vietTranslation": "1 Cô-rinh-tô", "vietTranslationBibleAPI": "I Cô-rinh-tô", "code": "1CO"},
    "2 Corinthians": {"vietTranslation": "2 Cô-rinh-tô", "vietTranslationBibleAPI": "II Cô-rinh-tô", "code": "2CO"},
    "Galatians": {"vietTranslation": "Ga-lát", "vietTranslationBibleAPI": "Ga-la-ti", "code": "GAL"},
    "Ephesians": {"vietTranslation": "Ê-phê-xô", "vietTranslationBibleAPI": "Ê-phê-sô", "code": "EPH"},
    "Philippians": {"vietTranslation": "Phi-líp-phê", "vietTranslationBibleAPI": "Phi-líp", "code": "PHP"},
    "Colossians": {"vietTranslation": "Cô-lô-xê", "vietTranslationBibleAPI": "Cô-lô-se", "code": "COL"},
    "1 Thessalonians": {
        "vietTranslation": "1 Thê-xa-lô-ni-ca",
        "vietTranslationBibleAPI": "I Tê-sa-lô-ni-ca",
        "code": "1TH",
    },
    "2 Thessalonians": {
        "vietTranslation": "2 Thê-xa-lô-ni-ca",
        "vietTranslationBibleAPI": "II Tê-sa-lô-ni-ca",
        "code": "2TH",
    },
    "1 Timothy": {"vietTranslation": "1 Ti-mô-thê", "vietTranslationBibleAPI": "I Ti-mô-thê", "code": "1TI"},
    "2 Timothy": {"vietTranslation": "2 Ti-mô-thê", "vietTranslationBibleAPI": "II Ti-mô-thê", "code": "2TI"},
    "Titus": {"vietTranslation": "Ti-tô", "vietTranslationBibleAPI": "Tít", "code": "TIT"},
    "Philemon": {"vietTranslation": "Phi-lê-môn", "vietTranslationBibleAPI": "Phi-lê-môn", "code": "PHM"},
    "Hebrews": {"vietTranslation": "Híp-ri", "vietTranslationBibleAPI": "Hê-bơ-rơ", "code": "HEB"},
    "James": {"vietTranslation": "Gia-cô-bê", "vietTranslationBibleAPI": "Gia-cơ", "code": "JAS"},
    "1 Peter": {"vietTranslation": "1 Phê-rô", "vietTranslationBibleAPI": "I Phi-e-rơ", "code": "1PE"},
    "2 Peter": {"vietTranslation": "2 Phê-rô", "vietTranslationBibleAPI": "II Phi-e-rơ", "code": "2PE"},
    "1 John": {"vietTranslation": "1 Gio-an", "vietTranslationBibleAPI": "I Giăng", "code": "1JN"},
    "2 John": {"vietTranslation": "2 Gio-an", "vietTranslationBibleAPI": "II Giăng", "code": "2JN"},
    "3 John": {"vietTranslation": "3 Gio-an", "vietTranslationBibleAPI": "III Giăng", "code": "3JN"},
    "Jude": {"vietTranslation": "Giu-đa", "vietTranslationBibleAPI": "Giu-đe", "code": "JUD"},
    "Revelation": {"vietTranslation": "Khải Huyền", "vietTranslationBibleAPI": "Khải Huyền", "code": "REV"},
}

BIBLICAL_BOOKS_VIET_TO_ENG_MAP: Dict[str, ReverseBookMetadata] = {
    info["vietTranslationBibleAPI"]: {"englishTranslation": eng_name, "code": info["code"]}
    for eng_name, info in BIBLICAL_BOOKS_ENG_TO_VIET_MAP.items()
}


def get_bible_api_universal_code(reference_english: str) -> str:
    parts = re.split(r"\s+(?=\d+(?:[:\-—–]|$))", reference_english.strip(), maxsplit=1)
    book_name = parts[0]
    normalized_book_name = BIBLICAL_BOOK_ENGLISH_ALIASES.get(book_name, book_name)
    if normalized_book_name not in BIBLICAL_BOOKS_ENG_TO_VIET_MAP:
        return ""

    return BIBLICAL_BOOKS_ENG_TO_VIET_MAP.get(normalized_book_name)["code"]


def translate_book_name(
    reference: str, target_language: Union[Literal["English"], Literal["Vietnamese"]] = "Vietnamese"
) -> Dict[str, str]:
    # Splits "2 Timothy 1:1-8" -> ("2 Timothy", "1:1-8")
    # Splits "Ti-mô-thê 2 1:1-8" -> ("Ti-mô-thê 2", "1:1-8")
    # Splits "2 Timothy" -> ("2 Timothy", "")
    parts = re.split(r"\s+(?=\d+(?:[:\-—–]|$))", reference.strip(), maxsplit=1)
    book_name = parts[0]
    verses = parts[1] if len(parts) > 1 else ""

    translated_bible_api = book_name
    translated_actual = book_name
    book_code = ""
    if target_language == "Vietnamese":
        normalized_book_name = BIBLICAL_BOOK_ENGLISH_ALIASES.get(book_name, book_name)
        if normalized_book_name in BIBLICAL_BOOKS_ENG_TO_VIET_MAP:
            translated_bible_api = BIBLICAL_BOOKS_ENG_TO_VIET_MAP.get(normalized_book_name)["vietTranslationBibleAPI"]
            translated_actual = BIBLICAL_BOOKS_ENG_TO_VIET_MAP.get(normalized_book_name)["vietTranslation"]
            book_code = BIBLICAL_BOOKS_ENG_TO_VIET_MAP.get(normalized_book_name)["code"]
        else:
            print("ERROR: English book not found in lookup!")
    elif target_language == "English":
        if book_name in BIBLICAL_BOOKS_VIET_TO_ENG_MAP:
            translated_bible_api = BIBLICAL_BOOKS_VIET_TO_ENG_MAP.get(book_name)["englishTranslation"]
            translated_actual = BIBLICAL_BOOKS_VIET_TO_ENG_MAP.get(book_name)["englishTranslation"]
            book_code = BIBLICAL_BOOKS_ENG_TO_VIET_MAP.get(book_name)["code"]
        else:
            print("ERROR: Vietnamese book not found in lookup!")

    return {
        f"bibleAPITranslatedTo{target_language}": f"{translated_bible_api} {verses}".strip(),
        f"actualTranslatedTo{target_language}": f"{translated_actual} {verses}".strip(),
        "referenceBookCode": book_code,
    }
