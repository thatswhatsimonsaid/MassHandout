from enum import StrEnum


class CatholicEnglishBibleBook(StrEnum):
    # --- Old Testament (46 Books) ---
    # Pentateuch
    GENESIS = "Genesis"
    EXODUS = "Exodus"
    LEVITICUS = "Leviticus"
    NUMBERS = "Numbers"
    DEUTERONOMY = "Deuteronomy"

    # Historical Books
    JOSHUA = "Joshua"
    JUDGES = "Judges"
    RUTH = "Ruth"
    FIRST_SAMUEL = "1 Samuel"
    SECOND_SAMUEL = "2 Samuel"
    FIRST_KINGS = "1 Kings"
    SECOND_KINGS = "2 Kings"
    FIRST_CHRONICLES = "1 Chronicles"
    SECOND_CHRONICLES = "2 Chronicles"
    EZRA = "Ezra"
    NEHEMIAH = "Nehemiah"
    TOBIT = "Tobit"
    JUDITH = "Judith"
    ESTHER = "Esther"
    FIRST_MACCABEES = "1 Maccabees"
    SECOND_MACCABEES = "2 Maccabees"

    # Wisdom & Poetry
    JOB = "Job"
    PSALMS = "Psalms"
    PROVERBS = "Proverbs"
    ECCLESIASTES = "Ecclesiastes"
    SONG_OF_SONGS = "Song of Songs"
    WISDOM = "Wisdom"
    SIRACH = "Sirach"

    # Major Prophets
    ISAIAH = "Isaiah"
    JEREMIAH = "Jeremiah"
    LAMENTATIONS = "Lamentations"
    BARUCH = "Baruch"
    EZEKIEL = "Ezekiel"
    DANIEL = "Daniel"

    # Minor Prophets
    HOSEA = "Hosea"
    JOEL = "Joel"
    AMOS = "Amos"
    OBADIAH = "Obadiah"
    JONAH = "Jonah"
    MICAH = "Micah"
    NAHUM = "Nahum"
    HABAKKUK = "Habakkuk"
    ZEPHANIAH = "Zephaniah"
    HAGGAI = "Haggai"
    ZECHARIAH = "Zechariah"
    MALACHI = "Malachi"

    # --- New Testament (27 Books) ---
    # Gospels & Acts
    MATTHEW = "Matthew"
    MARK = "Mark"
    LUKE = "Luke"
    JOHN = "John"
    ACTS = "Acts"

    # Pauline Epistles & Hebrews
    ROMANS = "Romans"
    FIRST_CORINTHIANS = "1 Corinthians"
    SECOND_CORINTHIANS = "2 Corinthians"
    GALATIANS = "Galatians"
    EPHESIANS = "Ephesians"
    PHILIPPIANS = "Philippians"
    COLOSSIANS = "Colossians"
    FIRST_THESSALONIANS = "1 Thessalonians"
    SECOND_THESSALONIANS = "2 Thessalonians"
    FIRST_TIMOTHY = "1 Timothy"
    SECOND_TIMOTHY = "2 Timothy"
    TITUS = "Titus"
    PHILEMON = "Philemon"
    HEBREWS = "Hebrews"

    # Catholic Epistles & Revelation
    JAMES = "James"
    FIRST_PETER = "1 Peter"
    SECOND_PETER = "2 Peter"
    FIRST_JOHN = "1 John"
    SECOND_JOHN = "2 John"
    THIRD_JOHN = "3 John"
    JUDE = "Jude"
    REVELATION = "Revelation"

    @property
    def json_filename(self) -> str:
        """Returns the local JSON filename (e.g. '2Timothy.json', 'SongofSongs.json')."""
        return f"{self.value.replace(' ', '')}.json"


NABRE_BOOK_ALIASES = {
    "Psalm": CatholicEnglishBibleBook.PSALMS.value,
    "Song of Solomon": CatholicEnglishBibleBook.SONG_OF_SONGS.value,
    "Ecclesiasticus": CatholicEnglishBibleBook.SIRACH.value,
    "Wisdom of Solomon": CatholicEnglishBibleBook.WISDOM.value,
}


def normalize_english_book_name(book_name: str) -> str:
    cleaned = book_name.strip()
    return NABRE_BOOK_ALIASES.get(cleaned, cleaned)
