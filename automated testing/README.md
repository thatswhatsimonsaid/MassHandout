# Automated Testing — MassHandout

Automated test suite for the Mass Handout generator notebook. Verifies URL generation, text parsing, scraping, and Word document output.

## Prerequisites

```bash
pip install pytest playwright beautifulsoup4 requests python-docx jupyter
python -m playwright install chromium
```

## Running Tests

### Unit tests only (fast, no network)

```bash
cd automated testing
pytest test_unit.py -v
```

### Integration tests (requires network + Playwright)

```bash
cd automated testing
pytest test_integration.py -v -s
```

### Run all tests

```bash
cd automated testing
pytest -v -s
```

### Skip slow integration tests

```bash
cd automated testing
pytest test_unit.py -v
pytest -v -s -k "not integration"
```

## Test Coverage

### `test_unit.py` — No network required

| Test Class | What it covers |
|---|---|
| `TestThanhLinhURL` | Dynamic URL formula for past, anchor, and future dates |
| `TestUSCCBUrl` | USCCB URL construction pattern |
| `TestCitationDetection` | `_looks_like_citation` with biblical citations and non-citations |
| `TestParseReading` | Citation/body separation, liturgical intro/outro stripping (EN + VI) |
| `TestParseAlleluia` | Alleluia frame stripping, citation extraction |
| `TestParseUSCCBPsalm` | English psalm: citation, response, numbered verses |
| `TestParseThanhLinhPsalm` | Vietnamese psalm: citation, response, numbered verses |
| `TestPrepareTemplateData` | Data assembly: structure, missing Reading 2, Vietnamese language selection |

### `test_integration.py` — Requires network + Playwright

| Test Class | What it covers |
|---|---|
| `TestUSCCBScraping` | USCCB returns all 5 sections, has Reading 1 + Gospel, non-default feast day |
| `TestThanhLinhScraping` | ThanhLinh returns sections with Reading 1 + Gospel |
| `TestKnownDateCitations` | Exact citation verification for Aug 7 & Aug 30, 2026 |
| `TestWordDocumentGeneration` | Page size, margins, columns, feast day, org, event, date, readings, hymns, Anima Christi, citations |
| `TestFutureDates` | Full pipeline for Dec 24, Dec 25, Nov 22, 2026 |

## Test Dates

| Date | Liturgical Day | Notes |
|---|---|---|
| `080726` (Aug 7) | Friday, 18th Week in Ordinary Time | Past date, weekday (no Reading 2) |
| `083026` (Aug 30) | 22nd Sunday in Ordinary Time | Past date, Sunday (full readings) |
| `112226` (Nov 22) | Christ the King | Future date |
| `122426` (Dec 24) | Christmas Eve (Vigil) | Future date |
| `122526` (Dec 25) | Christmas (Nativity of the Lord) | Future date, solemnity |

## Notes

- Integration tests hit live websites (USCCB + ThanhLinh) and may take 30-60 seconds per date.
- ThanhLinh URL IDs are computed from an anchor: **Aug 8, 2026 = ID 587**. If the anchor changes, update `conftest.py`.
- The notebook is loaded dynamically (not imported as a module), so `await main()` is skipped during test execution.
