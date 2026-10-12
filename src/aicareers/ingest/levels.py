"""Levels.fyi markdown summaries (the agent-friendly .md routes named in their robots.txt / llms.txt).

Self-reported, verified-in-tiers, skewed to tech. Attribution required: "Data source: Levels.fyi".
Raw .md files are NOT committed (their Data License governs redistribution). `extract` turns a local
folder of downloaded .md files into data/processed/levels_extract.csv; `load` reads that CSV.
"""
from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path

from ..schema import Confidence, Observation

SOURCE_ID = "levels_fyi"
FIELDS = ["page_url", "role", "region", "region_basis", "currency", "median", "p25", "p75", "p90", "n", "last_updated", "generated", "retrieved_on"]
REGION = {"United States": "US", "Thailand": "TH", "Singapore": "SG", "Germany": "DE"}
ROLE = {"AI Engineer": "AI / LLM Engineer", "Machine Learning Engineer": "Machine Learning Engineer", "Data Scientist": "Data Scientist",
        "Data Engineer": "Data Engineer", "Data Analyst": "Data Analyst / BI", "Software Engineer": "Software Engineer (context)"}
DEF = "Median total compensation (base + annualised stock + bonus), self-reported to Levels.fyi, annual."


def _num(s: str) -> float:
    return float(re.sub(r"[^\d.]", "", s))


def parse(text: str) -> dict | None:
    g = lambda pat: (m.group(1) if (m := re.search(pat, text)) else None)
    median = g(r"Median Total Compensation:\s*([^\n]+?)\s*(?:\n|$)")
    if not median:
        return None
    p = re.search(r"25th / 75th Percentile:\s*(.+?)\s*/\s*(.+?)\s*\n", text)
    title = g(r"^# Levels\.fyi – (.+?) Salary") or ""
    role, _, region = title.partition(" in ")
    return {
        "page_url": g(r"\*\*URL:\*\*\s*(\S+)"), "role": role.strip(),
        "region": (region or g(r"\*\*Location:\*\*\s*([^\n]+?)\s*\n") or "").strip(),
        "currency": g(r"\*\*Currency:\*\*\s*(\w+|\S+ \(\S+\))")[:3] if g(r"\*\*Currency:\*\*\s*(\S+)") and g(r"\*\*Currency:\*\*\s*(\S+)") != "USD" else "USD",
        "median": _num(median), "p25": _num(p.group(1)) if p else "", "p75": _num(p.group(2)) if p else "",
        "p90": _num(g(r"90th Percentile:\s*([^\n]+)") or "") if g(r"90th Percentile:\s*([^\n]+)") else "",
        "n": int(_num(g(r"Sample Size:\s*([\d,]+)"))), "last_updated": g(r"Last Updated:\s*([^\n]+?)\s*\n"),
        "generated": g(r"\*\*Generated:\*\*\s*(\S+)"),
    }


SLUG = {"united-states": "United States", "thailand": "Thailand", "singapore": "Singapore", "germany": "Germany"}


def extract(raw_md_dir: Path, out_csv: Path, retrieved_on: str) -> int:
    """Files are named <path with / -> _>.md. Title+country pages carry a wrong header (Location says
    United States, URL is the generic one) but country-specific figures, so the region comes from the
    requested URL and the row is marked region_basis=request_url."""
    rows, seen = [], set()
    for f in sorted(raw_md_dir.glob("*.md")):
        if f.stat().st_size == 0:
            continue
        r = parse(f.read_text())
        if not r:
            continue
        req = SLUG.get(f.stem.split("_locations_")[1]) if "_locations_" in f.stem else None
        r["region_basis"] = "page"
        if req and req != r["region"]:
            if r["region"] == "United States" and "Salary in" not in f.read_text().split("\n")[0]:
                r["region"], r["region_basis"] = req, "request_url"
        key = (r["role"], r["region"], r["currency"], r["median"], r["n"])
        if key in seen:
            continue
        seen.add(key)
        r["retrieved_on"] = retrieved_on
        rows.append(r)
    with out_csv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)
    return len(rows)


def load(csv_path: Path) -> list[Observation]:
    out = []
    for r in csv.DictReader(csv_path.open()):
        reg = REGION.get(r["region"])
        role = ROLE.get(r["role"])
        if not reg or not role:
            continue
        n = int(r["n"])
        lu = r["last_updated"]
        for metric, key, d in [("salary_median_total", "median", DEF), ("salary_p25_total", "p25", "25th percentile total compensation, self-reported to Levels.fyi, annual."),
                               ("salary_p75_total", "p75", "75th percentile total compensation, self-reported to Levels.fyi, annual."),
                               ("salary_p90_total", "p90", "90th percentile total compensation, self-reported to Levels.fyi, annual.")]:
            if r[key] == "":
                continue
            out.append(Observation(
                id=f"levels-{re.sub(r'[^a-z]+', '', role.lower())[:14]}-{reg}-{metric.split('_')[1]}", metric=metric, role=role, region=reg, period="2026",
                value=float(r[key]), unit=r["currency"], source_id=SOURCE_ID, retrieved_on=date.fromisoformat(r["retrieved_on"]), definition=d,
                confidence=Confidence.B if r["region_basis"] == "page" else Confidence.C, sample_size=n,
                notes=f"Page last updated {lu}. Page: {r['page_url']}. Data source: Levels.fyi (https://www.levels.fyi)."
                + ("" if r["region_basis"] == "page" else " Region taken from the requested URL: the page header says Location: United States with a generic URL, though the figures are country-specific.")))
    return out
