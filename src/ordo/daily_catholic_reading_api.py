from pydantic import BaseModel
from datetime import date
from typing import Optional

import requests


class CatholicReadingsAPIReadingVerseReference(BaseModel):
    firstReading: str
    psalm: str
    secondReading: Optional[str] = None
    # NOTE: gospelAcclamation (Not included)
    gospel: str


class CatholicReadingsAPIContents(BaseModel):
    date: date
    monthDay: str
    season: str
    readings: CatholicReadingsAPIReadingVerseReference
    usccbLink: str
    apiEndpoint: str


# GitHub Repository (External Dependency) https://github.com/cpbjr/catholic-readings-api
def get_catholic_daily_reading_reference(day: int, month: int, year: int) -> CatholicReadingsAPIContents:
    CATHOLIC_READING_URL = f"https://cpbjr.github.io/catholic-readings-api/readings/{year}/{month:02d}-{day:02d}.json"
    res = requests.get(CATHOLIC_READING_URL)

    catholic_readings_api_daily_res = CatholicReadingsAPIContents.model_validate(res.json())
    print(catholic_readings_api_daily_res.model_dump_json(indent=2))
    print(type(catholic_readings_api_daily_res))

    # for key, value in catholic_readings_api_daily_res.readings

    return catholic_readings_api_daily_res
