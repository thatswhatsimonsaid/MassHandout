"""
Shared test fixtures — extracts all functions from MassHandout.ipynb
so they can be imported and tested without running main().
"""
import json
import pytest
import asyncio

import os
NOTEBOOK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "MassHandout.ipynb")


def _load_notebook_source(path):
    """Read a .ipynb file and concatenate all code cell sources, skipping the
    final `await main()` line so nothing executes on import."""
    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    source_lines = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        for line in cell.get("source", []):
            stripped = line.strip()
            if stripped.startswith("await main()"):
                continue
            source_lines.append(line)

    return "\n".join(source_lines)


@pytest.fixture(scope="session")
def nb_module():
    """Executes the notebook source in a namespace and returns it as a
    module-like dict of functions."""
    source = _load_notebook_source(NOTEBOOK_PATH)
    ns = {}
    exec(source, ns)
    return ns


@pytest.fixture
def run_async():
    """Helper to run async functions in sync test code."""
    def _run(coro):
        return asyncio.get_event_loop().run_until_complete(coro)
    return _run


# ── Known-date expectations (verified from USCCB) ──────────────────────────
# Each entry: date_str -> expected citations for all 5 sections.
# `None` means there is no Reading 2 on that day (weekday).

KNOWN_DATES = {
    "080726": {  # Fri Aug 7, 2026 — 18th Week in Ordinary Time
        "feast_day_contains": "Eighteenth",
        "citations": {
            "reading1": None,   # Nahum — citation may vary in scrape
            "psalm": "Deuteronomy 32:35cd-36ab, 39abcd, 41",
            "reading2": None,
            "alleluia": "Matthew 5:10",
            "gospel": "Matthew 16:24-28",
        },
    },
    "083026": {  # Sun Aug 30, 2026 — 22nd Sunday in Ordinary Time
        "feast_day_contains": "Twenty",
        "citations": {
            "reading1": "Jeremiah 20:7-9",
            "psalm": "Psalm 63:2, 3-4, 5-6, 8-9",
            "reading2": "Romans 12:1-2",
            "alleluia": "cf. Ephesians 1:17-18",
            "gospel": "Matthew 16:21-27",
        },
    },
    "122526": {  # Fri Dec 25, 2026 — Christmas (Solemnity)
        "feast_day_contains": "Nativity",
        "citations": {
            "reading1": None,   # Christmas has multiple Mass options; citation varies
            "psalm": None,
            "reading2": None,
            "alleluia": None,
            "gospel": None,
        },
    },
    "122426": {  # Thu Dec 24, 2026 — Fourth Week of Advent (Christmas Vigil is evening)
        "feast_day_contains": "Advent",
        "citations": {
            "reading1": None,
            "psalm": None,
            "reading2": None,
            "alleluia": None,
            "gospel": None,
        },
    },
    "112226": {  # Sun Nov 22, 2026 — Christ the King / 34th Sunday
        "feast_day_contains": "Christ",
        "citations": {
            "reading1": None,
            "psalm": None,
            "reading2": None,
            "alleluia": None,
            "gospel": None,
        },
    },
}

# ThanhLinh URL anchor: Aug 8, 2026 = ID 587
THANHLINH_ANCHOR = {
    "anchor_date": "2026-08-08",
    "anchor_id": 587,
}

# Expected ThanhLinh IDs for test dates
EXPECTED_THANHLINH_IDS = {
    "080726": 586,   # Aug 7  → -1 day  → 587 - 1
    "080826": 587,   # Aug 8  →  0 days  → 587
    "080926": 588,   # Aug 9  → +1 day   → 587 + 1
    "083026": 609,   # Aug 30 → +22 days → 587 + 22
    "122526": 726,   # Dec 25 → +139 days → 587 + 139
    "122426": 725,   # Dec 24 → +138 days → 587 + 138
    "112226": 703,   # Nov 22 → +116 days → 587 + 116  (106 days from Aug 8 to Nov 22... let me recalc)
    # Aug 8 → Nov 22: Aug(23 left) + Sep(30) + Oct(31) + Nov(22) = 23+30+31+22 = 106 → 587+106 = 693
}

# Recalculate Nov 22 properly
from datetime import datetime as _dt
_delta = (_dt(2026, 11, 22) - _dt(2026, 8, 8)).days
EXPECTED_THANHLINH_IDS["112226"] = 587 + _delta
