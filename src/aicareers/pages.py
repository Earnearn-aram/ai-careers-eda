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
    nav = "".join(f'<a href="{up}{h}">{t}</a>' for h, t in [("index.html", "Overview"), ("thailand.html", "Thailand (limited evidence)"), ("index.html#roles", "Roles"), ("index.html#limits", "Method and limits"), ("index.html#sources", "Sources")])
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
    return shell("Overview", f'''<h1>AI-related careers, late 2023 to Oct 2026: a global view</h1>
<p>An exploratory, source-traceable look at how AI-related careers changed, mainly in the US and Europe, with Singapore and Hong Kong as APAC context. It starts from no hypothesis and reports what each source says, including where sources disagree or where there is no data. <strong>Thailand has its own page</strong> because the usable Thai evidence is thin: no Thai series exists in the open datasets used here, and the Thai pay and demand figures are mostly recruiter statements or unverified. The <a href="thailand.html">Thailand page</a> shows what exists and what is missing.</p>
<h2>Demand: Indeed AI keyword share</h2>
<p>The share of Indeed job postings whose text contains AI keywords (for example "Machine Learning", "Data Science", "Artificial Intelligence"). It covers nine countries. <strong>Thailand, Singapore and other APAC markets are not in the dataset.</strong> A keyword match does not mean the job requires AI skills, and it counts relabelled titles as well as new demand.</p>
{chart("timeseries", metric="ai_keyword_share", regions="US,GB,DE,FR,NL,IE,IT,AU,CA", title="Indeed: share of job postings with AI keywords, monthly mean of daily values", sub="Unit: % of postings. Oct 2023 to Sep 2026. Source: Indeed Hiring Lab AI Tracker (CC BY 4.0).", name="indeed_ai_keyword_share")}
{table}
<p class="sub">Start and end of the series per country (monthly mean of 7-day trailing daily values; our aggregation). The series is higher at the end than at the start in every covered country. The data cannot say how much is new demand and how much is changed wording. The tracker is revised between releases: Hiring Lab's 22 Jan 2026 article reported a high of 4.2% for December 2025, while the CSV retrieved in October 2026 shows 4.44% for 31 December 2025. Only the current CSV is plotted.</p>
<h2>Demand: share of postings with an AI skill (Lightcast, AI Index 2026)</h2>
<p>A different metric from the one above: a posting counts when its text includes at least one of 300+ AI skills on Lightcast's list (10 skill clusters; the list is revised every edition, and an "agentic AI" cluster was added this year). <strong>Not plotted with the Indeed series.</strong> Values are comparable only within the 2026 edition: the 2025 edition reported different figures for 2024 (for example US 1.8% vs 1.65% here, Singapore 3.2% vs 2.83%). The set covers 22 economies; <strong>Thailand is not one of them.</strong> Source is the Our World in Data republication of the AI Index 2026 data; 2025 values for 11 economies match the report's Figure 4.4.2 labels.</p>
{chart("bars", metric="ai_skill_share", title="Lightcast: share of job postings with at least one AI skill", sub="Unit: % of postings. 2023 to 2025, annual. Missing economy-years are gaps, not zeros.", name="lightcast_ai_skill_share")}
<h2>Requirements and skills (US, Lightcast)</h2>
<p>Counts of US AI-skill postings that list each skill, 2024 vs 2025 (a posting can list several skills). The AI Index notes that generative AI mentions grew 111% while their share of AI postings fell 5%, and that the share of AI postings mentioning ChatGPT, chatbot or conversational AI declined while agent-related and orchestration terms (for example LangGraph) rose. The "280%+" figure in the Lightcast blog is the agentic cluster's share of <em>all</em> US postings (0.06% to 0.23%); the larger percentages seen elsewhere describe single skills such as "Agentic AI" (151 to 16,541 postings). Only 2024 and 2025 are available; there is no 2023 skill baseline in the sources read so far.</p>
{chart("bars", metric="ai_skill_postings_count", group="skill", title="US AI job postings listing each skill, 2024 vs 2025", sub="Unit: postings (count). Lightcast via AI Index 2026, section 4.4.", name="us_ai_skill_counts")}
<h2 id="pay">Pay</h2>
<p>Pay figures are self-reported (Levels.fyi, verified in tiers but skewed towards big tech), recruiter-estimated, or modelled. Sources are shown side by side and never merged. Local currency comes first; USD uses the ECB reference rate of 9 Oct 2026. Percentile ranges are shown where the source gives them, because one median hides a wide spread (for the US AI Engineer page, p25 to p75 spans $109,500 to $211,250). Rows with confidence C are hidden by default. There is no 2023 to 2026 pay trend in the data collected.</p>
{chart("pay", title="Pay observations by source (annual total compensation unless the definition says otherwise)", sub="2026 cross-section only. Each row names its source, definition, n and confidence.", name="pay_all")}
<h2 id="entry">Entry level vs senior</h2>
<p>The evidence is US only, from ADP payroll data, and descriptive rather than causal. The authors report no evidence of widespread economy-wide job displacement and no comparable gap for experienced workers. The earlier headline numbers (13% in July 2025, 16% in September 2025) came from a regression adjusting for firm-level shocks; the 15% and 19% below are the simpler descriptive shortfall the authors now emphasise.</p>
{chart("bars", metric="employment_shortfall_age22_25", title="Employment of 22-25 year-olds in highly AI-exposed occupations, % below where it would be had it kept pace with less-exposed peers", sub="Unit: %. US only, ADP data. Data vintages July 2025 and June 2026 (Stanford Digital Economy Lab, revised 12 Aug 2026).", name="entry_level")}
<h2>Postings by seniority, and AI in job titles (Indeed Hiring Lab, US unless noted)</h2>
<p>Indeed's articles of 8 and 23 July 2026 describe US postings. Software-development postings rose almost 15% between 24 Feb 2025 and June 2026 while all postings fell 7%, and software-development postings remain 27.5% below their February 2020 level. The authors point out that correlation is not causation and that many factors are at work. 71% of the May 2025 to May 2026 increase in software-development postings came from senior roles and 37% from postings with AI in the title (the two overlap).</p>
{chart("bars", metric="postings_change_vs_2025_01", group="segment", title="US job postings by seniority, change May 2026 vs January 2025", sub="Unit: %. Indeed Hiring Lab, 23 Jul 2026 (task-based seniority classification).", name="postings_by_seniority")}
{chart("bars", metric="share_of_postings_by_seniority", group="segment", title="Share of all US postings by seniority level, May 2026 (approximate)", sub="Unit: %. Senior postings are rising from a low base: about 14% of postings versus 46% entry-level.", name="posting_share_seniority")}
{chart("bars", metric="share_of_applications_by_level", group="segment", title="Where workers with 10+ years of experience applied, May 2026", sub="Unit: % of their applications. Indeed application data.", name="applications_10y")}
<p>Hiring Lab also counts job <em>titles</em> that carry AI in the posting title ("AI-touched" titles: a normalised title with at least 5 postings mentioning AI in the title in a quarter). This is a share of titles, not of postings, so it is not comparable with either series above. In the US the count fell from 264 (Q1 2022) to 159 (Q1 2023) and rose to 822 (Q1 2026), 8.3% of titles. In five of six markets examined, more than half of AI-touched titles are outside tech occupations; the article lists sales, HR, customer service, legal, administrative and teaching roles, many of them long-standing jobs newly described with AI wording. The authors note that an AI title may also be competitive signalling by the employer.</p>
{chart("bars", metric="ai_touched_title_share", title="AI-touched job titles as a share of all normalised titles", sub="Unit: % of TITLES (not postings). Q1 2022 and Q1 2026 for the US; Q1 2026 for five European markets. Source: Indeed Hiring Lab, 8 Jul 2026.", name="ai_title_share")}
<p>Advertised (not realised) US pay is shown by Hiring Lab to have risen about 46% since 2021 in the most AI-exposed occupations versus about 25% in the least exposed. The authors report a post-ChatGPT premium of 5.7% controlling for occupation mix, 4.7% comparing each title with its own past, and 2.4% also holding seniority mix constant (which they note may over-correct), and treat the seniority split as suggestive because most regression terms were not statistically significant.</p>
{chart("bars", metric="advertised_pay_premium_post_chatgpt", group="segment", title="US advertised-pay premium in AI-exposed jobs after ChatGPT, by control used", sub="Unit: %. Advertised pay in postings, not what workers are paid.", name="advertised_pay_premium")}
<h2 id="roles">Role deep-dives</h2><ul>{roles}</ul>
<h2 id="verification">Verification log (checks against primary pages, 12 Oct 2026)</h2>
<ul>
<li><strong>Confirmed.</strong> US share of postings with AI skills 2.5% (+55% YoY) and Singapore about 4.8%, from Lightcast's blog; Switzerland 1.59%, Germany 1.13%, France 0.99%, Austria 0.84% (AI Index Figure 4.4.2); RAG postings 2,885 to 12,609 in the US (AI Index section 4.4); 19% employment shortfall (Stanford DEL); Levels.fyi US AI Engineer median $151,000, n=331, page updated 11 Oct 2026 (the starting note said 10 Oct).</li>
<li><strong>Resolved.</strong> The "10,854%" agentic figure is the single skill "Agentic AI" (151 to 16,541 postings), not the cluster. The 13% vs 15% question: 13% was the earlier regression headline, 15% the descriptive shortfall at the same July 2025 vintage.</li>
<li><strong>Edition differences.</strong> Starting notes took 2024 values (US 1.8%, Singapore 3.2%, Luxembourg 2.0%, Hong Kong 1.9%) from the 2025 report. The 2026 edition gives 1.65%, 2.83%, 2.39% and 2.01% for 2024 because the skill list changes yearly. Only same-edition values are plotted together.</li>
<li><strong>Indeed figures traced to their source.</strong> The starting note that the Indeed US share peaked at 4.2% in December 2025 is from Hiring Lab's 22 Jan 2026 article. The current CSV shows 4.44% for 31 Dec 2025 and rises to {last}, so the series was revised after that article. The starting note's Q1 2026 Germany 4.2%, France 3.3%, UK 2.7%, Netherlands 2.2% (via a secondary blog) are the share of job <em>titles</em> that are AI-touched (Hiring Lab, 8 Jul 2026), not the share of postings; the CSV gives about 4.4%, 3.5%, 7.3% and 2.8% for postings. The 71% senior and 37% AI-titled shares, and "nearly 45%" of data and analytics postings mentioning AI, were confirmed in the articles.</li>
<li><strong>Levels.fyi data quality.</strong> For role plus country pages the markdown header says "Location: United States" with a generic URL, while the figures are in local currency with different sample sizes. Region is taken from the URL requested and these rows are confidence C. Role pages for Thailand did not return data, so the earlier Thai role figures stay unverified (confidence C).</li>
<li><strong>Still not reachable:</strong> BLS (403), JobsDB (403) and Wayback. Their figures stay confidence C or absent.</li>
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


def thailand(obs: list[Observation]) -> str:
    return shell("Thailand vs world", f'''<h1>Thailand: what the evidence shows (limited)</h1>
<p>Thai evidence is thin, so this page does not try to compare Thailand with the world quantitatively. It lists what exists, labels recruiter statements as statements, and says what is missing. For global patterns see the <a href="index.html">overview</a>.</p>
<h2>Demand</h2>
<ul><li><strong>Indeed AI Tracker:</strong> no Thailand series (covered: AU, CA, DE, FR, GB, IE, IT, NL, US).</li>
<li><strong>Lightcast / AI Index share with an AI skill:</strong> Thailand is not among the 22 economies covered. Singapore and Hong Kong are the nearest APAC comparators.</li>
<li><strong>JobsDB Thailand counts:</strong> search counts depend on the query text and date, and queries like "AI" mix in trainers and sales roles. The site returned 403 to the build environment, and earlier counts were not recorded with an exact query and date, so none are entered. <code>data/processed/thailand_jobsdb_snapshots.csv</code> and <code>aicareers-log-snapshot</code> let a like-for-like series accumulate from now on. No trend can be drawn today.</li></ul>
<p>The Lightcast chart of 22 economies on the <a href="index.html">overview</a> is the nearest comparison for APAC (Singapore and Hong Kong); it has no Thailand series.</p>
<h2>Pay (local currency first; USD at the stated ECB rate)</h2>
<p>Two verified Thai pay points exist, both context rather than AI or data roles: the generic <em>Software Engineer</em> median on Levels.fyi (self-reported, n shown) and the top of Michael Page's monthly range for <em>Solution Architect</em> (monthly, from its 2026 guide). Role-specific Thai figures for AI and data roles are unverified and appear only when confidence C is included. For other regions see the <a href="index.html#pay">overview</a>.</p>
{chart("pay", region="TH", title="Thailand: pay observations by source", sub="Annual total compensation (Levels.fyi) and monthly figures (recruiters) are different definitions; read the definition column.", name="th_pay")}
<h2>What Thai recruiters say (statements, not measurements)</h2>
<p><strong>Robert Walters Thailand</strong> (hiring guides of 22 and 30 Dec 2025; the pay data sits in a salary survey that requires a request form) says hiring slowed in 2025, with companies scaling back mid-level hiring to favour senior candidates, and expects AI/ML engineers to be among the roles with the biggest demand in 2026. It names manual QA testers, level-1 support, data-entry operators and junior developers as the roles most exposed to AI because their tasks are repetitive, and expects entry-level salaries to be stable while mid- to senior-level raises are larger. A consultant is quoted on 280,000 new jobs across smart electronics, electric vehicles and semiconductors, with no source given and not specific to AI. <strong>Michael Page Thailand</strong> says unemployment is under 1% and candidates have strong bargaining power; no AI, data or ML role appears in its 2026 top-10 highest-paying list (the only technology role is Solution Architect). These are recruiters' views and expectations from commercial firms that earn fees from placements, not samples of workers or postings.</p>
{chart("ranges", metric_lo="pay_increment_pct_low", metric_hi="pay_increment_pct_high", title="Thailand: expected salary increment when changing jobs, 2026", sub="Unit: % increase. Ranges stated by two recruiters (indicative, not survey samples).", name="th_increments")}
<h2>Where Thai figures may come from (leads, not yet read)</h2>
<p>These sources were found through search summaries only. Their hosts are blocked from the build environment, or the survey is gated behind a request form. Nothing from them is shown unless a person has read the page or file and entered the figure with its definition (see <code>docs/THAILAND_COLLECTION.md</code>). Any figures already recorded from them are confidence C and hidden by default.</p>
<table><thead><tr><th>Source</th><th>Would add</th><th>Status</th></tr></thead><tbody>
<tr><td>Robert Walters Thailand salary survey 2026 (and 2024, 2025 editions)</td><td>Monthly pay bands for data and AI roles; a pay trend if earlier editions are obtained</td><td>Hiring guides read (above); the survey itself is gated (free request form)</td></tr>
<tr><td>Michael Page Thailand salary guide</td><td>Same roles from a second recruiter, to show disagreement</td><td>Top-10 page read (above); the guide is a form-gated download</td></tr>
<tr><td>Hays, Adecco, Monroe Consulting Thailand guides</td><td>A third and fourth recruiter</td><td>Hosts blocked; downloads are free</td></tr>
<tr><td>DEPA digital industry workforce survey 2025</td><td>Demand vs graduates by sector; skills mismatch in AI and data analytics</td><td>Seen via news coverage only; depa.or.th is reachable but the report was not located</td></tr>
<tr><td>TDRI 2025 AI labour market report</td><td>Thai AI posting growth. Its definition and base are unknown, so it is not comparable with Indeed or Lightcast</td><td>Seen via an undated government page only</td></tr>
<tr><td>Levels.fyi role pages for Thailand</td><td>Role-level medians, percentiles and n</td><td>Not served on the agent-friendly route</td></tr>
<tr><td>JobsDB Thailand search counts</td><td>A like-for-like series if logged with fixed queries</td><td>Pages return 403 to automated requests; counts must be read by hand</td></tr>
</tbody></table>
{chart("bars", metric="software_workforce_per_year", group="segment", title="Thailand: software sector people needed vs graduates entering related fields, per year", sub="Unit: people per year. DEPA 2025 digital industry survey, reported via Thairath Online (confidence C, hidden by default). Whole software sector, not AI-specific.", name="th_software_workforce")}
<h2>Employer context</h2>
{chart("bars", metric="org_share_cites_skill_shortage", title="Thailand: organisations citing lack of skilled candidates as the primary hiring obstacle", sub="Unit: %, reported as 'over 67%'. Robert Walters Thailand 2026 survey, via The Story Thailand (confidence C). All sectors, not AI-specific.", name="th_skill_shortage")}
{chart("bars", metric="org_share_cites_talent_shortage", title="Thailand: organisations citing talent shortage as top barrier to AI adoption", sub="Unit: %. Survey (AWS Summit Bangkok 2026), reported via secondary source.", name="th_talent")}
{chart("bars", metric="org_share_plan_ai_invest_up_50", title="Thailand: enterprises planning to raise AI investment by 50% or more", sub="Unit: %. Survey (Alibaba Cloud / NielsenIQ), reported via secondary source.", name="th_invest")}
<p class="gap">Not available: Thai openings by role over time, Thai skill requirements, Thai entry-level evidence, any Thai pay trend.</p>''')


SKILL_ROLES = {"ai-engineer", "ml-engineer", "mlops"}
DATA_ROLES = {"data-scientist", "data-analyst", "data-engineer"}


def role(slug: str, name: str, obs: list[Observation]) -> str:
    rn = ROLE_NAME.get(slug)
    mine = [o for o in obs if rn and o.role == rn]
    shared: list[Observation] = []
    openings = '<p class="gap">No role-level openings series was collected. The country-level series on the <a href="../index.html">overview</a> are not specific to this role.</p>'
    req = '<p class="gap">No verified skill-shift data was collected for this role.</p>'
    if slug in DATA_ROLES:
        shared = [o for o in obs if o.metric == "ai_keyword_share_by_occupation"]
        openings = ('<p>Not a role-level openings series. Indeed Hiring Lab reported the share of US postings in broad occupation groups that mention AI terms, as of December 2025 (January 2026 article). Data and analytics sits well above the other groups shown. A mention does not mean the job requires AI work, and the figure is a share of postings, not a count of openings. Only one date is available, so there is no trend.</p>'
                    + chart("bars", metric="ai_keyword_share_by_occupation", group="segment", title="US postings mentioning AI terms, by occupation group, December 2025", sub="Unit: % of postings in the group. Indeed Hiring Lab, 22 Jan 2026 (a different vintage and definition from the AI Tracker CSV; do not compare with it).", name=f"ai_mentions_{slug}"))
    if slug in SKILL_ROLES:
        shared = [o for o in obs if o.metric == "ai_skill_postings_count"]
        req = ('<p>Not role-specific. These are skills listed across all US AI-skill postings (Lightcast, AI Index 2026), the closest available evidence for roles that build with these tools. Counts for 2024 and 2025 only; there is no 2023 baseline in the sources read.</p>'
               + chart("bars", metric="ai_skill_postings_count", group="skill", title="US AI job postings listing each skill, 2024 vs 2025", sub="Unit: postings (count). A posting can list several skills.", name=f"skills_{slug}"))
    pay = chart("pay", role=rn, title=f"{name}: pay observations", sub="Local currency; USD at the stated ECB rate; sources shown separately.", name=f"pay_{slug}") if mine else '<p class="gap">No pay observations were collected for this role.</p>'
    ids = sorted({o.id for o in mine + shared})
    ev = f'<h2>Evidence on this page</h2><p class="sub">Observation ids (in <a href="../data/observations.json">observations.json</a>): {escape(", ".join(ids)) if ids else "none"}.</p>'
    return shell(name, f'''<h1>{escape(name)}</h1>
<p>Built only from collected observations. Each lens says what exists and what does not. Pay is one source among several and skews high for big-tech roles; Levels.fyi in particular is self-reported.</p>
<h2>Openings</h2>{openings}
<h2>Requirements and skills</h2>{req}
<h2>Pay</h2>{pay}
<h2>Entry level vs senior</h2><p class="gap">No role-level evidence was collected. The US-wide seniority and entry-level evidence is on the <a href="../index.html#entry">overview</a>; it is not specific to this role.</p>
{ev}''', depth=1)


def write_all(obs: list[Observation], site: Path) -> None:
    (site / "roles").mkdir(exist_ok=True)
    (site / "index.html").write_text(index(obs))
    (site / "thailand.html").write_text(thailand(obs))
    for s, n in ROLES:
        (site / "roles" / f"{s}.html").write_text(role(s, n, obs))
