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
<p>The share of Indeed job postings whose text contains AI keywords (for example "Machine Learning", "Data Science", "Artificial Intelligence"). It covers nine countries. <strong>Thailand, Singapore and other APAC markets are not in the dataset.</strong> A keyword match does not mean the job requires AI skills, and it counts relabelled titles as well as new demand.</p>
{chart("timeseries", metric="ai_keyword_share", regions="US,GB,DE,FR,NL,IE,IT,AU,CA", title="Indeed: share of job postings with AI keywords, monthly mean of daily values", sub="Unit: % of postings. Oct 2023 to Sep 2026. Source: Indeed Hiring Lab AI Tracker (CC BY 4.0).", name="indeed_ai_keyword_share")}
{table}
<p class="sub">Start and end of the series per country (monthly mean of 7-day trailing daily values; our aggregation). The series is higher at the end than at the start in every covered country. The data cannot say how much is new demand and how much is changed wording.</p>
<h2>Demand: share of postings with an AI skill (Lightcast, AI Index 2026)</h2>
<p>A different metric from the one above: a posting counts when its text includes at least one of 300+ AI skills on Lightcast's list (10 skill clusters; the list is revised every edition, and an "agentic AI" cluster was added this year). <strong>Not plotted with the Indeed series.</strong> Values are comparable only within the 2026 edition: the 2025 edition reported different figures for 2024 (for example US 1.8% vs 1.65% here, Singapore 3.2% vs 2.83%). The set covers 22 economies; <strong>Thailand is not one of them.</strong> Source is the Our World in Data republication of the AI Index 2026 data; 2025 values for 11 economies match the report's Figure 4.4.2 labels.</p>
{chart("bars", metric="ai_skill_share", title="Lightcast: share of job postings with at least one AI skill", sub="Unit: % of postings. 2023 to 2025, annual. Missing economy-years are gaps, not zeros.", name="lightcast_ai_skill_share")}
<h2>Requirements and skills (US, Lightcast)</h2>
<p>Counts of US AI-skill postings that list each skill, 2024 vs 2025 (a posting can list several skills). The AI Index notes that generative AI mentions grew 111% while their share of AI postings fell 5%, and that the share of AI postings mentioning ChatGPT, chatbot or conversational AI declined while agent-related and orchestration terms (for example LangGraph) rose. The "280%+" figure in the Lightcast blog is the agentic cluster's share of <em>all</em> US postings (0.06% to 0.23%); the larger percentages seen elsewhere describe single skills such as "Agentic AI" (151 to 16,541 postings). Only 2024 and 2025 are available; there is no 2023 skill baseline in the sources read so far.</p>
{chart("bars", metric="ai_skill_postings_count", group="skill", title="US AI job postings listing each skill, 2024 vs 2025", sub="Unit: postings (count). Lightcast via AI Index 2026, section 4.4.", name="us_ai_skill_counts")}
<h2>Pay</h2>
<p>Pay figures are self-reported (Levels.fyi, verified in tiers but skewed towards big tech), recruiter-estimated, or modelled. Sources are shown side by side and never merged. Local currency comes first; USD uses the ECB reference rate of 9 Oct 2026. Percentile ranges are shown where the source gives them, because one median hides a wide spread (for the US AI Engineer page, p25 to p75 spans $109,500 to $211,250). Rows with confidence C are hidden by default. There is no 2023 to 2026 pay trend in the data collected.</p>
{chart("pay", title="Pay observations by source (annual total compensation unless the definition says otherwise)", sub="2026 cross-section only. Each row names its source, definition, n and confidence.", name="pay_all")}
<h2 id="entry">Entry level vs senior</h2>
<p>The evidence is US only, from ADP payroll data, and descriptive rather than causal. The authors report no evidence of widespread economy-wide job displacement and no comparable gap for experienced workers. The earlier headline numbers (13% in July 2025, 16% in September 2025) came from a regression adjusting for firm-level shocks; the 15% and 19% below are the simpler descriptive shortfall the authors now emphasise.</p>
{chart("bars", metric="employment_shortfall_age22_25", title="Employment of 22-25 year-olds in highly AI-exposed occupations, % below where it would be had it kept pace with less-exposed peers", sub="Unit: %. US only, ADP data. Data vintages July 2025 and June 2026 (Stanford Digital Economy Lab, revised 12 Aug 2026).", name="entry_level")}
<h2 id="roles">Role deep-dives</h2><ul>{roles}</ul>
<h2 id="verification">Verification log (checks against primary pages, 12 Oct 2026)</h2>
<ul>
<li><strong>Confirmed.</strong> US share of postings with AI skills 2.5% (+55% YoY) and Singapore about 4.8%, from Lightcast's blog; Switzerland 1.59%, Germany 1.13%, France 0.99%, Austria 0.84% (AI Index Figure 4.4.2); RAG postings 2,885 to 12,609 in the US (AI Index section 4.4); 19% employment shortfall (Stanford DEL); Levels.fyi US AI Engineer median $151,000, n=331, page updated 11 Oct 2026 (the starting note said 10 Oct).</li>
<li><strong>Resolved.</strong> The "10,854%" agentic figure is the single skill "Agentic AI" (151 to 16,541 postings), not the cluster. The 13% vs 15% question: 13% was the earlier regression headline, 15% the descriptive shortfall at the same July 2025 vintage.</li>
<li><strong>Edition differences.</strong> Starting notes took 2024 values (US 1.8%, Singapore 3.2%, Luxembourg 2.0%, Hong Kong 1.9%) from the 2025 report. The 2026 edition gives 1.65%, 2.83%, 2.39% and 2.01% for 2024 because the skill list changes yearly. Only same-edition values are plotted together.</li>
<li><strong>Not matched.</strong> A starting note said the Indeed US share peaked at 4.2% in December 2025. The current Indeed CSV shows December 2025 at 4.38% (monthly mean), still rising to {last}. A note via a secondary blog gave Q1 2026 Germany 4.2%, France 3.3%, UK 2.7%, Netherlands 2.2%; the CSV gives about 4.4%, 3.5%, 7.3% and 2.8%. The UK differs most; the cause is not established. The CSV is used.</li>
<li><strong>Levels.fyi data quality.</strong> For role plus country pages the markdown header says "Location: United States" with a generic URL, while the figures are in local currency with different sample sizes. Region is taken from the URL requested and these rows are confidence C. Role pages for Thailand did not return data, so the earlier Thai role figures stay unverified (confidence C).</li>
<li><strong>Still not reachable:</strong> Indeed Hiring Lab articles (redirects to a blocked host), BLS, JobsDB and Wayback. Their figures stay confidence C or absent.</li>
<li><strong>Indeed GenAI series.</strong> The tracker README lists GenAI_posting.csv, but that file returns 404.</li>
</ul>
<h2 id="limits">Method and limits</h2>
<ul>
<li>Every number is an observation with source, retrieval date, definition, confidence (A primary and method documented; B primary but republished, self-reported or small sample; C secondary or unverified) and an estimate flag.</li>
<li>Metrics with different definitions are never plotted together. Missing years or regions are left as gaps.</li>
<li>Pay: self-reporting and survivorship bias, big-tech skew, ambiguous titles, recruiter figures are indicative.</li>
<li>Postings: duplicates and ghost jobs inflate counts; keyword or skill-list matching is not the same as a skill requirement.</li>
<li>Entry-level evidence is US-centric. Thai data is thin: no Thai series in the Indeed tracker or the Lightcast set, and Thai posting counts depend on the exact search query and date.</li>
<li>Currency: USD uses ECB reference rates dated 9 Oct 2026, applied to 2026 figures only.</li>
</ul>
<h2>How to contribute data or corrections</h2>
<p>Open an issue with the figure, the primary URL, the retrieval date and the exact definition. Corrections to anything on these pages are welcome.</p>
<h2 id="sources">Source list</h2>{chart("sources")}''')


def compare(obs: list[Observation]) -> str:
    return shell("Thailand vs world", f'''<h1>Thailand vs the world</h1>
<p>Thailand evidence is thin. This page shows what exists and states plainly what does not.</p>
<h2>Demand</h2>
<ul><li><strong>Indeed AI Tracker:</strong> no Thailand series (covered: AU, CA, DE, FR, GB, IE, IT, NL, US).</li>
<li><strong>Lightcast / AI Index share with an AI skill:</strong> Thailand is not among the 22 economies covered. Singapore and Hong Kong are the nearest APAC comparators.</li>
<li><strong>JobsDB Thailand counts:</strong> search counts depend on the query text and date, and queries like "AI" mix in trainers and sales roles. The site returned 403 to the build environment, and earlier counts were not recorded with an exact query and date, so none are entered. <code>data/processed/thailand_jobsdb_snapshots.csv</code> and <code>aicareers-log-snapshot</code> let a like-for-like series accumulate from now on. No trend can be drawn today.</li></ul>
{chart("bars", metric="ai_skill_share", title="Lightcast: share of job postings with at least one AI skill", sub="Unit: %. Thailand absent from the dataset.", name="compare_lightcast")}
<h2>Pay (local currency first; USD at the stated ECB rate)</h2>
<p>The only verified Thai pay figure is for the generic <em>Software Engineer</em> role on Levels.fyi, shown as context. Role-specific Thai figures (AI, data) are unverified, from earlier notes, and shown only when confidence C is included. Levels.fyi Thai medians depend on a self-selected sample.</p>
{chart("pay", title="Pay observations, all regions", sub="Compare within a role and source first; sources differ in definition and sample.", name="compare_pay")}
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
