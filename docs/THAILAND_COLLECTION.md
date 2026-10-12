# Collecting Thai evidence by hand

The build environment cannot reach Thai recruiter, government or job-board sites (all blocked or 403), and some
sources are gated behind a free request form. Everything below can be read in a normal browser. Nothing here needs
scraping.

## How to add a figure
1. Add one row to `data/sources.csv` for the source (id, name, URL, `retrieved_on`, tier, status `fetched`).
2. Add one row per figure to a CSV in `data/manual/` (copy the header from `data/manual/_template.csv`).
   Required: `id` (unique), `metric`, `region` (TH), `period`, `value`, `unit`, `source_id`, `retrieved_on`,
   `definition` (what exactly was measured, copied from the source), `confidence`.
   - Use `confidence` A/B only if you read the primary page or PDF yourself; put the page or table number in `notes`.
   - Put the sample size in `sample_size` when the source gives it. Under 30 is flagged on the site.
   - Put range ends in two rows with metric `salary_range_bound` and say "low end" / "high end" in `definition`.
3. `uv run aicareers-build && uv run pytest`. A row with a missing source or a bad field fails with the file and line.

## Where to look (in priority order)
| Source | What to take | Notes |
|---|---|---|
| Robert Walters Thailand salary survey 2026 (robertwalters.co.th, free request form) | Monthly bands for data scientist, data engineer, ML/AI engineer, by experience | Also ask for the 2024 and 2025 editions to get a trend. |
| Michael Page Thailand salary guide (michaelpage.co.th, free download) | Same roles; sector, seniority | Salary benchmark tool is an alternative. |
| Hays / Adecco / Monroe Consulting Thailand salary guides 2025 and 2026 | Same roles, IT sections | Adecco 2025 guide has a download link. |
| Evantis Thailand Salary Guide 2026 | AI, data and analytics monthly bands (the plan's seed figures) | Confirm the figures and band definitions. |
| Levels.fyi Thailand pages (levels.fyi/t/<role>/locations/thailand) | Median total comp, percentiles, n, "last updated" | The agent-friendly `.md` route returned nothing for these; a browser shows them. |
| DEPA digital industry workforce survey 2025 | Demand vs graduates by sector, AI/data skill mismatch | Use the DEPA report itself, not news coverage. |
| TDRI 2025 AI labour market report | Method and base for the 31% / 278% / 37% figures | Needed to judge whether any of it is comparable. |
| NESDC / NSO labour force survey; NXPO / IRIS workforce study | Occupation counts, wages if a matching occupation exists | Official wage data for Thailand is thin for AI roles. |
| JobsDB Thailand search counts | Result count for a fixed query on a fixed date | Log with `uv run aicareers-log-snapshot "AI Engineer" <count>`. Use the same query strings every time. Counts are query-dependent and mix in unrelated roles. |

## Tips
- Record the exact wording of the source's definition. "Monthly base" and "total compensation" are not the same.
- Keep currency as published (THB). USD is added at build time from the ECB rate.
- Do not average sources or fill gaps. If a year is missing, leave it missing.
