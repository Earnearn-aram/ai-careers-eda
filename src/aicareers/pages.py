"""Render static pages. Numbers in prose are computed from observations so they stay traceable."""
from __future__ import annotations

from html import escape
from pathlib import Path

from .schema import Observation

ROLES = [
    ("ai-engineer", "AI / LLM / Applied AI Engineer"), ("ml-engineer", "Machine Learning Engineer"),
    ("data-scientist", "Data Scientist"), ("data-analyst", "Data Analyst / BI"), ("data-engineer", "Data Engineer"),
    ("mlops", "MLOps / LLMOps / AI Platform"), ("ai-research", "AI Research / Applied Scientist"),
    ("ai-pm", "AI Product Manager"), ("forward-deployed", "Forward Deployed / Solutions Engineer (AI)"),
]
ROLE_NAME = {"ai-engineer": "AI / LLM Engineer", "ml-engineer": "Machine Learning Engineer", "data-scientist": "Data Scientist",
             "data-analyst": "Data Analyst / BI", "data-engineer": "Data Engineer"}
BANNER = '<div class="banner"><strong>Exploratory.</strong> Not financial or career advice. Thai data is limited. Figures marked confidence C are hidden unless you tick the box below.</div>'


def shell(title: str, body: str, depth: int = 0) -> str:
    up = "../" * depth
    nav = "".join(f'<a href="{up}{h}">{t}</a>' for h, t in [("index.html", "Overview"), ("compare.html", "Thailand vs world"), ("index.html#roles", "Roles"), ("index.html#limits", "Method and limits"), ("index.html#sources", "Sources")])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} | AI careers EDA</title><link rel="stylesheet" href="{up}style.css"></head><body>
<header><nav>{nav}</nav>{BANNER}<label class="ctl"><input type="checkbox" id="incl-c"> include confidence C (secondary or unverified) figures</label></header>
<main>{body}</main><footer><p class="sub">No tracking, no third-party requests. Data: <a href="{up}data/observations.json">observations.json</a>. Issues and corrections welcome on the repository.</p></footer>
<script src="{up}app.js"></script></body></html>'''


def chart(kind: str, **a: str) -> str:
    attrs = " ".join(f'data-{k.replace("_", "-")}="{escape(v)}"' for k, v in a.items())
    return f'<div data-chart="{kind}" {attrs}></div>'


def indeed_summary(obs: list[Observation]) -> str:
    d = {(o.region, o.period): o for o in obs if o.metric == "ai_keyword_share"}
    first, last = "2023-10", max(p for _, p in d)
    rows = []
    for c in sorted({r for r, _ in d}):
        a, b = d[(c, first)], d[(c, last)]
        rows.append(f"<tr><td>{c}</td><td>{a.value:.2f}%</td><td>{b.value:.2f}%</td><td>{a.id}, {b.id}</td></tr>")
    return (f"<table><thead><tr><th>Country</th><th>{first}</th><th>{last}</th><th>Observation ids</th></tr></thead><tbody>{''.join(rows)}</tbody></table>", last)


def index(obs: list[Observation]) -> str:
    table, last = indeed_summary(obs)
    roles = "".join(f'<li><a href="roles/{s}.html">{escape(n)}</a></li>' for s, n in ROLES)
    return shell("Overview", f'''<h1>AI-related careers, late 2023 to Oct 2026</h1>
<p>An exploratory, source-traceable look at how AI-related careers changed, comparing Thailand with the US, Europe and Singapore/APAC. It starts from no hypothesis and reports what each source says, including where sources disagree or where there is no data.</p>
<h2>Demand: Indeed AI keyword share</h2>
<p>This is the only series so far fetched from its primary source. It measures the share of Indeed job postings whose text contains AI keywords (for example "Machine Learning", "Data Science", "Artificial Intelligence"). It covers nine countries. <strong>Thailand, Singapore and other APAC markets are not in the dataset.</strong> A keyword match does not mean the job requires AI skills, and it counts titles that were relabelled as well as new demand.</p>
{chart("timeseries", metric="ai_keyword_share", regions="US,GB,DE,FR,NL,IE,IT,AU,CA", title="Indeed: share of job postings with AI keywords, monthly mean of daily values", sub="Unit: % of postings. Oct 2023 to Sep 2026. Source: Indeed Hiring Lab AI Tracker (CC BY 4.0).", name="indeed_ai_keyword_share")}
{table}
<p class="sub">Start and end points of the series for each country (monthly mean of 7-day trailing daily values; our aggregation). The series rises in every covered country over the window; the data cannot say how much is new demand and how much is changed wording.</p>
<h2>Demand: share of postings requiring an AI skill (Lightcast / Stanford AI Index)</h2>
<p>A different metric from the one above (a posting must <em>require</em> an AI skill). Not plotted on the same axis. These figures are currently secondary or unverified, so they are hidden unless you tick the confidence C box.</p>
{chart("bars", metric="ai_skill_share", title="Lightcast: share of postings requiring at least one AI skill", sub="Unit: % of postings. Annual. Missing country-years are gaps, not zeros.", name="lightcast_ai_skill_share")}
<h2>Pay</h2>
<p>Pay figures are self-reported (Levels.fyi, skewed towards big tech), recruiter-estimated, or modelled. Sources are shown side by side and never merged or converted. No FX rate has been retrieved yet, so there is no USD conversion. There is no reliable 2023 to 2026 pay trend in the data collected so far.</p>
{chart("pay", title="Pay observations by source (local currency, annual unless the definition says monthly)", sub="2026 cross-section only.", name="pay_all")}
<h2 id="entry">Entry level vs senior</h2>
<p>The evidence collected is US only and descriptive (Stanford Digital Economy Lab, ADP payroll data). Currently unverified, so confidence C.</p>
{chart("bars", metric="employment_gap_age22_25", title="Employment of 22-25 year-olds in highly AI-exposed occupations relative to less-exposed peers", sub="Unit: % difference. US only. Descriptive, not causal.", name="entry_level")}
<h2 id="roles">Role deep-dives</h2><ul>{roles}</ul>
<h2 id="verification">Verification log</h2>
<ul>
<li><strong>Indeed US peak.</strong> A starting note said the US share peaked at 4.2% in December 2025. The current primary CSV shows December 2025 at 4.38% (monthly mean) and values continuing to rise to {last}. The CSV is used; the earlier note is not.</li>
<li><strong>Indeed Q1 2026 Europe.</strong> A starting note (via a secondary blog) gave Germany 4.2%, France 3.3%, UK 2.7%, Netherlands 2.2%. The current CSV gives roughly 4.4%, 3.5%, 7.3% and 2.8% for the Q1 2026 mean. The UK figure differs most. The reason is not established (an earlier data vintage, a different metric, or a misquote); the secondary figures are not used.</li>
<li><strong>Not reachable from the build environment:</strong> Stanford AI Index, Levels.fyi, Indeed Hiring Lab articles, Stanford Digital Economy Lab, BLS, Wayback, JobsDB. Figures from these are carried as confidence C until the primary page is read. Re-run fetching from an environment with open network access.</li>
<li><strong>Indeed GenAI series.</strong> The tracker README lists GenAI_posting.csv, but that file returns 404 (retrieved 2026-10-12).</li>
</ul>
<h2 id="limits">Method and limits</h2>
<ul>
<li>Every number is an observation with source, retrieval date, definition, confidence (A primary and method documented; B primary but self-reported or small sample; C secondary or unverified) and an estimate flag.</li>
<li>Metrics with different definitions are never plotted together. Missing years or regions are left as gaps.</li>
<li>Pay: self-reporting and survivorship bias, big-tech skew, ambiguous titles (the same title covers different jobs), recruiter figures are indicative.</li>
<li>Postings: duplicates and ghost jobs inflate counts; keyword matching is not skill requirement.</li>
<li>Entry-level evidence is US-centric. Thai data is thin: no Thai series in the Indeed tracker, and Thai posting counts depend on the exact search query and date.</li>
<li>Currency: no conversion until an FX rate with date and source is recorded.</li>
</ul>
<h2>How to contribute data or corrections</h2>
<p>Open an issue with the figure, the primary URL, the retrieval date and the exact definition. Corrections to anything on these pages are welcome.</p>
<h2 id="sources">Source list</h2>{chart("sources")}''')


def compare(obs: list[Observation]) -> str:
    return shell("Thailand vs world", f'''<h1>Thailand vs the world</h1>
<p>Thailand evidence is thin. This page shows what exists and states plainly what does not.</p>
<h2>Demand</h2>
<ul><li><strong>Indeed AI Tracker:</strong> no Thailand series (covered: AU, CA, DE, FR, GB, IE, IT, NL, US).</li>
<li><strong>Lightcast / AI Index share requiring an AI skill:</strong> no Thailand figure collected yet. Singapore and a few other economies appear below (confidence C, hidden by default).</li>
<li><strong>JobsDB Thailand counts:</strong> search counts depend on the query text and date, and queries like "AI" mix in trainers and sales roles. Counts from earlier notes were not recorded with an exact query and date, so they are not entered. <code>data/processed/thailand_jobsdb_snapshots.csv</code> and <code>aicareers-log-snapshot</code> exist so a like-for-like series can accumulate from now on. No trend can be drawn today.</li></ul>
{chart("bars", metric="ai_skill_share", title="Lightcast: share of postings requiring at least one AI skill", sub="Unit: %. Thailand absent from the data collected.", name="compare_lightcast")}
<h2>Pay (local currency, separate sources, not converted)</h2>
{chart("pay", title="Pay observations, all regions", sub="Thailand: Levels.fyi pages are small-sample and disagree with each other; recruiter bands are indicative.", name="compare_pay")}
<h2>Employer context</h2>
{chart("bars", metric="org_share_cites_talent_shortage", title="Thailand: organisations citing talent shortage as top barrier to AI adoption", sub="Unit: %. Survey (AWS Summit Bangkok 2026), reported via secondary source.", name="th_talent")}
{chart("bars", metric="org_share_plan_ai_invest_up_50", title="Thailand: enterprises planning to raise AI investment by 50% or more", sub="Unit: %. Survey (Alibaba Cloud / NielsenIQ), reported via secondary source.", name="th_invest")}
<p class="gap">Not available: Thai openings by role over time, Thai skill requirements, Thai entry-level evidence, any Thai pay trend.</p>''')


def role(slug: str, name: str, obs: list[Observation]) -> str:
    mine = [o for o in obs if o.role == ROLE_NAME.get(slug)]
    pay = chart("pay", role=ROLE_NAME[slug], title=f"{name}: pay observations", sub="Local currency; sources shown separately.", name=f"pay_{slug}") if mine else '<p class="gap">No pay observations collected for this role yet.</p>'
    return shell(name, f'''<h1>{escape(name)}</h1>
<p>Built from collected observations only. Each lens below says what exists and what does not.</p>
<h2>Openings</h2><p class="gap">No role-level openings series collected. Country-level AI keyword share is on the <a href="../index.html">overview</a>; it is not specific to this role.</p>
<h2>Requirements and skills</h2><p class="gap">No verified skill-shift data collected for this role.</p>
<h2>Pay</h2>{pay}
<h2>Entry level vs senior</h2><p class="gap">No role-level evidence collected.</p>''', depth=1)


def write_all(obs: list[Observation], site: Path) -> None:
    (site / "roles").mkdir(exist_ok=True)
    (site / "index.html").write_text(index(obs))
    (site / "compare.html").write_text(compare(obs))
    for s, n in ROLES:
        (site / "roles" / f"{s}.html").write_text(role(s, n, obs))
