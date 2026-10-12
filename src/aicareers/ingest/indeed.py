"""Indeed Hiring Lab AI Tracker -> monthly mean of the 7-day-trailing daily share.

Metric: share of job postings whose text includes AI keywords (e.g. "Machine Learning",
"Data Science", "Artificial Intelligence"). NOT comparable with Lightcast's "requires an AI skill".
Monthly values are the arithmetic mean of daily values; this is our aggregation, noted per row.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

from ..schema import Confidence, Observation

SOURCE_ID = "indeed_ai_tracker"
DEFINITION = (
    "Share of job postings in the country containing AI keywords (7-day trailing average, "
    "keyword match on posting text). Monthly = mean of daily values (our aggregation)."
)
START = "2023-10"


def load(raw_dir: Path) -> list[Observation]:
    retrieved = date.fromisoformat((raw_dir / "RETRIEVED_ON").read_text().strip())
    acc: dict[tuple[str, str], list[float]] = defaultdict(list)
    with (raw_dir / "AI_posting.csv").open() as f:
        for r in csv.DictReader(f):
            month = r["date"][:7]
            if month >= START and r["AI_share_postings"]:
                acc[(r["jobcountry"], month)].append(float(r["AI_share_postings"]))
    out = []
    for (cc, month), vals in sorted(acc.items()):
        out.append(
            Observation(
                id=f"indeed-ai-{cc}-{month}",
                metric="ai_keyword_share",
                region=cc,
                period=month,
                value=round(sum(vals) / len(vals), 4),
                unit="%",
                source_id=SOURCE_ID,
                retrieved_on=retrieved,
                definition=DEFINITION,
                confidence=Confidence.A,
                notes=f"mean of {len(vals)} daily values",
            )
        )
    return out
