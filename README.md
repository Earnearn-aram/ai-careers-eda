# ai-careers-eda

An exploratory, neutral, source-traceable look at how AI-related careers changed from late 2023 to Oct 2026, comparing Thailand with the US, Europe and Singapore/APAC. No hypothesis; the aim is to show what each source says, including where sources disagree and where data is missing.

## Status (12 Oct 2026)

| Piece | State |
|---|---|
| Schema, build, tests (16), static site | Working |
| Indeed AI Tracker (9 countries, no TH/SG) | Fetched from primary, confidence A |
| Lightcast AI-skill share, 22 economies, 2023-2025 (Thailand not covered) | Via Our World in Data CSV of AI Index 2026; spot-checked against the report PDF; confidence B |
| US skill counts (RAG, agents, ...), 2024 vs 2025 | From the AI Index 2026 PDF; confidence A |
| Entry level (Stanford DEL, ADP payroll, US only) | From the Aug 2026 paper; confidence B |
| Pay: Levels.fyi, US/DE/SG roles, Thailand generic Software Engineer | `.md` routes; confidence B (C where region was inferred, see overview) |
| FX | ECB reference rates dated 2026-10-09 |
| Indeed Hiring Lab articles (6 read: seniority, AI-titled roles, software postings, advertised pay; US, Europe for titles only) | Fetched from `hiringlab.indeed.com` (crawl-delay respected); confidence A |
| Not reachable | BLS (403), JobsDB (403), Wayback |
| Thai role-level pay and demand | Unverified seed values only (confidence C); JobsDB snapshot log is empty |
| Role pages | Pay where data exists; other lenses state "no data collected" |

Raw files from third parties are not committed; `data/raw/MANIFEST.csv` lists URL, date and sha256, and `scripts/fetch_raw.sh` re-fetches and compares.

## Use

```
uv sync
uv run pytest            # schema, no-orphan-source, no-mixed-metric, neutral-wording checks
uv run aicareers-build   # writes site/data/*.json, data/processed/*.csv, site/*.html
python -m http.server -d site   # view; add ?c=1 to include confidence C
```

## How to read it

Every number is an `Observation` (`src/aicareers/schema.py`) with source, retrieval date, definition, confidence (A primary and documented; B primary but self-reported or small sample; C secondary or unverified) and estimate flag. Metrics with different definitions are never plotted together. Gaps stay gaps. Pay is never reduced to "the salary".

## Limits

Self-reporting and survivorship bias, big-tech skew in pay, title ambiguity, duplicate postings and ghost jobs, keyword match is not skill requirement, US-centric entry-level evidence, thin Thai data. Charts use dependency-free SVG; no tracking or third-party requests.

## Contributing

Open an issue with the figure, primary URL, retrieval date and exact definition. Scraping that breaks site terms is out of scope; use published pages, CSVs and APIs.

Indeed data: Indeed Hiring Lab, CC BY 4.0. Code: MIT.

## Publishing

Copy `docs/pages.yml.example` to `.github/workflows/pages.yml` (needs a token with workflow scope), then enable GitHub Pages with source “GitHub Actions”.
