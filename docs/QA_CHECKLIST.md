# QA checklist status (12 Oct 2026)

| Item | Status | Notes |
|---|---|---|
| Every number traces to a row in `sources.csv` | Partly | Enforced for all observations (test). Numbers typed into page prose (for example "almost 15%", the Indeed start/end table is generated) are written by hand and not machine-checked; each is also an observation. |
| No chart mixes metrics with different definitions | Yes | Charts take one metric; tests check one unit per metric and keep Lightcast, Indeed keyword share, Indeed title share and TDRI as separate metrics. |
| No fabricated, interpolated or extrapolated values | Yes | Test checks the Indeed monthly series has no filled gaps; missing economy-years are gaps. One derived value (Spain non-tech share = 100 - 64) is flagged in its notes. |
| Currency: rate, date, source; local currency beside USD | Yes | ECB reference rates dated 2026-10-09, shown under each pay table. |
| Secondary-only figures are confidence C and hidden by default | Yes | Tests; the checkbox or `?c=1` shows them. |
| Sample sizes shown; n under 30 flagged | Yes | Pay table column and a warning marker. |
| Neutral wording | Yes | Test bans loaded words; manual scan found none. Hiring Lab's own caveats (correlation, over-correction) are carried into the text. |
| Limits section lists the required items | Yes | Self-reporting and survivorship, big-tech skew, title ambiguity, duplicates and ghost jobs, US-centric entry-level evidence, thin Thai data. |
| Re-run all links; archive key pages on Wayback | No | Wayback is unreachable from the build environment. Instead `data/raw/MANIFEST.csv` records URL, date and sha256 and `scripts/fetch_raw.sh` re-checks them. Links were not machine-checked. |
| Second pass for framing that favours a narrative | Done once | Both directions are shown: software postings up about 15% since Feb 2025 yet 27.5% below Feb 2020; entry-level shortfall 19% with no economy-wide displacement found; advertised-pay premium shrinks from 5.7% to 2.4% under stricter controls. Findings stay descriptive and the authors' causal caveats are quoted. A reviewer outside the project should repeat this pass. |

## Known weaknesses
- Pay is cross-section only. No 2023 to 2026 trend exists in the collected data.
- Lightcast shares are a Our World in Data republication, spot-checked against the report, confidence B.
- Levels.fyi region for role+country pages is inferred from the requested URL (confidence C).
- Thai evidence is limited to a few recruiter statements and two context pay points.
- Singapore and APAC posting volumes beyond the Lightcast share were not collected.
