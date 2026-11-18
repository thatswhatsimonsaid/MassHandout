import json
from datetime import date
from typing import Any, Dict, List, Optional

import requests


# GitHub Repository (External Dependency): https://github.com/Liturgical-Calendar/LiturgicalCalendarAPI
# OpenAPI Specification: https://litcal.johnromanodorazio.com/dist/
# Frontend Website (for Testing): https://litcal.johnromanodorazio.com/
class LiturgicalCalendarAPIWrapper:
    __year: int

    def __init__(self, year: int):
        self.__year = year

    def get_year(self) -> int:
        return self.__year

    def get_yearly_ordo_liturgical_calendar_info(self, year: Optional[int] = None) -> Dict[str, Any]:
        requested_year = self.__year
        if year is not None:  # 'year' override provided
            requested_year = year
        print("Requested Year:", requested_year)

        req_headers = {"accept": "application/json", "Accept-Language": "en-US"}
        LIT_CAL_URL = f"https://litcal.johnromanodorazio.com:443/api/v5/calendar/{requested_year}?year_type=CIVIL"
        res = requests.get(LIT_CAL_URL, headers=req_headers, timeout=10)
        print("STATUS-CODE:", res.status_code)
        lit_cal_all_data = dict(res.json())
        print(lit_cal_all_data.keys())  # Expected: dict_keys(['litcal', 'settings', 'metadata', 'messages'])

        litcal_yearly_info = lit_cal_all_data["litcal"]
        print(f"Total Liturgical-Calendar Entries (for Calendar Year {year}):", len(litcal_yearly_info))
        # print(json.dumps(litcal_yearly_info, indent=2))
        return litcal_yearly_info

    def _filter_litcal_entries_by_date(
        self, litcal_yearly_info: List[Dict[str, Any]], day: int, month: int, year: int
    ) -> List[Dict[str, Any]]:
        return [
            entry
            for entry in litcal_yearly_info
            if entry.get("month") == month and entry.get("day") == day and entry.get("year") == year
        ]

    def _is_valid_date(self, year: int, day: int, month: int) -> bool:
        try:
            date(year, month, day)
            return True
        except ValueError:
            return False

    def get_daily_ordo_liturgical_calendar_info(self, day: int, month: int) -> List[Dict[str, Any]]:
        self._is_valid_date(self.__year, day, month)

        litcal_yearly_info = self.get_yearly_ordo_liturgical_calendar_info(self.__year)

        litcal_daily_info = self._filter_litcal_entries_by_date(litcal_yearly_info, day, month, self.__year)
        print(json.dumps(litcal_daily_info, indent=2))
        print(f"Valid Liturgical-Calendar Entries (for {month}-{day}-{self.__year}):", len(litcal_daily_info))

        return litcal_daily_info
