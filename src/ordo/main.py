import argparse
import json
import sys
from datetime import date
from typing import List, Optional, Tuple

from src.bible_reading_retrieval import english_bible_api, vietnamese_bible_api
from src.ordo.daily_catholic_reading_api import get_catholic_daily_reading_reference
from src.ordo.liturgical_calendar_api import LiturgicalCalendarAPIWrapper


def _parse_named_cli_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    today = date.today()
    parser = argparse.ArgumentParser(description="Fetch Catholic daily readings and liturgical calendar info.")
    parser.add_argument("-d", "--day", type=int, default=today.day, help="Day of the month (default: today)")
    parser.add_argument("-m", "--month", type=int, default=today.month, help="Month of the year (default: today)")
    parser.add_argument("-y", "--year", type=int, default=today.year, help="Four-digit year (default: today)")
    return parser.parse_args(argv)


def main(day: int, month: int, year: int) -> None:
    catholic_daily_reading_reference = get_catholic_daily_reading_reference(day=day, month=month, year=year)

    lit_cal_api = LiturgicalCalendarAPIWrapper(year=year)
    # catholic_yearly_ordo_liturgical_calendar_info = lit_cal_api.get_yearly_ordo_liturgical_calendar_info()
    catholic_daily_ordo_liturgical_calendar_info = lit_cal_api.get_daily_ordo_liturgical_calendar_info(
        day=day, month=month
    )

    celebrations_for_day = list(map(lambda entry: str(entry.get("name")), catholic_daily_ordo_liturgical_calendar_info))
    print()
    print(f"Today [Date: {date(year, month, day).strftime('%m/%d/%Y')}]: We celebrate {celebrations_for_day[0]}")
    if len(celebrations_for_day) > 1:
        bulleted_list = "\n- " + "\n- ".join(celebrations_for_day[1:])
        print(f"Additionally we also celebrate the following celebrations today: {bulleted_list}")
    print()

    english_bible_section_entries: List[Tuple[str, str]] = []
    vietnamese_bible_section_entries: List[Tuple[str, str]] = []
    for (
        lit_word_section,
        bible_passage_reference_english,
    ) in catholic_daily_reading_reference.readings.model_dump().items():
        english_bible_section_entry = english_bible_api.get_english_bible_section(
            lit_word_section, bible_passage_reference_english
        )
        if english_bible_section_entry[1] is not None:
            english_bible_section_entries.append(english_bible_section_entry)
        vietnamese_bible_section_entry = vietnamese_bible_api.get_vietnamese_bible_section(
            lit_word_section, bible_passage_reference_english
        )
        if vietnamese_bible_section_entry[1] is not None:
            vietnamese_bible_section_entries.append(vietnamese_bible_section_entry)

    print(json.dumps(english_bible_section_entries, indent=2, ensure_ascii=False))
    print(json.dumps(vietnamese_bible_section_entries, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("ARGS:", sys.argv)
    print(len(sys.argv))

    cli_args = _parse_named_cli_args()
    main(day=cli_args.day, month=cli_args.month, year=cli_args.year)
