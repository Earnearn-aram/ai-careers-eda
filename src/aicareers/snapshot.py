"""Append one manually observed JobsDB result count (exact query + date) to the snapshot log.

No scraping: read the count off the public search page yourself, then log it here so repeated
like-for-like readings accumulate into a series.
usage: aicareers-log-snapshot "AI Engineer" 262 --site "th.jobsdb.com" [--date 2026-10-12]
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "thailand_jobsdb_snapshots.csv"


def main() -> None:
    a = argparse.ArgumentParser()
    a.add_argument("query"); a.add_argument("count", type=int)
    a.add_argument("--site", default="th.jobsdb.com"); a.add_argument("--date", default=date.today().isoformat())
    a.add_argument("--notes", default="")
    n = a.parse_args()
    new = not PATH.exists() or PATH.stat().st_size == 0
    with PATH.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["captured_on", "query_exact", "site", "result_count", "recorded_by", "notes"])
        w.writerow([n.date, n.query, n.site, n.count, "manual", n.notes])


if __name__ == "__main__":
    main()
