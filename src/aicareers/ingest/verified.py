"""Figures read directly from fetched primary pages (2026-10-12). Each row names where it was found."""
from __future__ import annotations

from datetime import date

from ..schema import Confidence, Observation

R = date(2026, 10, 12)
IDX = "stanford_ai_index_2026"
CNT = "Postings listing the skill among US AI job postings (a posting can list several skills). Lightcast, AI Index 2026 report."


def _o(id, metric, region, period, value, unit, src, defn, conf=Confidence.A, role="all", **kw):
    return Observation(id=id, metric=metric, role=role, region=region, period=period, value=value, unit=unit, source_id=src,
                       retrieved_on=R, definition=defn, confidence=conf, **kw)


def load() -> list[Observation]:
    o = []
    # AI Index 2026, section 4.4 (Jobs), "Generative AI skills in AI job postings in the US, 2024 vs 2025" and "AI agent skills ..."
    skills = [("rag", "Retrieval augmented generation", 2885, 12609), ("genai", "Generative artificial intelligence", 65557, 138188),
              ("llm", "Large language modeling", 19045, 38526), ("prompt", "Prompt engineering", 6152, 22227),
              ("agentic-ai", "Agentic AI (single skill)", 151, 16541), ("ai-agents", "AI agents", 1310, 15217),
              ("chatgpt", "ChatGPT", 5535, 14376), ("conv-ai", "Conversational AI", 5430, 6976), ("langgraph", "LangGraph", 194, 4294),
              ("copilot", "Microsoft Copilot", 1416, 6395), ("chatbot", "Chatbot", 2316, 4596)]
    for key, name, a, b in skills:
        for yr, v in (("2024", a), ("2025", b)):
            o.append(_o(f"aix-skill-{key}-{yr}", "ai_skill_postings_count", "US", yr, float(v), "count", IDX, CNT, skill=name,
                        notes="AI Index 2026, section 4.4 skill charts (2024 vs 2025)."))
    o.append(_o("aix-py-2025", "ai_skill_postings_count", "US", "2025", 258674.0, "count", IDX,
                "Postings listing Python (most frequent specialised skill in US AI postings). AI Index 2026 section 4.4.", skill="Python"))
    # Lightcast blog (Lightcast is the data owner), cluster-level shares of ALL US postings
    for yr, v in (("2024", 0.06), ("2025", 0.23)):
        o.append(_o(f"lcblog-agentic-cluster-{yr}", "agentic_cluster_share_all_postings", "US", yr, v, "%", "lightcast_blog_ai_index_2026",
                    "Share of all US job postings with Agentic AI cluster skills (agents, agentic systems). Lightcast blog quoting AI Index 2026.",
                    conf=Confidence.B, notes='Blog: "more than 280% increase", "nearly 90,000 job postings in the US". Different slice from the single skill "Agentic AI" (151 to 16,541 postings).'))
    # Stanford Digital Economy Lab, Canaries (rev. 12 Aug 2026), ADP payroll, descriptive
    D = "stanford_del_canaries"
    ddef = "Employment of 22-25 year-olds in highly AI-exposed occupations is this % below where it would be had it kept pace with less-exposed peers (descriptive 'kept-pace shortfall'; ADP payroll data; not causal)."
    o += [_o("del-gap-2025-07", "employment_shortfall_age22_25", "US", "2025-07", 15.0, "%", D, ddef, conf=Confidence.B, notes="Data vintage July 2025 (paper, Aug 2026 revision)."),
          _o("del-gap-2026-06", "employment_shortfall_age22_25", "US", "2026-06", 19.0, "%", D, ddef, conf=Confidence.B, notes="Data through June 2026. Experienced workers show no comparable gap; no economy-wide displacement found."),
          _o("del-reg-2025-07", "employment_decline_age22_25_regression", "US", "2025-07", 13.0, "%", D, "Earlier headline regression estimate (adjusting for firm-level shocks), relative decline for 22-25 year-olds in exposed occupations.", conf=Confidence.B, notes="Superseded as the headline; different method from the shortfall metric."),
          _o("del-reg-2025-09", "employment_decline_age22_25_regression", "US", "2025-09", 16.0, "%", D, "Same regression estimate, September 2025 data.", conf=Confidence.B)]
    o += _hiringlab()
    o += _thailand_recruiters()
    return o


def _th(id, metric, period, value, unit, src, defn, url, who, role="all", **kw):
    return _o(id, metric, "TH", period, value, unit, src, defn, conf=Confidence.B, role=role, is_estimate=kw.pop("approx", True),
              notes=f"{who}. {url}. Recruiter statement, indicative, not a survey sample. " + kw.pop("notes", ""), **kw)


def _thailand_recruiters() -> list[Observation]:
    RW = "robert_walters_th_2026"
    CO = "https://www.robertwalters.co.th/insights/hiring-advice/blog/country-overview-hiring-guide-and-trends-2026.html"
    MP = "michaelpage_th"
    MPU = "https://www.michaelpage.co.th/advice/career-advice/salary-and-negotiation/highest-paying-jobs-thailand"
    inc = "Expected salary increment for people changing jobs in Thailand in 2026 (percentage points of pay), %s: %s end of the stated range."
    o = []
    for seg, lo, hi in (("In-demand skills, 'plug-and-play' movers", 15, 20), ("Hired on potential or lateral moves", 10, 15), ("Staying in the same role", 2, 4)):
        o.append(_th(f"th-rw-inc-{seg[:6].lower().replace(' ', '').replace(chr(39), '').replace(',', '')}-lo", "pay_increment_pct_low", "2026", float(lo), "%", RW, inc % (seg, "low"), CO, "Robert Walters Thailand, Country Overview (30 Dec 2025)", segment=seg, approx=False))
        o.append(_th(f"th-rw-inc-{seg[:6].lower().replace(' ', '').replace(chr(39), '').replace(',', '')}-hi", "pay_increment_pct_high", "2026", float(hi), "%", RW, inc % (seg, "high"), CO, "Robert Walters Thailand, Country Overview (30 Dec 2025)", segment=seg, approx=False))
    o.append(_th("th-mp-inc-lo", "pay_increment_pct_low", "2026", 15.0, "%", MP, "Average salary increment now (candidates changing jobs, all sectors), low end. Same page says some reach 40%.", MPU, "Michael Page Thailand, 'Highest-paying jobs in Thailand: Top 10 in 2026'", segment="Michael Page: average increment, all sectors", approx=False))
    o.append(_th("th-mp-inc-hi", "pay_increment_pct_high", "2026", 20.0, "%", MP, "Average salary increment now (candidates changing jobs, all sectors), high end.", MPU, "Michael Page Thailand, 'Highest-paying jobs in Thailand: Top 10 in 2026'", segment="Michael Page: average increment, all sectors", approx=False))
    o.append(_th("th-mp-solarch-hi", "salary_monthly_high_range", "2026", 250000.0, "THB", MP, "Higher end of average MONTHLY salary for Solution Architect (technology), from Michael Page's 2026 Salary Guide as listed on its Top 10 page. Only tech role in the list; no AI, data or ML role appears.", MPU, "Michael Page Thailand", role="Solution Architect (context)", approx=False))
    return o


HL = "indeed_hiringlab_articles"
U = "https://hiringlab.indeed.com/"


def _hl(id, metric, region, period, value, unit, defn, art, role="all", approx=False, **kw):
    return _o(id, metric, region, period, value, unit, HL, defn, role=role, is_estimate=approx,
              notes=f"Indeed Hiring Lab, {art[0]} ({art[1]}). {U}{art[2]}. " + kw.pop("notes", ""), **kw)


def _hiringlab() -> list[Observation]:
    DJ = ("8 Jul 2026", "AI and Job Postings: From Destruction to Creation?", "2026/07/08/ai-and-job-postings-from-destruction-to-creation/")
    TI = ("8 Jul 2026", "AI Is No Longer Just a Tech Occupation Story", "2026/07/08/ai-is-no-longer-just-a-tech-occupation-story/")
    SN = ("23 Jul 2026", "The Labor Market Is Tilting Toward Seniority", "2026/07/23/the-labor-market-is-tilting-toward-seniority/")
    EN = ("23 Jul 2026", "Entry-Level Jobs Aren't Just for Inexperienced Workers", "2026/07/23/entry-level-jobs-arent-just-for-inexperienced-workers/")
    JN = ("22 Jan 2026", "January 2026 US Labor Market Update", "2026/01/22/january-labor-market-update-jobs-mentioning-ai-are-growing-amid-broader-hiring-weakness/")
    PY = ("17 Sep 2026", "AI Exposure Isn't Squeezing Advertised Pay in the US", "2026/09/17/ai-exposure-isnt-squeezing-advertised-pay-in-the-us-its-boosting-it/")
    o = []
    # software development postings (US, seasonally adjusted)
    o += [_hl("hl-sw-since-cc", "postings_change_since_2025_02_24", "US", "2026-06", 15.0, "%", "Change in US software-development postings since 24 Feb 2025 (Claude Code launch date used by the authors as a marker). Article says 'almost 15%'; correlation not causation, per the authors.", DJ, role="Software development (context)", approx=True, segment="Software development"),
          _hl("hl-all-since-cc", "postings_change_since_2025_02_24", "US", "2026-06", -7.0, "%", "Change in all US postings over the same period.", DJ, segment="All postings"),
          _hl("hl-sw-vs-2020", "postings_change_vs_2020_02", "US", "2026-06", -27.5, "%", "US software-development postings relative to Feb 2020 (pre-pandemic), seasonally adjusted. All postings are 'essentially unchanged' on the same basis.", DJ, role="Software development (context)", segment="Software development"),
          _hl("hl-sw-senior-71", "share_of_posting_increase", "US", "2026-05", 71.0, "%", "Share of the May 2025 to May 2026 increase in US software-development postings that came from senior roles.", DJ, role="Software development (context)", segment="Senior roles"),
          _hl("hl-sw-ai-37", "share_of_posting_increase", "US", "2026-05", 37.0, "%", "Share of the same increase from postings with AI in the title. Overlaps with the senior share; the two do not sum.", DJ, role="Software development (context)", segment="AI-titled roles")]
    # seniority of all US postings
    sdef = "Change in US job postings by seniority (Indeed's task-based seniority classification), %s."
    o += [_hl("hl-sen-yoy-senior", "postings_change_yoy_may2026", "US", "2026-05", 14.7, "%", sdef % "May 2026 vs May 2025", SN, segment="Senior"),
          _hl("hl-sen-yoy-entry", "postings_change_yoy_may2026", "US", "2026-05", -7.5, "%", sdef % "May 2026 vs May 2025", SN, segment="Entry"),
          _hl("hl-sen-jan25-senior", "postings_change_vs_2025_01", "US", "2026-05", 13.5, "%", sdef % "May 2026 vs Jan 2025", SN, segment="Senior"),
          _hl("hl-sen-jan25-mid", "postings_change_vs_2025_01", "US", "2026-05", -6.7, "%", sdef % "May 2026 vs Jan 2025", SN, segment="Mid"),
          _hl("hl-sen-jan25-entry", "postings_change_vs_2025_01", "US", "2026-05", -6.3, "%", sdef % "May 2026 vs Jan 2025", SN, segment="Entry", notes="Article text elsewhere says 6.2% for the same comparison."),
          _hl("hl-sen-share-senior", "share_of_postings_by_seniority", "US", "2026-05", 14.0, "%", "Share of all US postings at each seniority level (about).", SN, segment="Senior", approx=True),
          _hl("hl-sen-share-mid", "share_of_postings_by_seniority", "US", "2026-05", 40.0, "%", "Share of all US postings at each seniority level (about).", SN, segment="Mid", approx=True),
          _hl("hl-sen-share-entry", "share_of_postings_by_seniority", "US", "2026-05", 46.0, "%", "Share of all US postings at each seniority level (about).", SN, segment="Entry", approx=True),
          _hl("hl-swdev-senior-share", "senior_share_of_postings_in_occupation", "US", "2026-Q1", 69.3, "%", "Senior-level share of software-development postings, Q1 2026 (highest of occupations listed).", SN, role="Software development (context)", segment="Senior"),
          _hl("hl-apps-10y-senior", "share_of_applications_by_level", "US", "2026-05", 12.0, "%", "Share of applications by workers with 10+ years of experience that went to senior-level roles (Indeed application data).", EN, segment="Senior roles"),
          _hl("hl-apps-10y-entry", "share_of_applications_by_level", "US", "2026-05", 49.0, "%", "Share of applications by workers with 10+ years of experience that went to entry-level roles.", EN, segment="Entry-level roles")]
    # AI in job titles
    tdef = "Number of normalised job titles with at least 5 postings having AI in the raw posting title in the quarter ('AI-touched' titles). Not a share of postings."
    for yr, v, extra in (("2022-Q1", 264, "2.6% of titles"), ("2023-Q1", 159, ""), ("2026-Q1", 822, "8.3% of titles")):
        o.append(_hl(f"hl-aititles-US-{yr}", "ai_touched_title_count", "US", yr, float(v), "count", tdef, TI, notes=extra))
    for cc, n, sh, nt in (("DE", 288, 4.2, 59), ("GB", 160, 2.7, 54), ("FR", 138, 3.3, 54), ("NL", 84, 2.2, 58), ("ES", 81, 2.3, 36)):
        o.append(_hl(f"hl-aititles-{cc}-2026-Q1", "ai_touched_title_count", cc, "2026-Q1", float(n), "count", tdef, TI))
        o.append(_hl(f"hl-aititles-share-{cc}-2026-Q1", "ai_touched_title_share", cc, "2026-Q1", sh, "%", "AI-touched titles as % of all normalised titles with at least 5 postings, Q1 2026. A share of TITLES, not of postings.", TI))
        o.append(_hl(f"hl-aititles-nontech-{cc}", "ai_touched_titles_nontech_share", cc, "2026-Q1", float(nt), "%", "Share of AI-touched titles that are outside tech occupations, Q1 2026.", TI, notes="Spain: article reports 64% of AI-touched titles are tech, so 36% non-tech." if cc == "ES" else ""))
    o.append(_hl("hl-aititles-nontech-US", "ai_touched_titles_nontech_share", "US", "2026-Q1", 63.0, "%", "Share of AI-touched titles that are outside tech occupations, Q1 2026.", TI))
    o.append(_hl("hl-aititles-share-US-2022-Q1", "ai_touched_title_share", "US", "2022-Q1", 2.6, "%", "AI-touched titles as % of all normalised titles with at least 5 postings. A share of TITLES, not of postings.", TI))
    o.append(_hl("hl-aititles-share-US-2026-Q1", "ai_touched_title_share", "US", "2026-Q1", 8.3, "%", "AI-touched titles as % of all normalised titles with at least 5 postings. A share of TITLES, not of postings.", TI))
    # Jan 2026 update (as published then)
    o += [_hl("hl-jan26-tracker-high", "ai_keyword_share_as_published", "US", "2025-12", 4.2, "%", "Indeed AI Tracker high at end of 2025 as reported on 22 Jan 2026. The current CSV (retrieved Oct 2026) gives 4.44% for 31 Dec 2025, so the series has been revised since; do not splice vintages.", JN, notes="Different vintage from the AI_posting.csv series."),
          _hl("hl-jan26-da", "ai_keyword_share_by_occupation", "US", "2025-12", 45.0, "%", "Share of US data & analytics postings containing AI-related terms ('nearly 45%').", JN, approx=True, segment="Data & analytics"),
          _hl("hl-jan26-mkt", "ai_keyword_share_by_occupation", "US", "2025-12", 15.0, "%", "Share of US marketing postings containing AI-related terms ('about 15%').", JN, approx=True, segment="Marketing"),
          _hl("hl-jan26-hr", "ai_keyword_share_by_occupation", "US", "2025-12", 9.0, "%", "Share of US human resources postings containing AI-related terms ('9%').", JN, approx=True, segment="Human resources")]
    # advertised pay by AI exposure (US)
    o += [_hl("hl-pay-hi", "advertised_pay_growth_since_2021", "US", "2026-06", 46.0, "%", "Growth in median advertised salary since the 2021 average, most AI-exposed occupations (about). Advertised, not realised, pay.", PY, approx=True, segment="Most AI-exposed"),
          _hl("hl-pay-lo", "advertised_pay_growth_since_2021", "US", "2026-06", 25.0, "%", "Same, least AI-exposed occupations (about).", PY, approx=True, segment="Least AI-exposed"),
          _hl("hl-pay-prem-mix", "advertised_pay_premium_post_chatgpt", "US", "2026-06", 5.7, "%", "Post-ChatGPT advertised-pay premium for AI-exposed jobs, controlling for occupation mix.", PY, segment="Control: occupation mix"),
          _hl("hl-pay-prem-title", "advertised_pay_premium_post_chatgpt", "US", "2026-06", 4.7, "%", "Same premium comparing each job title with its own past.", PY, segment="Control: job title"),
          _hl("hl-pay-prem-sen", "advertised_pay_premium_post_chatgpt", "US", "2026-06", 2.4, "%", "Same premium also holding seniority mix constant within occupations. The authors note this may over-correct.", PY, segment="Control: seniority mix")]
    return o
