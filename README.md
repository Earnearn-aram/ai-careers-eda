# ai-careers-eda

An exploratory, neutral, source-traceable look at how AI-related careers changed from late 2023 to Oct 2026, comparing Thailand with the US, Europe and Singapore/APAC. No hypothesis; the aim is to show what each source says, including where sources disagree and where data is missing.

## Status (12 Oct 2026)

| Piece | State |
|---|---|
| Schema, build, tests, static site | Working |
| Indeed AI Tracker (9 countries, no TH/SG) | Fetched from primary, confidence A |
| Lightcast / AI Index, Levels.fyi, recruiter guides, Stanford DEL, Indeed articles | **Not fetched.** Their hosts were unreachable from the build environment. Seed figures from PLAN.md are loaded as confidence C and hidden by default |
| Seed claims re-checked against the Indeed CSV | Two did not match (US peak, UK/Europe Q1 2026); see the Verification log on the overview page |
| FX conversion | No rate retrieved, so no USD conversion |
| Thailand series | None. JobsDB snapshot log is empty; start it with `aicareers-log-snapshot` |
| Role pages | Structure only; most lenses state "no data collected" |

Next: re-run fetching from an environment with open network access and replace each C-grade seed row with a primary-page value (record `n` and last-updated for Levels.fyi).

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
