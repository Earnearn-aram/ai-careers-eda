"""Hand-entered observations: any CSV in data/manual/ whose header matches the Observation fields.

For figures a person reads in their own browser (gated or bot-protected pages, PDFs, JobsDB result counts).
Rules enforced by the schema: every row needs source_id (a row in data/sources.csv), retrieved_on, definition,
confidence, and `reported_via` forces confidence C. Template: data/manual/_template.csv.
"""
from __future__ import annotations

import csv
from pathlib import Path

from ..schema import Observation

NUMERIC = {"value": float, "sample_size": int}
BOOL = {"is_estimate"}


def load(folder: Path) -> list[Observation]:
    out = []
    for f in sorted(folder.glob("*.csv")):
        if f.name.startswith("_"):
            continue
        for i, r in enumerate(csv.DictReader(f.open()), start=2):
            row = {k: v for k, v in r.items() if v not in ("", None)}
            for k, fn in NUMERIC.items():
                if k in row:
                    row[k] = fn(row[k].replace(",", ""))
            for k in BOOL:
                if k in row:
                    row[k] = row[k].strip().lower() in ("1", "true", "yes")
            try:
                out.append(Observation(**row))
            except Exception as e:  # surface file and line so a contributor can fix the row
                raise ValueError(f"{f.name} line {i}: {e}") from e
    return out
