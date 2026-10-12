"""Processed data -> site/data/*.json (and data/processed/*.csv)."""
from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

from . import fx, pages
from .ingest import indeed, levels, manual, owid, seed, verified
from .schema import Observation, Source

ROOT = Path(__file__).resolve().parents[2]


def load_sources(path: Path = ROOT / "data" / "sources.csv") -> list[Source]:
    with path.open() as f:
        return [Source(**{k: (v or None) if k == "retrieved_on" else v for k, v in r.items()}) for r in csv.DictReader(f)]


def collect() -> list[Observation]:
    raw = ROOT / "data" / "raw"
    return (indeed.load(raw / "indeed_ai_tracker")
            + owid.load(raw / "owid" / "share-ai-job-postings.csv", date(2026, 10, 12))
            + verified.load()
            + levels.load(ROOT / "data" / "processed" / "levels_extract.csv")
            + manual.load(ROOT / "data" / "manual")
            + seed.load())


def main() -> None:
    sources = load_sources()
    obs = collect()
    ids = {s.id for s in sources}
    missing = {o.source_id for o in obs} - ids
    if missing:
        raise SystemExit(f"observations reference unknown sources: {sorted(missing)}")
    if len({o.id for o in obs}) != len(obs):
        raise SystemExit("duplicate observation ids")

    out = ROOT / "site" / "data"
    out.mkdir(parents=True, exist_ok=True)
    (out / "observations.json").write_text(json.dumps([json.loads(o.model_dump_json()) for o in obs], indent=1))
    (out / "sources.json").write_text(json.dumps([json.loads(s.model_dump_json()) for s in sources], indent=1))

    rates = fx.from_ecb_xml(ROOT / "data" / "raw" / "ecb" / "eurofxref-daily.xml")
    (out / "fx.json").write_text(json.dumps({c: json.loads(r.model_dump_json()) for c, r in rates.items()}, indent=1))

    proc = ROOT / "data" / "processed"
    with (proc / "observations.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(Observation.model_fields))
        w.writeheader()
        for o in obs:
            w.writerow(json.loads(o.model_dump_json()))
    pages.write_all(obs, ROOT / "site")
    print(f"{len(obs)} observations, {len(sources)} sources")


if __name__ == "__main__":
    main()
