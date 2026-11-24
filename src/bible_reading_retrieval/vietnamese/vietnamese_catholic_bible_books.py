import re
import unicodedata
from enum import StrEnum
from typing import Dict


class CatholicVietnameseBibleBook(StrEnum):
    # --- Old Testament (Cựu Ước - 46 Books) ---
    # Pentateuch (Ngũ Thư)
    GENESIS = "Sáng Thế"
    EXODUS = "Xuất Hành"
    LEVITICUS = "Lê-vi"
    NUMBERS = "Dân Số"
    DEUTERONOMY = "Đệ Nhị Luật"

    # Historical Books (Sách Lịch Sử)
    JOSHUA = "Giô-suê"
    JUDGES = "Thủ Lãnh"
    RUTH = "Rút"
    FIRST_SAMUEL = "1 Sa-mu-en"
    SECOND_SAMUEL = "2 Sa-mu-en"
    FIRST_KINGS = "1 Các Vua"
    SECOND_KINGS = "2 Các Vua"
    FIRST_CHRONICLES = "1 Sử Biên Niên"
    SECOND_CHRONICLES = "2 Sử Biên Niên"
    EZRA = "Ét-ra"
    NEHEMIAH = "Nơ-khe-mi-a"
    TOBIT = "Tô-bi-a"
    JUDITH = "Giu-đi-tha"
    ESTHER = "Ét-te"
    FIRST_MACCABEES = "1 Ma-ca-bê"
    SECOND_MACCABEES = "2 Ma-ca-bê"

    # Wisdom & Poetry (Sách Giáo Huấn)
    JOB = "Gióp"
    PSALMS = "Thánh Vịnh"
    PROVERBS = "Châm Ngôn"
    ECCLESIASTES = "Giảng Viên"
    SONG_OF_SONGS = "Diễm Ca"
    WISDOM = "Khôn Ngoan"
    SIRACH = "Huấn Ca"

    # Major Prophets (Ngôn Sứ Lớn)
    ISAIAH = "I-sai-a"
    JEREMIAH = "Giê-rê-mi-a"
    LAMENTATIONS = "Ai Ca"
    BARUCH = "Ba-rúc"
    EZEKIEL = "Ê-dê-ki-en"
    DANIEL = "Đa-ni-en"

    # Minor Prophets (Ngôn Sứ Nhỏ)
    HOSEA = "Hô-sê"
    JOEL = "Giô-en"
    AMOS = "A-mốt"
    OBADIAH = "Ô-va-đi-a"
    JONAH = "Giô-na"
    MICAH = "Mi-kha"
    NAHUM = "Na-khum"
    HABAKKUK = "Kha-ba-cúc"
    ZEPHANIAH = "Xô-phô-ni-a"
    HAGGAI = "Khác-gai"
    ZECHARIAH = "Da-ca-ri-a"
    MALACHI = "Ma-la-khi"

    # --- New Testament (Tân Ước - 27 Books) ---
    # Gospels & Acts (Tin Mừng & Công Vụ)
    MATTHEW = "Mát-thêu"
    MARK = "Mác-cô"
    LUKE = "Lu-ca"
    JOHN = "Gio-an"
    ACTS = "Công Vụ Tông Đồ"

    # Pauline Epistles & Hebrews (Thư Thánh Phao-lô & Híp-ri)
    ROMANS = "Rô-ma"
    FIRST_CORINTHIANS = "1 Cô-rinh-tô"
    SECOND_CORINTHIANS = "2 Cô-rinh-tô"
    GALATIANS = "Ga-lát"
    EPHESIANS = "Ê-phê-xô"
    PHILIPPIANS = "Phi-líp-phê"
    COLOSSIANS = "Cô-lô-xê"
    FIRST_THESSALONIANS = "1 Thê-xa-lô-ni-ca"
    SECOND_THESSALONIANS = "2 Thê-xa-lô-ni-ca"
    FIRST_TIMOTHY = "1 Ti-mô-thê"
    SECOND_TIMOTHY = "2 Ti-mô-thê"
    TITUS = "Ti-tô"
    PHILEMON = "Phi-lê-môn"
    HEBREWS = "Híp-ri"

    # Catholic Epistles & Revelation (Thư Công Giáo & Khải Huyền)
    JAMES = "Gia-cô-bê"
    FIRST_PETER = "1 Phê-rô"
    SECOND_PETER = "2 Phê-rô"
    FIRST_JOHN = "1 Gio-an"
    SECOND_JOHN = "2 Gio-an"
    THIRD_JOHN = "3 Gio-an"
    JUDE = "Giu-đa"
    REVELATION = "Khải Huyền"

    def _to_ascii_filename(self, text: str) -> str:
        """Convert a Vietnamese book name into an ASCII-safe filename stem (e.g. 'Sáng Thế' -> 'SangThe')."""
        replaced = text.replace("đ", "d").replace("Đ", "D")
        decomposed = unicodedata.normalize("NFD", replaced)
        ascii_only = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
        return re.sub(r"[^A-Za-z0-9]+", "", ascii_only)

    @property
    def json_filename(self) -> str:
        """Returns the local ASCII-safe JSON filename (e.g. 'SangThe.json', '2Timothe.json')."""
        return f"{self._to_ascii_filename(self.value)}.json"


# Mapping from ktcgkpv.org numeric `data-book-id` to canonical CatholicVietnameseBibleBook.
# Skips intro-only IDs on ktcgkpv.org (1, 7, 24, 32, 51, 52, 58, 81).
KTCG_BOOK_ID_TO_VIETNAMESE_BOOK: Dict[str, CatholicVietnameseBibleBook] = {
    "2": CatholicVietnameseBibleBook.GENESIS,
    "3": CatholicVietnameseBibleBook.EXODUS,
    "4": CatholicVietnameseBibleBook.LEVITICUS,
    "5": CatholicVietnameseBibleBook.NUMBERS,
    "6": CatholicVietnameseBibleBook.DEUTERONOMY,
    "8": CatholicVietnameseBibleBook.JOSHUA,
    "9": CatholicVietnameseBibleBook.JUDGES,
    "10": CatholicVietnameseBibleBook.RUTH,
    "11": CatholicVietnameseBibleBook.FIRST_SAMUEL,
    "12": CatholicVietnameseBibleBook.SECOND_SAMUEL,
    "13": CatholicVietnameseBibleBook.FIRST_KINGS,
    "14": CatholicVietnameseBibleBook.SECOND_KINGS,
    "15": CatholicVietnameseBibleBook.FIRST_CHRONICLES,
    "16": CatholicVietnameseBibleBook.SECOND_CHRONICLES,
    "17": CatholicVietnameseBibleBook.EZRA,
    "18": CatholicVietnameseBibleBook.NEHEMIAH,
    "19": CatholicVietnameseBibleBook.TOBIT,
    "20": CatholicVietnameseBibleBook.JUDITH,
    "21": CatholicVietnameseBibleBook.ESTHER,
    "22": CatholicVietnameseBibleBook.FIRST_MACCABEES,
    "23": CatholicVietnameseBibleBook.SECOND_MACCABEES,
    "25": CatholicVietnameseBibleBook.JOB,
    "26": CatholicVietnameseBibleBook.PSALMS,
    "27": CatholicVietnameseBibleBook.PROVERBS,
    "28": CatholicVietnameseBibleBook.ECCLESIASTES,
    "29": CatholicVietnameseBibleBook.SONG_OF_SONGS,
    "30": CatholicVietnameseBibleBook.WISDOM,
    "31": CatholicVietnameseBibleBook.SIRACH,
    "33": CatholicVietnameseBibleBook.ISAIAH,
    "34": CatholicVietnameseBibleBook.JEREMIAH,
    "35": CatholicVietnameseBibleBook.LAMENTATIONS,
    "36": CatholicVietnameseBibleBook.BARUCH,
    "37": CatholicVietnameseBibleBook.EZEKIEL,
    "38": CatholicVietnameseBibleBook.DANIEL,
    "39": CatholicVietnameseBibleBook.HOSEA,
    "40": CatholicVietnameseBibleBook.JOEL,
    "41": CatholicVietnameseBibleBook.AMOS,
    "42": CatholicVietnameseBibleBook.OBADIAH,
    "43": CatholicVietnameseBibleBook.JONAH,
    "44": CatholicVietnameseBibleBook.MICAH,
    "45": CatholicVietnameseBibleBook.NAHUM,
    "46": CatholicVietnameseBibleBook.HABAKKUK,
    "47": CatholicVietnameseBibleBook.ZEPHANIAH,
    "48": CatholicVietnameseBibleBook.HAGGAI,
    "49": CatholicVietnameseBibleBook.ZECHARIAH,
    "50": CatholicVietnameseBibleBook.MALACHI,
    "53": CatholicVietnameseBibleBook.MATTHEW,
    "54": CatholicVietnameseBibleBook.MARK,
    "55": CatholicVietnameseBibleBook.LUKE,
    "56": CatholicVietnameseBibleBook.JOHN,
    "57": CatholicVietnameseBibleBook.ACTS,
    "59": CatholicVietnameseBibleBook.ROMANS,
    "60": CatholicVietnameseBibleBook.FIRST_CORINTHIANS,
    "61": CatholicVietnameseBibleBook.SECOND_CORINTHIANS,
    "62": CatholicVietnameseBibleBook.GALATIANS,
    "63": CatholicVietnameseBibleBook.EPHESIANS,
    "64": CatholicVietnameseBibleBook.PHILIPPIANS,
    "65": CatholicVietnameseBibleBook.COLOSSIANS,
    "66": CatholicVietnameseBibleBook.FIRST_THESSALONIANS,
    "67": CatholicVietnameseBibleBook.SECOND_THESSALONIANS,
    "68": CatholicVietnameseBibleBook.FIRST_TIMOTHY,
    "69": CatholicVietnameseBibleBook.SECOND_TIMOTHY,
    "70": CatholicVietnameseBibleBook.TITUS,
    "71": CatholicVietnameseBibleBook.PHILEMON,
    "72": CatholicVietnameseBibleBook.HEBREWS,
    "73": CatholicVietnameseBibleBook.JAMES,
    "74": CatholicVietnameseBibleBook.FIRST_PETER,
    "75": CatholicVietnameseBibleBook.SECOND_PETER,
    "76": CatholicVietnameseBibleBook.FIRST_JOHN,
    "77": CatholicVietnameseBibleBook.SECOND_JOHN,
    "78": CatholicVietnameseBibleBook.THIRD_JOHN,
    "79": CatholicVietnameseBibleBook.JUDE,
    "80": CatholicVietnameseBibleBook.REVELATION,
}
