# ai-careers-eda

An exploratory, neutral, source-traceable look at how AI-related careers changed from late 2023 to Oct 2026. The report is global-first (US and Europe, with Singapore and Hong Kong as APAC context). Thailand has its own limited-evidence page, because the usable Thai data is thin. No hypothesis; the aim is to show what each source says, including where sources disagree and where data is missing.

## Status (12 Oct 2026)

| Piece | State |
|---|---|
| Schema, build, tests (21), static site | Working |
| Indeed AI Tracker (9 countries, no TH/SG) | Fetched from primary, confidence A |
| Lightcast AI-skill share, 22 economies, 2023-2025 (Thailand not covered) | Via Our World in Data CSV of AI Index 2026; spot-checked against the report PDF; confidence B |
| US skill counts (RAG, agents, ...), 2024 vs 2025 | From the AI Index 2026 PDF; confidence A |
| Entry level (Stanford DEL, ADP payroll, US only) | From the Aug 2026 paper; confidence B |
| Pay: Levels.fyi, US/DE/SG roles, Thailand generic Software Engineer | `.md` routes; confidence B (C where region was inferred, see overview) |
| FX | ECB reference rates dated 2026-10-09 |
| Indeed Hiring Lab articles (6 read: seniority, AI-titled roles, software postings, advertised pay; US, Europe for titles only) | Fetched from `hiringlab.indeed.com` (crawl-delay respected); confidence A |
| Not reachable | BLS (403), JobsDB (403), Wayback |
| Thailand | Robert Walters salary-calculator ranges for AI and app-development roles in Bangkok, 2025 and 2026 (AI ranges unchanged), plus survey headlines; page limited to what exists: Levels.fyi generic Software Engineer pay, Michael Page 2026 top-10 page, Robert Walters hiring guides (recruiter statements, increment ranges). Role-level Thai pay and demand are unverified (confidence C). Both recruiters' salary surveys are form-gated; most other Thai hosts are blocked; JobsDB returns 403. JobsDB log is empty |
| Role pages | Built from the evidence held: pay and, for data roles, the AI-mention share; skills for AI/ML roles (all US AI postings, not role-specific). Roles with no data (MLOps pay, AI research, AI PM, forward deployed) say so |
| QA | See [docs/QA_CHECKLIST.md](docs/QA_CHECKLIST.md) (Wayback archiving not done; second framing pass should be repeated by a human) |

Raw files from third parties are not committed; `data/raw/MANIFEST.csv` lists URL, date and sha256, and `scripts/fetch_raw.sh` re-fetches and compares.

## Adding Thai (or any) figures by hand

See [docs/THAILAND_COLLECTION.md](docs/THAILAND_COLLECTION.md): which sources to read in a browser, what to record, and how to add rows to `data/manual/*.csv` (validated at build; a bad row fails with file and line).

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

## Licences

The site has a licences-and-attribution section (Indeed AI Tracker CC BY 4.0, AI Index report CC BY-ND 4.0, Levels.fyi Data License, Robert Walters and Michael Page all rights reserved). This project republishes individual figures with sources, not datasets or pages. It is not legal advice; check the terms before wider publication.
