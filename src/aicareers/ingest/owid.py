"""Lightcast share of job postings with at least one AI skill, per economy and year.

Republished by Our World in Data (CC BY) from the Stanford AI Index 2026 (Lightcast data), last updated
2026-04-20 per OWID metadata. Spot-checked against the AI Index 2026 PDF, Figure 4.4.2 (11 economies,
2025) and Lightcast's blog (US, SG, HK, LU, ES). The skill list is revised every edition, so values
are only comparable within the 2026 edition; do not splice in figures from the 2024/2025 editions.
"""
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from ..schema import Confidence, Observation

SOURCE_ID = "owid_lightcast_ai_index_2026"
CODE = {"Australia": "AU", "Austria": "AT", "Belgium": "BE", "Canada": "CA", "Chile": "CL", "Croatia": "HR", "France": "FR", "Germany": "DE",
        "Hong Kong": "HK", "Italy": "IT", "Luxembourg": "LU", "Mexico": "MX", "Netherlands": "NL", "New Zealand": "NZ", "Poland": "PL",
        "Singapore": "SG", "Spain": "ES", "Sweden": "SE", "Switzerland": "CH", "United Arab Emirates": "AE", "United Kingdom": "GB", "United States": "US"}
DEF = ("Share of job postings that include at least one AI skill (Lightcast skill list of 300+ skills in 10 clusters, matched in posting text; "
       "list revised each edition). AI Index 2026 edition. Lightcast metric, not comparable with Indeed keyword share.")


def load(csv_path: Path, retrieved_on: date) -> list[Observation]:
    out = []
    for r in csv.DictReader(csv_path.open()):
        yr = int(r["year"])
        if yr < 2023:
            continue
        cc = CODE[r["entity"]]
        out.append(Observation(
            id=f"lc26-{cc}-{yr}", metric="ai_skill_share", region=cc, period=str(yr), value=round(float(r["ai_job_postings_share"]), 4), unit="%",
            source_id=SOURCE_ID, retrieved_on=retrieved_on, definition=DEF, confidence=Confidence.B,
            notes="Via Our World in Data CSV of Lightcast / AI Index 2026; spot-checked against the report PDF."))
    return out
